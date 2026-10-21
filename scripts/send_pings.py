"""Publish simulated sensor pings to Event Hubs (chapter 09).

    pip install azure-eventhub azure-identity
    python scripts/send_pings.py --namespace <EVENT_HUB_NAMESPACE> --count 500

Uses your Azure CLI login (DefaultAzureCredential); the Bicep template grants you
"Azure Event Hubs Data Owner" on the namespace.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime

from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import DefaultAzureCredential


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--namespace", required=True, help="Event Hubs namespace name (without suffix)")
    p.add_argument("--hub", default="sensor-pings")
    p.add_argument("--count", type=int, default=500)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()

    rng = random.Random(a.seed)
    producer = EventHubProducerClient(
        fully_qualified_namespace=f"{a.namespace}.servicebus.windows.net",
        eventhub_name=a.hub,
        credential=DefaultAzureCredential(),
    )
    with producer:
        batch = producer.create_batch()
        for i in range(a.count):
            ping = {
                "ping_id": f"E{i:09d}",
                "sensor_id": f"S{rng.randint(1, 40):03d}",
                "location_id": f"L{rng.randint(1, 10):03d}",
                "event_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "energy_reading": round(max(0.0, rng.gauss(50, 15)), 2),
            }
            try:
                batch.add(EventData(json.dumps(ping)))
            except ValueError:  # batch full
                producer.send_batch(batch)
                batch = producer.create_batch()
                batch.add(EventData(json.dumps(ping)))
        producer.send_batch(batch)
    print(f"sent {a.count} pings")


if __name__ == "__main__":
    main()
