import csv
import logging
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the CSV filename
CSV_FILENAME = "spam_detection_results.csv"

def write_spam_results(results: list[dict[str, Any]], filename: str = CSV_FILENAME) -> None:
    """Write spam detection results to a CSV file."""
    try:
        with Path(filename).open(mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["mail_id", "Pct_spam"])
            writer.writeheader()
            writer.writerows(results)

        logging.info("Spam detection results written to %s", filename)
    except Exception:
        logging.exception("Failed to write spam results to CSV")
