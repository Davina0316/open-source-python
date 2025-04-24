import csv
import logging
from typing import List, Dict

def write_spam_results(results: List[Dict[str, float]], filename: str = "spam_results.csv") -> None:
    """Write spam detection results to a CSV file.

    Args:
        results: A list of dictionaries with keys 'mail_id' and 'Pct_spam'.
        filename: Output CSV filename (default: 'spam_results.csv').
    """
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["mail_id", "Pct_spam"])
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        logging.info("Spam detection results written to %s", filename)
    except Exception as e:
        logging.exception("Failed to write spam results to CSV: %s", e)
