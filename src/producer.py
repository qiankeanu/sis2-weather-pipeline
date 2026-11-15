"""Часть 2 — Kundyz: Kafka Producer."""
import uuid
from datetime import datetime, timezone

from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from src.common import read_json, records_hash, save_json
from src.config import BROKER, DATA, METRICS, TOPIC, make_dirs
import json


def ensure_topic(broker=BROKER, topic=TOPIC):
    admin = KafkaAdminClient(bootstrap_servers=broker, request_timeout_ms=20000)
    try:
        try:
            # Одна partition сохраняет порядок записей в нашем небольшом проекте.
            admin.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
        except TopicAlreadyExistsError:
            pass
        description = admin.describe_topics([topic])[0]
        if len(description["partitions"]) != 1:
            raise ValueError("This educational pipeline expects a topic with one partition")
    finally:
        admin.close()


def publish_records(broker=BROKER, topic=TOPIC):
    make_dirs()
    records = read_json(DATA / "raw_data.json")
    source = read_json(METRICS / "collection.json")
    if records_hash(records) != source["dataset_sha256"] or len(records) < 200:
        raise ValueError("Raw data is changed or has fewer than 200 records")
    ensure_topic(broker, topic)
    run_id = uuid.uuid4().hex
    producer = KafkaProducer(
        bootstrap_servers=broker, acks="all", retries=3,
        request_timeout_ms=20000, max_block_ms=20000,
        value_serializer=lambda value: json.dumps(value, allow_nan=False).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8"),
    )
    published = 0
    try:
        for record in records:
            message = {"run_id": run_id, "record": record}
            # get() ждёт подтверждение брокера; считаем только подтверждённые сообщения.
            producer.send(topic, key=record["record_id"], value=message, partition=0).get(timeout=30)
            published += 1
        producer.flush(timeout=30)
    finally:
        producer.close(timeout=10)
    summary = {"run_id": run_id, "broker": broker, "topic": topic,
               "published": published, "dataset_sha256": records_hash(records),
               "finished_at_utc": datetime.now(timezone.utc).isoformat()}
    save_json(METRICS / "producer.json", summary)
    print(f"Kafka published: {published}; run_id={run_id}", flush=True)
    return summary


# CLI
if __name__ == "__main__":
    publish_records()
