"""Запуск всей цепочки. Настоящий Kafka должен быть запущен заранее."""
import argparse
import logging

from src.api_client import collect_data, load_snapshot
from src.producer import publish_records
from src.consumer import consume_records
from src.validator import run_validation
from src.cleaner import clean_data
from src.loader import run_loading
from src.analysis import run_analysis
from src.verification import verify_pipeline
from src.config import START_DATE, END_DATE


def main():
    parser = argparse.ArgumentParser(description="SIS 2: end-to-end weather pipeline")
    parser.add_argument("--use-snapshot", action="store_true", help="Use the preserved real API data")
    parser.add_argument("--start-date", default=START_DATE)
    parser.add_argument("--end-date", default=END_DATE)
    args = parser.parse_args()
    if args.use_snapshot:
        load_snapshot()
    else:
        collect_data(args.start_date, args.end_date)
    publish_records()
    consume_records()
    valid = run_validation()
    cleaned = clean_data(valid)
    run_loading(cleaned)
    run_analysis()
    verify_pipeline()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    try:
        main()
    except Exception:
        logging.exception("Pipeline stopped. Fix the reported stage before continuing.")
        raise
