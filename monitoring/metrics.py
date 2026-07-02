import csv
import os


CSV_FILE = "logs/metrics.csv"


def initialize_csv(csv_file=CSV_FILE):

    os.makedirs("logs", exist_ok=True)
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    with open(csv_file, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "abr_policy",
            "segment",
            "timestamp",
            "segment_start_timestamp",
            "segment_end_timestamp",
            "server_id",
            "quality",
            "bitrate_kbps",
            "bytes_received",
            "download_time_s",
            "elapsed_time_s",
            "download_mode",
            "buffer_confidence",
            "buffer_time_s",
            "buffer_can_play",
            "rebuffer_event",
            "throughput_kbps",
            "jitter_network_kbps",
            "jitter_ewma_kbps",
            "failover",
            "failover_time_s",
            "failback",
            "failback_time_s"
        ])


def save_metric(
    abr_policy,
    segment,
    result,
    current_rep,
    buffer_metrics,
    jitter_metrics,
    server_id,
    download_mode,
    elapsed_time_s,
    failover=False,
    failover_time=0.0,
    failback=False,
    failback_time=0.0,
    csv_file=CSV_FILE
):

    with open(csv_file, mode="a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            abr_policy,
            segment,
            result["timestamp"],
            result["segment_start_timestamp"],
            result["segment_end_timestamp"],
            server_id,
            result["quality"],
            current_rep["bitrate_kbps"],
            result["bytes_received"],
            result["download_time_s"],
            round(elapsed_time_s, 3),
            download_mode,
            buffer_metrics.buffer_confidence(),
            buffer_metrics.buffer_level,
            buffer_metrics.buffer_can_play,
            buffer_metrics.rebuffer_event,
            result["throughput_kbps"],
            jitter_metrics["jitter_network_kbps"],
            jitter_metrics["jitter_ewma_kbps"],
            failover,
            round(failover_time, 3),
            failback,
            round(failback_time, 3)
        ])
