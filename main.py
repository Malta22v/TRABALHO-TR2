from manifest import load_manifest
from downloader import download_segment
from metrics import initialize_csv, save_metric
from plot import plot_throughput

manifest = load_manifest()

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

    save_metric(i + 1, result)

    print(f'Segmento {i+1}')
    print(result)
    print()

plot_throughput()