"""Data quality rules for incident reports.

Each rule is a (name, SQL expression) pair. The SQL expression must be TRUE for a valid row.
The notebooks and the declarative pipeline evaluate these with Spark; `failed_rules` is a
pure-Python mirror used for fast unit tests (and checked against Spark when pyspark is present).
"""

from __future__ import annotations

from datetime import UTC, datetime

SEVERITIES = ("low", "medium", "high", "critical")

# `reported_ts` is the parsed timestamp column (try_to_timestamp(reported_at)).
INCIDENT_RULES: dict[str, str] = {
    "has_agent": "agent_id IS NOT NULL",
    "valid_timestamp": "reported_ts IS NOT NULL AND reported_ts <= current_timestamp()",
    "valid_severity": "severity IN ('low', 'medium', 'high', 'critical')",
    "non_negative_casualties": "casualties IS NOT NULL AND casualties >= 0",
}


def _parse(ts: str | None) -> datetime | None:
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except (TypeError, ValueError):
        return None


def failed_rules(row: dict) -> list[str]:
    """Names of the rules a raw incident row violates (empty list means valid)."""
    failed = []
    if row.get("agent_id") is None:
        failed.append("has_agent")
    ts = _parse(row.get("reported_at"))
    if ts is None or ts > datetime.now(UTC):
        failed.append("valid_timestamp")
    if row.get("severity") not in SEVERITIES:
        failed.append("valid_severity")
    c = row.get("casualties")
    if c is None or c < 0:
        failed.append("non_negative_casualties")
    return failed
