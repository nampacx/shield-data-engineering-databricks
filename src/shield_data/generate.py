"""Seeded generator for the synthetic S.H.I.E.L.D. field-intelligence dataset.

Standard library only, so it runs anywhere (laptop, Databricks, CI).

    python -m shield_data.generate --out ./data --incidents 10000 --seed 42 --dirty 0.05
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

CODENAMES = [
    "Falcon", "Raven", "Cobalt", "Nomad", "Sparrow", "Ember", "Onyx", "Vesper",
    "Mirage", "Tundra", "Harbor", "Zephyr", "Quartz", "Saber", "Willow", "Atlas",
]
CITIES = [
    ("New York", "US", 40.71, -74.01), ("Budapest", "HU", 47.50, 19.04),
    ("Sokovia", "SK", 48.15, 17.11), ("Wakanda Border", "KE", -1.29, 36.82),
    ("London", "GB", 51.51, -0.13), ("Tokyo", "JP", 35.68, 139.69),
    ("Cairo", "EG", 30.04, 31.24), ("Sydney", "AU", -33.87, 151.21),
    ("Berlin", "DE", 52.52, 13.40), ("Sao Paulo", "BR", -23.55, -46.63),
]
INCIDENT_TYPES = ["surveillance", "breach", "hydra_sighting", "enhanced_activity", "smuggling", "cyber"]
SEVERITIES = ["low", "medium", "high", "critical"]
THREAT_LEVELS = ["green", "yellow", "orange", "red"]
CLEARANCES = [1, 2, 3, 4, 5]

START = datetime(2025, 1, 1, tzinfo=UTC)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_locations() -> list[dict]:
    return [
        {"location_id": f"L{i:03d}", "city": c, "country": cc, "lat": lat, "lon": lon}
        for i, (c, cc, lat, lon) in enumerate(CITIES, start=1)
    ]


def make_agents(rng: random.Random, n: int = 50) -> list[dict]:
    return [
        {
            "agent_id": f"A{i:04d}",
            "codename": f"{rng.choice(CODENAMES)}-{rng.randint(10, 99)}",
            "clearance_level": rng.choice(CLEARANCES),
            "home_location_id": f"L{rng.randint(1, len(CITIES)):03d}",
            "active": rng.random() > 0.1,
        }
        for i in range(1, n + 1)
    ]


def make_incidents(
    rng: random.Random, agents: list[dict], n: int, dirty: float = 0.0, drift_after: float = 0.8
) -> list[dict]:
    """Event-style incident reports. `dirty` is the fraction of rows with defects.
    The last (1 - drift_after) share of rows gain an extra `source_channel` field (schema drift)."""
    rows: list[dict] = []
    for i in range(1, n + 1):
        ts = START + timedelta(seconds=rng.randint(0, 365 * 24 * 3600))
        row = {
            "incident_id": f"I{i:07d}",
            "reported_at": _iso(ts),
            "agent_id": rng.choice(agents)["agent_id"],
            "location_id": f"L{rng.randint(1, len(CITIES)):03d}",
            "incident_type": rng.choice(INCIDENT_TYPES),
            "severity": rng.choices(SEVERITIES, weights=[50, 30, 15, 5])[0],
            "casualties": max(0, int(rng.gauss(0.5, 1.5))),
            "summary": f"Report {i}: activity observed.",
        }
        if i > n * drift_after:
            row["source_channel"] = rng.choice(["radio", "satellite", "informant"])
        rows.append(row)

    # Inject defects. Each defect type is tagged so tests and chapters can find them.
    for row in rows:
        if rng.random() >= dirty:
            continue
        defect = rng.choice(["null_agent", "future_ts", "bad_severity", "negative_casualties", "bad_ts"])
        if defect == "null_agent":
            row["agent_id"] = None
        elif defect == "future_ts":
            row["reported_at"] = _iso(datetime.now(UTC) + timedelta(days=rng.randint(30, 400)))
        elif defect == "bad_severity":
            row["severity"] = "catastrophic"
        elif defect == "negative_casualties":
            row["casualties"] = -rng.randint(1, 5)
        elif defect == "bad_ts":
            row["reported_at"] = "not-a-timestamp"

    # Duplicates (late/replayed deliveries): re-emit some existing rows at the end.
    # Row order is kept (no shuffle) so schema drift only shows up in the last files.
    dups = [dict(r) for r in rng.sample(rows, k=int(len(rows) * dirty / 2))] if dirty else []
    rows.extend(dups)
    return rows


def make_sensor_pings(rng: random.Random, n: int, dirty: float = 0.0) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        ts = START + timedelta(seconds=i * 5)
        rows.append(
            {
                "ping_id": f"P{i:09d}",
                "sensor_id": f"S{rng.randint(1, 40):03d}",
                "location_id": f"L{rng.randint(1, len(CITIES)):03d}",
                "event_time": _iso(ts),
                "energy_reading": round(max(0.0, rng.gauss(50, 15)), 2),
            }
        )
    for row in rows:
        if rng.random() < dirty:
            row["energy_reading"] = rng.choice([-999.0, 1e6])  # sensor glitches
    return rows


def make_threat_assessments(rng: random.Random, n_subjects: int = 30, versions: int = 4) -> list[dict]:
    """Slowly changing: each subject gets several dated assessments (good for MERGE / SCD2)."""
    rows = []
    for s in range(1, n_subjects + 1):
        for v in range(versions):
            rows.append(
                {
                    "subject_id": f"T{s:04d}",
                    "assessed_on": (START + timedelta(days=v * 60 + rng.randint(0, 20))).date().isoformat(),
                    "threat_level": rng.choice(THREAT_LEVELS),
                    "analyst_id": f"A{rng.randint(1, 50):04d}",
                }
            )
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_jsonl(path: Path, rows: list[dict], files: int = 1) -> None:
    """Write JSON Lines, optionally split across several files to mimic arriving batches."""
    path.mkdir(parents=True, exist_ok=True)
    size = max(1, -(-len(rows) // files))
    for idx in range(files):
        chunk = rows[idx * size : (idx + 1) * size]
        if not chunk:
            break
        with (path / f"part-{idx:04d}.json").open("w", encoding="utf-8") as f:
            for r in chunk:
                f.write(json.dumps(r) + "\n")


def generate(out: Path, incidents: int = 10_000, pings: int = 20_000, seed: int = 42,
             dirty: float = 0.0, batches: int = 5) -> dict[str, int]:
    rng = random.Random(seed)
    locations = make_locations()
    agents = make_agents(rng)
    inc = make_incidents(rng, agents, incidents, dirty)
    png = make_sensor_pings(rng, pings, dirty)
    ta = make_threat_assessments(rng)

    _write_csv(out / "locations" / "locations.csv", locations)
    _write_csv(out / "agents" / "agents.csv", agents)
    _write_csv(out / "threat_assessments" / "threat_assessments.csv", ta)
    _write_jsonl(out / "incident_reports", inc, files=batches)
    _write_jsonl(out / "sensor_pings", png, files=batches)
    return {"locations": len(locations), "agents": len(agents), "incident_reports": len(inc),
            "sensor_pings": len(png), "threat_assessments": len(ta)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=Path("data"))
    p.add_argument("--incidents", type=int, default=10_000)
    p.add_argument("--pings", type=int, default=20_000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--dirty", type=float, default=0.0, help="fraction of rows with defects (0-1)")
    p.add_argument("--batches", type=int, default=5, help="number of JSON files per feed")
    a = p.parse_args()
    counts = generate(a.out, a.incidents, a.pings, a.seed, a.dirty, a.batches)
    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
