from manifest import load_manifest
from downloader import download_segment
from metrics import initialize_csv, save_metric
from plot import plot_throughput
from buffer import BufferManager


manifest = load_manifest()

SEGMENT_TIME= 2.0
buffer_metrics = BufferManager()

server = manifest["servers"][0]
base_url = server["url"]

representations = manifest["representations"]

initialize_csv()

print("\n=== BAIXANDO SEGMENTOS ===\n")

for i in range(10):

    rep = representations[i % len(representations)]

    result = download_segment(
        base_url,
        rep["url_path"],
        rep["quality"]
    )

    buffer_metrics.att_buffer(SEGMENT_TIME, result['download_time_s'])# tempo do segmento é fixo por enquanto

    save_metric(i + 1, result, buffer_metrics)

    print(f'Segmento {i+1}')
    print(result)
    print()

plot_throughput()