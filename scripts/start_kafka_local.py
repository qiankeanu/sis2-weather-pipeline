"""Запуск настоящего Kafka без Docker (macOS/Linux, Java 17+)."""
import argparse
import hashlib
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
VERSION = "3.9.1"
NAME = f"kafka_2.13-{VERSION}"


def download_kafka():
    RUNTIME.mkdir(exist_ok=True)
    home = RUNTIME / NAME
    if home.exists():
        return home
    archive = RUNTIME / f"{NAME}.tgz"
    url = f"https://archive.apache.org/dist/kafka/{VERSION}/{NAME}.tgz"
    print(f"Downloading {url}", flush=True)
    with requests.get(url, stream=True, timeout=(10, 180)) as response:
        response.raise_for_status()
        with archive.open("wb") as output:
            for chunk in response.iter_content(1024 * 1024):
                output.write(chunk)
    checksum = requests.get(url + ".sha512", timeout=30)
    checksum.raise_for_status()
    # Apache публикует SHA-512 группами по 8 символов с переносами строк.
    expected = re.sub(r"\s+", "", checksum.text.split(":", 1)[-1])
    actual = hashlib.sha512(archive.read_bytes()).hexdigest()
    if not re.fullmatch(r"[a-fA-F0-9]{128}", expected) or actual.lower() != expected.lower():
        raise ValueError("Apache Kafka archive checksum does not match")
    with tarfile.open(archive) as bundle:
        bundle.extractall(RUNTIME, filter="data")
    return home


def start(kafka_home=None):
    if not shutil.which("java"):
        raise RuntimeError("Install Java 17+ or use docker compose up -d --wait")
    home = Path(kafka_home).resolve() if kafka_home else download_kafka()
    RUNTIME.mkdir(exist_ok=True)
    logs = RUNTIME / "kafka-data"
    config = RUNTIME / "server.properties"
    config.write_text(f"""process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://127.0.0.1:9092,CONTROLLER://127.0.0.1:9093
advertised.listeners=PLAINTEXT://127.0.0.1:9092
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
inter.broker.listener.name=PLAINTEXT
log.dirs={logs}
num.partitions=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
group.initial.rebalance.delay.ms=0
""", encoding="utf-8")
    # Прямой вызов Java корректно работает даже с пробелами в "Data Collect".
    # Shell-скрипты Kafka разворачивают некоторые JVM-опции без кавычек.
    java = [shutil.which("java"), "-Xms256m", "-Xmx512m",
            f"-Dlog4j.configuration=file:{home / 'config/log4j.properties'}",
            f"-Dkafka.logs.dir={RUNTIME / 'broker-logs'}", "-cp", str(home / "libs" / "*")]
    if not (logs / "meta.properties").exists():
        cluster_id = subprocess.check_output(java + ["kafka.tools.StorageTool", "random-uuid"],
                                             text=True).strip()
        subprocess.run(java + ["kafka.tools.StorageTool", "format", "-t", cluster_id,
                                "-c", str(config)], check=True)
    print("Starting Kafka on localhost:9092. Keep this terminal open; Ctrl+C stops Kafka.", flush=True)
    subprocess.run(java + ["kafka.Kafka", str(config)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kafka-home", help="Optional existing official Kafka 3.9.1 directory")
    start(parser.parse_args().kafka_home)
