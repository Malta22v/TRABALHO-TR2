from manifest import load_manifest
from downloader import download_segment
from metrics import initialize_csv, save_metric
from plot import plot_throughput
from buffer import BufferManager
from abr import choose_quality
from jitter import JitterCalculator


manifest = load_manifest()

SEGMENT_TIME = manifest["segment_duration_s"]

buffer_metrics = BufferManager()
jitter_calculator = JitterCalculator()

server = manifest["servers"][0]
base_url = server["url"]

representations = manifest["representations"]

initialize_csv()

print(manifest)

print("\n=== BAIXANDO SEGMENTOS ===\n")

# começa na menor qualidade
current_rep = representations[0]

last_throughput = None

for i in range(10):

    result = download_segment(
        base_url,
        current_rep["url_path"],
        current_rep["quality"]
    )

    buffer_metrics.att_buffer(
        SEGMENT_TIME,
        result["download_time_s"]
    )

    jitter_ms, jitter_ewma_ms = (
        jitter_calculator.update(
            result["download_time_s"]
        )
    )

    jitter_metrics = {
        "jitter_network_ms": jitter_ms,
        "jitter_ewma_ms": jitter_ewma_ms
    }

    save_metric(
        i + 1,
        result,
        buffer_metrics,
        jitter_metrics
    )

    print(f"Segmento {i + 1}")
    print(result)

    print(
        f"Jitter: {jitter_ms} ms | "
        f"EWMA: {jitter_ewma_ms} ms"
    )

    print()

    last_throughput = result["throughput_kbps"]

    current_rep = choose_quality(
        last_throughput,
        representations
    )

plot_throughput()