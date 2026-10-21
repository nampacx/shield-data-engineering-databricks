import random

import pytest

from shield_data.generate import make_agents, make_incidents
from shield_data.quality import INCIDENT_RULES, failed_rules


def _rows(dirty):
    rng = random.Random(11)
    return make_incidents(rng, make_agents(rng), 1500, dirty=dirty)


def test_clean_rows_pass_all_rules():
    assert all(failed_rules(r) == [] for r in _rows(0.0))


def test_each_injected_defect_is_caught():
    seen = {name for r in _rows(0.2) for name in failed_rules(r)}
    assert seen == set(INCIDENT_RULES)


def test_python_mirror_matches_spark():
    pytest.importorskip("pyspark")
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F

    spark = SparkSession.builder.master("local[1]").appName("rules").getOrCreate()
    rows = _rows(0.2)[:300]
    df = spark.createDataFrame(
        [(r["agent_id"], r["reported_at"], r["severity"], r["casualties"]) for r in rows],
        "agent_id string, reported_at string, severity string, casualties int",
    ).withColumn("reported_ts", F.expr("try_to_timestamp(reported_at, \"yyyy-MM-dd'T'HH:mm:ss'Z'\")"))
    for name, expr in INCIDENT_RULES.items():
        spark_fail = df.filter(~F.expr(expr)).count()
        py_fail = sum(name in failed_rules(r) for r in rows)
        assert spark_fail == py_fail, name
