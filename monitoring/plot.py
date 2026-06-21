import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_stream_metrics(
    throughput_window=5,
    quality_order=None
):

    os.makedirs("graphs", exist_ok=True)

    df = pd.read_csv("logs/metrics.csv")

    if df.empty:
        return

    df["avg_throughput_kbps"] = (
        df["throughput_kbps"]
        .rolling(
            window=throughput_window,
            min_periods=1
        )
        .mean()
    )

    
    # BUFFER

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["segment"],
        df["buffer_time_s"]
    )

    plt.xlabel("Segmento")
    plt.ylabel("Buffer (s)")
    plt.title("Tamanho do Buffer por Segmento")

    plt.grid(True)

    plt.savefig(
        "graphs/buffer.png",
        bbox_inches="tight"
    )

    plt.close()

    
    # THROUGHPUT
    

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["segment"],
        df["throughput_kbps"],
        label="Throughput"
    )

    plt.plot(
        df["segment"],
        df["avg_throughput_kbps"],
        label=f"Média móvel ({throughput_window})"
    )

    plt.xlabel("Segmento")
    plt.ylabel("Throughput (kbps)")
    plt.title(
        "Throughput e Média Móvel por Segmento"
    )

    plt.legend()

    plt.grid(True)

    plt.savefig(
        "graphs/throughput.png",
        bbox_inches="tight"
    )

    plt.close()

    
    # QUALIDADE
    

    plt.figure(figsize=(10, 5))

    quality_labels = (
        df["quality"]
        .astype(str)
    )

    if quality_order is None:

        quality_order = list(
            dict.fromkeys(
                quality_labels.tolist()
            )
        )

    quality_codes = pd.Categorical(
        quality_labels,
        categories=quality_order,
        ordered=True
    ).codes

    plt.step(
        df["segment"],
        quality_codes,
        where="mid"
    )

    plt.yticks(
        range(len(quality_order)),
        quality_order
    )

    plt.xlabel("Segmento")
    plt.ylabel("Qualidade selecionada")

    plt.title(
        "Qualidade Selecionada por Segmento"
    )

    plt.grid(True)

    plt.savefig(
        "graphs/quality.png",
        bbox_inches="tight"
    )

    plt.close()

    
    # JITTER
    

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["segment"],
        df["jitter_network_ms"],
        label="Jitter Instantâneo"
    )

    plt.plot(
        df["segment"],
        df["jitter_ewma_ms"],
        label="Jitter EWMA"
    )

    plt.xlabel("Segmento")
    plt.ylabel("Jitter (ms)")

    plt.title(
        "Jitter por Segmento"
    )

    plt.legend()

    plt.grid(True)

    plt.savefig(
        "graphs/jitter.png",
        bbox_inches="tight"
    )

    plt.close()