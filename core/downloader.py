import requests
import time
from datetime import datetime


def download_segment(base_url, url_path, quality):

    full_url = f"{base_url}{url_path}"

    start_timestamp = datetime.now()
    start_time = time.perf_counter()

    response = requests.get(
        full_url,
        timeout=5
    )

    end_time = time.perf_counter()
    end_timestamp = datetime.now()

    response.raise_for_status()

    content = response.content

    bytes_received = len(content)

    download_time = end_time - start_time

    throughput_kbps = (
        bytes_received * 8
    ) / download_time / 1000

    return {
        "quality": quality,
        "bytes_received": bytes_received,
        "download_time_s": round(download_time, 3),
        "throughput_kbps": round(throughput_kbps, 2),
        "segment_start_timestamp": start_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "segment_end_timestamp": end_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "timestamp": end_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    }
