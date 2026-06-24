import csv
import os


CSV_FILE = "logs/metrics.csv"

_failover_total = 0


def initialize_csv():

    global _failover_total
    _failover_total = 0

    os.makedirs("logs", exist_ok=True)

    with open(CSV_FILE, mode="w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "segment",
            "timestamp",
            "server_id",
            "quality",
            "bytes_received",
            "download_time_s",
            "buffer_level_s",
            "buffer_can_play",
            "rebuffer_event",
            "stall_duration_s",
            "throughput_kbps",
            "jitter_network_kbps",
            "jitter_ewma_kbps",
            "jitter_intra_ms",
            "failover",
            "failover_time_s",
            "failover_total"
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

    global _failover_total

    if failover:
        _failover_total += 1

    # stall_duration_s: tempo que o buffer ficou em 0 durante o download.
    # Ocorre quando download_time_s > buffer_level_s anterior + segment_duration.
    # Como o BufferManager já clampeia em 0, aproximamos pelo tempo de failover
    # (que é o único atraso extra mensurável fora do download normal).
    stall_duration_s = round(failover_time, 3) if failover else 0.0

    with open(CSV_FILE, mode="a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            segment,
            result["timestamp"],
            server_id,
            result["quality"],
            result["bytes_received"],
            result["download_time_s"],
            round(buffer_metrics.buffer_level, 3),
            1 if buffer_metrics.buffer_can_play else 0,
            buffer_metrics.rebuffer_event,
            stall_duration_s,
            result["throughput_kbps"],
            jitter_metrics["jitter_network_kbps"],
            jitter_metrics["jitter_ewma_kbps"],
            jitter_metrics.get("jitter_intra_ms", 0.0),
            1 if failover else 0,
            round(failover_time, 3),
            _failover_total
        ])