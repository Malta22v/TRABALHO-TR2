from core.manifest import load_manifest
from core.downloader import download_segment
from core.buffer import BufferManager
from core.jitter import JitterCalculator
from core.server_manager import ServerManager

from abr.abr import choose_quality
from abr.abr_buffer import choose_quality_buffer
from abr.abr_hybrid import choose_quality_hybrid

from monitoring.metrics import (
    initialize_csv,
    save_metric
)

from monitoring.plot import (
    plot_stream_metrics
)



from collections import deque
from time import sleep

import time

ABR_POLICY = "HYBRID"   # RATE ou BUFFER ou HYBRID

manifest = load_manifest()

SEGMENT_TIME = manifest["segment_duration_s"]

buffer_metrics = BufferManager()
jitter_calculator = JitterCalculator()

server_manager = ServerManager(
    manifest["servers"]
)

base_url = server_manager.get_base_url()

representations = manifest["representations"]

DEBUG_ABR = True
THROUGHPUT_WINDOW = 5

initialize_csv()

print(manifest)

print("\n=== BAIXANDO SEGMENTOS ===\n")

current_rep = representations[0]

str_download_mode = "burst"

throughput_history = deque(maxlen=THROUGHPUT_WINDOW)

i = 0

try:

    while True:

        failover_event = False
        failover_time = 0.0

        try:

            result = download_segment(
                base_url,
                current_rep["url_path"],
                current_rep["quality"]
            )

        except Exception:

            print("\nServidor falhou!\n")

            start = time.perf_counter()

            new_server = server_manager.failover()

            failover_time = (
                time.perf_counter() - start
            )

            failover_event = True

            if new_server is None:

                print("Nenhum servidor disponível.")

                break

            base_url = new_server["url"]

            print(
                f"Servidor ativo: "
                f"{server_manager.get_server_id()}"
            )

            result = download_segment(
                base_url,
                current_rep["url_path"],
                current_rep["quality"]
            )

            print(
                f"Failover concluído em "
                f"{failover_time:.3f}s"
            )

        download_time_s = result["download_time_s"]

        elapsed_time_s = download_time_s

        if str_download_mode == "on/off":

            wait_s = max(
                0.0,
                SEGMENT_TIME - download_time_s
            )

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
            jitter_metrics,
            server_manager.get_server_id(),
            failover_event,
            failover_time
        )

        print("\n" + "=" * 60)

        print(
            f"SEGMENTO {i + 1} | "
            f"POLÍTICA: {ABR_POLICY}"
        )

        print("=" * 60)

        print(
            f"Servidor ..........: "
            f"{server_manager.get_server_id()}"
        )

        print(
            f"Qualidade .........: "
            f"{result['quality']}"
        )

        print(
            f"Bytes recebidos ...: "
            f"{result['bytes_received']}"
        )

        print(
            f"Download ..........: "
            f"{result['download_time_s']} s"
        )

        print(
            f"Throughput ........: "
            f"{result['throughput_kbps']} kbps"
        )

        print(
            f"Jitter ............: "
            f"{jitter_ms} ms"
        )

        print(
            f"Jitter EWMA .......: "
            f"{jitter_ewma_ms} ms"
        )

        print(
            f"Buffer ............: "
            f"{buffer_metrics.buffer_level:.2f} s"
        )

        print(
            f"Modo Download .....: "
            f"{str_download_mode}"
        )

        print()

        throughput_history.append(
            result["throughput_kbps"]
        )

        avg_throughput = (
            sum(throughput_history)
            / len(throughput_history)
        )

        str_download_mode = (
            buffer_metrics.download_mode()
        )

        buffer_confidence = (
            buffer_metrics.buffer_confidence()
        )

        if ABR_POLICY == "RATE":

            current_rep = choose_quality(
                avg_throughput,
                representations,
                buffer_confidence,
                debug=DEBUG_ABR
            )

        if ABR_POLICY == "BUFFER":

            current_rep = choose_quality_buffer(
                buffer_metrics.buffer_level,
                representations
            )

        if ABR_POLICY == "HYBRID":

            current_rep = choose_quality_hybrid(
                avg_throughput_kbps=avg_throughput,
                representations=representations,
                buffer_level=buffer_metrics.buffer_level,
                jitter_ewma_ms=jitter_ewma_ms,
                debug=DEBUG_ABR
            )

        i += 1

except KeyboardInterrupt:

    print(
        "\nStreaming interrompido "
        "pelo usuário."
    )

finally:

    plot_stream_metrics(
        throughput_window=THROUGHPUT_WINDOW,
        quality_order=[
            rep["quality"]
            for rep in representations
        ]
    )