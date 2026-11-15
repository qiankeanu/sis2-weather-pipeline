"""Часть 2 — Kundyz: Kafka Consumer."""
import json
import time

import pandas as pd
from kafka import KafkaConsumer, TopicPartition

from src.common import read_json, records_hash, save_json
from src.config import DATA, METRICS


def consume_records(timeout_seconds=120):
    manifest = read_json(METRICS / "producer.json")
    expected = manifest["published"]
    consumer = KafkaConsumer(bootstrap_servers=manifest["broker"], group_id=None,
                             enable_auto_commit=False, request_timeout_ms=30000,
                             fetch_max_bytes=4 * 1024 * 1024,
                             max_partition_fetch_bytes=2 * 1024 * 1024,
                             # Ответ включает служебные байты: лимит должен быть больше fetch.
                             receive_message_max_bytes=8 * 1024 * 1024)
    records, offsets = [], []
    skipped_old = 0
    deadline = time.monotonic() + timeout_seconds
    try:
        consumer.assign([TopicPartition(manifest["topic"], 0)])
        consumer.seek_to_beginning()
        while len(records) < expected:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Kafka received {len(records)} of {expected} records")
            batch = consumer.poll(timeout_ms=1000, max_records=500)
            for messages in batch.values():
                for message in messages:
                    try:
                        value = json.loads(message.value.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        raise ValueError(f"Invalid JSON at offset {message.offset}") from error
                    if value.get("run_id") != manifest["run_id"]:
                        skipped_old += 1
                        continue
                    if not isinstance(value.get("record"), dict):
                        raise ValueError(f"Missing record at offset {message.offset}")
                    records.append(value["record"])
                    offsets.append(message.offset)
    finally:
        consumer.close()
    # Проверяем не только количество, но и точное содержимое и порядок записей.
    if len(records) != expected or records_hash(records) != manifest["dataset_sha256"]:
        raise ValueError("Published and consumed datasets are different")
    save_json(DATA / "consumed_data.json", records)
    pd.DataFrame(records).to_csv(DATA / "consumed_data.csv", index=False)
    summary = {"run_id": manifest["run_id"], "consumed": len(records),
               "dataset_sha256": records_hash(records), "topic": manifest["topic"],
               "partition": 0, "first_offset": min(offsets), "last_offset": max(offsets),
               "skipped_previous_run_messages": skipped_old,
               "termination": "expected count reached; complete dataset hash verified"}
    save_json(METRICS / "consumer.json", summary)
    print(f"Kafka consumed: {len(records)}", flush=True)
    return pd.DataFrame(records)


# CLI
if __name__ == "__main__":
    consume_records()
