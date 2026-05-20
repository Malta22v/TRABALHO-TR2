import csv
import os


CSV_FILE = "logs/metrics.csv"


def initialize_csv():

    os.makedirs("logs", exist_ok=True)

    with open(CSV_FILE, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "segment",
            "quality",
            "bytes_received",
            "download_time_s",
            "throughput_kbps"
        ])


def save_metric(segment, result):

    with open(CSV_FILE, mode="a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            segment,
            result["quality"],
            result["bytes_received"],
            result["download_time_s"],
            result["throughput_kbps"]
        ])