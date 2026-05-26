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
            "buffer_time_s",
            "buffer_can_play",
            "rebuffer_event",
            "throughput_kbps"
        ])


def save_metric(segment, result, buffer_metrics: object):

    with open(CSV_FILE, mode="a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            segment,
            result["quality"],
            result["bytes_received"],
            result["download_time_s"],
            buffer_metrics.buffer_level,
            buffer_metrics.buffer_can_play,
            buffer_metrics.rebuffer_event,
            result["buffer_can_play"],
            result["rebuffer_event"],
            result["throughput_kbps"],

        ])