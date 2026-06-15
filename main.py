from manifest import load_manifest
from downloader import download_segment
from metrics import initialize_csv, save_metric
from plot import plot_stream_metrics
from buffer import BufferManager
from abr import choose_quality
from jitter import JitterCalculator
from collections import deque
from time import sleep

manifest = load_manifest()

SEGMENT_TIME = manifest["segment_duration_s"]

buffer_metrics = BufferManager()
jitter_calculator = JitterCalculator()

server = manifest["servers"][0]
base_url = server["url"]

representations = manifest["representations"]
DEBUG_ABR = True
THROUGHPUT_WINDOW = 5

initialize_csv()

print(manifest)

print("\n=== BAIXANDO SEGMENTOS ===\n")

# começa na menor qualidade
current_rep = representations[0]
str_download_mode = 'burst'
last_throughput = None
throughput_history = deque(maxlen=THROUGHPUT_WINDOW)
i = 0

try:
    while True:
        result = download_segment(
            base_url,
            current_rep["url_path"],
            current_rep["quality"]
        )

        download_time_s = result["download_time_s"]
        elapsed_time_s = download_time_s

        if str_download_mode == 'on/off':
            wait_s = max(0.0, SEGMENT_TIME - download_time_s)
            sleep(wait_s)
            elapsed_time_s += wait_s

        buffer_metrics.update_buffer(
            SEGMENT_TIME,
            elapsed_time_s
        )

        jitter_ms, jitter_ewma_ms = (
            jitter_calculator.update(
                download_time_s
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
        print(f"Modo de download: {str_download_mode}")
        print(f"Buffer: {buffer_metrics.buffer_level:.2f} s")
        print()

        last_throughput = result["throughput_kbps"]
        throughput_history.append(last_throughput)
        avg_throughput = sum(throughput_history) / len(throughput_history)
        str_download_mode = buffer_metrics.download_mode()
        buffer_confidence = buffer_metrics.buffer_confidence()
        
        current_rep = choose_quality(
            avg_throughput,
            representations,
            buffer_confidence,
            debug=DEBUG_ABR
        )

        i += 1

except KeyboardInterrupt:
    print("\nStreaming interrompido pelo usuário.")

finally:
    plot_stream_metrics(
        throughput_window=THROUGHPUT_WINDOW,
        quality_order=[rep["quality"] for rep in representations]
    )