import csv
import os


CSV_FILE = "logs/metrics.csv"


def initialize_csv():

    os.makedirs("logs", exist_ok=True)

    with open(CSV_FILE, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "segment",
            "server_id",
            "quality",
            "bytes_received",
            "download_time_s",
            "buffer_time_s",
            "buffer_can_play",
            "rebuffer_event",
            "throughput_kbps",
            "jitter_network_ms",
            "jitter_ewma_ms",
            "failover",
            "failover_time_s"
        ])


def save_metric(
    segment,
    result,
    buffer_metrics,
    jitter_metrics,
    server_id,
    failover=False,
    failover_time=0.0
):

    with open(CSV_FILE, mode="a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            segment,
            server_id,
            result["quality"],
            result["bytes_received"],
            result["download_time_s"],
            buffer_metrics.buffer_level,
            buffer_metrics.buffer_can_play,
            buffer_metrics.rebuffer_event,
            result["throughput_kbps"],
            jitter_metrics["jitter_network_ms"],
            jitter_metrics["jitter_ewma_ms"],
            failover,
            round(failover_time, 3)
        ])