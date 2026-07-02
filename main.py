import argparse
import os
import statistics
import time
from collections import deque
from datetime import datetime
from time import sleep

from abr.abr import choose_quality
from abr.abr_buffer import choose_quality_buffer
from abr.abr_hybrid import choose_quality_hybrid, average_throughput_for_hybrid
from core.buffer import BufferManager
from core.downloader import download_segment
from core.jitter import JitterCalculator
from core.manifest import load_manifest
from core.server_manager import ServerManager
from monitoring.metrics import initialize_csv, save_metric
from monitoring.plot import plot_policy_comparison, plot_stream_metrics


POLICY_ALIASES = {
    "1": "RATE",
    "RATE": "RATE",
    "2": "BUFFER",
    "BUFFER": "BUFFER",
    "3": "HYBRID",
    "HYBRID": "HYBRID",
}

POLICY_LABELS = {
    "RATE": "1_RATE",
    "BUFFER": "2_BUFFER",
    "HYBRID": "3_HYBRID",
}

THROUGHPUT_WINDOW = 5
DEBUG_ABR = True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cliente ABR com politicas comparaveis."
    )
    parser.add_argument(
        "--policy",
        choices=["1", "2", "3", "RATE", "BUFFER", "HYBRID", "all"],
        help="Politica ABR: 1/RATE, 2/BUFFER, 3/HYBRID ou all."
    )
    parser.add_argument(
        "--max-segments",
        type=int,
        default=30,
        help="Quantidade de segmentos por politica. Use 0 para rodar continuamente."
    )
    parser.add_argument(
        "--failover-test",
        action="store_true",
        help="Simula uma falha para validar failover."
    )
    parser.add_argument(
        "--failover-after",
        type=int,
        default=20,
        help="Segmento em que o teste de failover deve ocorrer."
    )
    parser.add_argument(
        "--extra-download-delay",
        type=float,
        default=0.0,
        help="Atraso artificial em segundos para estressar o buffer."
    )
    parser.add_argument(
        "--failback-check-interval",
        type=float,
        default=10.0,
        help=(
            "Intervalo em segundos para tentar voltar ao servidor primario "
            "apos um failover. Use 0 para desativar."
        )
    )
    return parser.parse_args()


def choose_policy_from_input():
    print("\nEscolha a politica ABR:")
    print("1 - RATE   (baseada em throughput)")
    print("2 - BUFFER (baseada em nivel de buffer)")
    print("3 - HYBRID (throughput + buffer + jitter)")

    while True:
        choice = input("Politica [1/2/3]: ").strip().upper()
        if choice in POLICY_ALIASES:
            return POLICY_ALIASES[choice]
        print("Opcao invalida. Use 1, 2 ou 3.")


def normalize_policy(policy):
    if policy is None:
        return choose_policy_from_input()
    if policy == "all":
        return "all"
    return POLICY_ALIASES[policy.upper()]


def build_run_paths(policy):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{POLICY_LABELS[policy]}_{timestamp}"
    csv_file = os.path.join("logs", f"metrics_{run_name}.csv")
    graph_dir = os.path.join("graphs", run_name)
    return run_name, csv_file, graph_dir


def select_next_representation(
    policy,
    representations,
    throughput_history,
    buffer_metrics,
    jitter_ewma_kbps
):
    avg_throughput = statistics.mean(throughput_history)
    buffer_confidence = buffer_metrics.buffer_confidence()

    if policy == "RATE":
        return choose_quality(
            avg_throughput,
            representations,
            buffer_confidence,
            debug=DEBUG_ABR
        )

    if policy == "BUFFER":
        return choose_quality_buffer(
            buffer_metrics.buffer_level,
            representations
        )

    avg_throughput = average_throughput_for_hybrid(
        throughput_history,
        buffer_metrics.buffer_level
    )
    return choose_quality_hybrid(
        avg_throughput_kbps=avg_throughput,
        representations=representations,
        buffer_level=buffer_metrics.buffer_level,
        jitter_ewma_kbps=jitter_ewma_kbps,
        debug=DEBUG_ABR
    )


def run_policy(
    policy,
    manifest,
    max_segments,
    enable_failover_test,
    failover_after_segments,
    extra_download_delay_s,
    failback_check_interval_s
):
    run_name, csv_file, graph_dir = build_run_paths(policy)
    initialize_csv(csv_file)

    segment_time = manifest["segment_duration_s"]
    representations = manifest["representations"]

    buffer_metrics = BufferManager()
    jitter_calculator = JitterCalculator()
    server_manager = ServerManager(manifest["servers"])
    base_url = server_manager.get_base_url()

    current_rep = representations[0]
    download_mode = "burst"
    throughput_history = deque(maxlen=THROUGHPUT_WINDOW)
    failover_test_triggered = False
    last_failback_check = time.perf_counter()

    print(f"\n=== POLITICA {POLICY_LABELS[policy]} ===")
    print(f"CSV: {csv_file}")
    print(f"Graficos: {graph_dir}\n")

    i = 0
    try:
        while True:
            failover_event = False
            failover_time = 0.0
            failback_event = False
            failback_time = 0.0
            control_plane_time_s = 0.0

            if (
                failback_check_interval_s > 0
                and not server_manager.is_on_primary()
            ):
                now = time.perf_counter()

                if now - last_failback_check >= failback_check_interval_s:
                    last_failback_check = now
                    start = time.perf_counter()
                    primary_server = server_manager.failback_to_primary()
                    failback_time = time.perf_counter() - start
                    control_plane_time_s += failback_time

                    if primary_server is not None:
                        base_url = primary_server["url"]
                        failback_event = True
                        print(
                            f"Failback concluido em "
                            f"{failback_time:.3f}s"
                        )

            try:
                if (
                    enable_failover_test
                    and not failover_test_triggered
                    and i >= failover_after_segments
                ):
                    failover_test_triggered = True
                    raise RuntimeError("Falha simulada para teste de failover")

                result = download_segment(
                    base_url,
                    current_rep["url_path"],
                    current_rep["quality"]
                )

            except Exception:
                print("\nServidor falhou!\n")
                start = time.perf_counter()
                new_server = server_manager.failover()
                failover_time = time.perf_counter() - start
                failover_event = True

                if new_server is None:
                    print("Nenhum servidor disponivel.")
                    break

                base_url = new_server["url"]
                print(f"Servidor ativo: {server_manager.get_server_id()}")

                result = download_segment(
                    base_url,
                    current_rep["url_path"],
                    current_rep["quality"]
                )
                print(f"Failover concluido em {failover_time:.3f}s")

            download_time_s = result["download_time_s"]
            elapsed_time_s = (
                download_time_s
                + failover_time
                + control_plane_time_s
            )

            if extra_download_delay_s > 0:
                elapsed_time_s += extra_download_delay_s

            if download_mode == "on/off":
                wait_s = max(0.0, segment_time - download_time_s)
                sleep(wait_s)
                elapsed_time_s += wait_s

            buffer_metrics.update_buffer(segment_time, elapsed_time_s)
            jitter_kbps, jitter_ewma_kbps = jitter_calculator.update(
                result["throughput_kbps"]
            )
            jitter_metrics = {
                "jitter_network_kbps": jitter_kbps,
                "jitter_ewma_kbps": jitter_ewma_kbps
            }

            save_metric(
                policy,
                i + 1,
                result,
                current_rep,
                buffer_metrics,
                jitter_metrics,
                server_manager.get_server_id(),
                download_mode,
                elapsed_time_s,
                failover_event,
                failover_time,
                failback_event,
                failback_time,
                csv_file
            )

            print("\n" + "=" * 60)
            print(f"SEGMENTO {i + 1} | POLITICA: {policy}")
            print("=" * 60)
            print(f"Timestamp Wireshark: {result['timestamp']}")
            print(f"Inicio download ...: {result['segment_start_timestamp']}")
            print(f"Fim download ......: {result['segment_end_timestamp']}")
            print(f"Servidor ..........: {server_manager.get_server_id()}")
            print(f"Failover ..........: {failover_event}")
            print(f"Failback ..........: {failback_event}")
            print(f"Qualidade .........: {result['quality']}")
            print(f"Bitrate ...........: {current_rep['bitrate_kbps']} kbps")
            print(f"Bytes recebidos ...: {result['bytes_received']}")
            print(f"Download ..........: {result['download_time_s']} s")
            print(f"Tempo efetivo .....: {elapsed_time_s:.3f} s")
            print(f"Throughput ........: {result['throughput_kbps']} kbps")
            print(f"Jitter ............: {jitter_kbps} kbps")
            print(f"Jitter EWMA .......: {jitter_ewma_kbps} kbps")
            print(f"Buffer ............: {buffer_metrics.buffer_level:.2f} s")
            print(f"Confianca buffer ..: {buffer_metrics.buffer_confidence()}")
            print(f"Modo Download .....: {download_mode}\n")

            throughput_history.append(result["throughput_kbps"])
            download_mode = buffer_metrics.download_mode()
            current_rep = select_next_representation(
                policy,
                representations,
                throughput_history,
                buffer_metrics,
                jitter_ewma_kbps
            )

            i += 1
            if max_segments and i >= max_segments:
                print(f"\nTeste encerrado apos {max_segments} segmentos.")
                break

    except KeyboardInterrupt:
        print("\nStreaming interrompido pelo usuario.")

    summary = plot_stream_metrics(
        throughput_window=THROUGHPUT_WINDOW,
        quality_order=[rep["quality"] for rep in representations],
        csv_file=csv_file,
        output_dir=graph_dir,
        policy_name=POLICY_LABELS[policy]
    )

    return {
        "policy": policy,
        "run_name": run_name,
        "csv_file": csv_file,
        "graph_dir": graph_dir,
        "summary_file": os.path.join(graph_dir, "summary.csv"),
        "summary": summary,
    }


def main():
    args = parse_args()
    selected_policy = normalize_policy(args.policy)
    policies = ["RATE", "BUFFER", "HYBRID"] if selected_policy == "all" else [selected_policy]

    manifest = load_manifest()
    print(manifest)
    print("\n=== BAIXANDO SEGMENTOS ===\n")

    runs = []
    for policy in policies:
        runs.append(
            run_policy(
                policy=policy,
                manifest=manifest,
                max_segments=args.max_segments,
                enable_failover_test=args.failover_test,
                failover_after_segments=args.failover_after,
                extra_download_delay_s=args.extra_download_delay,
                failback_check_interval_s=args.failback_check_interval
            )
        )

    if len(runs) > 1:
        comparison_dir = os.path.join(
            "graphs",
            f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        plot_policy_comparison(
            [run["summary_file"] for run in runs],
            output_dir=comparison_dir
        )
        print(f"\nComparacao salva em: {comparison_dir}")

    print("\nArquivos gerados:")
    for run in runs:
        print(f"- {run['policy']}: {run['csv_file']} | {run['graph_dir']}")


if __name__ == "__main__":
    main()
