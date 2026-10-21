import json
import random

from shield_data.generate import generate, make_agents, make_incidents


def _read_incidents(path):
    rows = []
    for f in sorted((path / "incident_reports").glob("*.json")):
        rows += [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines()]
    return rows


def test_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    generate(a, incidents=200, pings=200, seed=7, dirty=0.1)
    generate(b, incidents=200, pings=200, seed=7, dirty=0.1)
    assert _read_incidents(a) == _read_incidents(b)


def test_clean_data_has_no_defects(tmp_path):
    generate(tmp_path, incidents=500, pings=100, seed=1, dirty=0.0)
    rows = _read_incidents(tmp_path)
    assert len(rows) == 500
    assert len({r["incident_id"] for r in rows}) == 500
    assert all(r["agent_id"] for r in rows)
    assert all(r["casualties"] >= 0 for r in rows)
    assert all(r["severity"] in {"low", "medium", "high", "critical"} for r in rows)


def test_dirty_data_has_duplicates_and_defects():
    rng = random.Random(3)
    rows = make_incidents(rng, make_agents(rng), 2000, dirty=0.1)
    ids = [r["incident_id"] for r in rows]
    assert len(ids) > len(set(ids))  # duplicates
    assert any(r["agent_id"] is None for r in rows)
    assert any(r["severity"] == "catastrophic" for r in rows)


def test_schema_drift_appears_late():
    rng = random.Random(5)
    rows = make_incidents(rng, make_agents(rng), 1000, dirty=0.0, drift_after=0.8)
    with_field = [r for r in rows if "source_channel" in r]
    assert 0 < len(with_field) < len(rows)
    assert all(int(r["incident_id"][1:]) > 800 for r in with_field)
