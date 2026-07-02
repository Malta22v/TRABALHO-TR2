import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def save_summary_metrics(df, output_dir, policy_name):
    os.makedirs(output_dir, exist_ok=True)

    quality_switches = (
        df["quality"].astype(str) != df["quality"].astype(str).shift(1)
    ).sum() - 1

    failover_mask = df["failover"].astype(str).str.lower().eq("true")
    avg_failover_time = df.loc[failover_mask, "failover_time_s"].mean()
    if pd.isna(avg_failover_time):
        avg_failover_time = 0.0

    if "failback" in df.columns:
        failback_mask = df["failback"].astype(str).str.lower().eq("true")
        avg_failback_time = df.loc[failback_mask, "failback_time_s"].mean()
        if pd.isna(avg_failback_time):
            avg_failback_time = 0.0
    else:
        failback_mask = pd.Series([False] * len(df))
        avg_failback_time = 0.0

    summary = {
        "abr_policy": policy_name,
        "segments": int(len(df)),
        "avg_throughput_kbps": round(df["throughput_kbps"].mean(), 2),
        "median_throughput_kbps": round(df["throughput_kbps"].median(), 2),
        "min_throughput_kbps": round(df["throughput_kbps"].min(), 2),
        "max_throughput_kbps": round(df["throughput_kbps"].max(), 2),
        "avg_buffer_s": round(df["buffer_time_s"].mean(), 2),
        "min_buffer_s": round(df["buffer_time_s"].min(), 2),
        "max_buffer_s": round(df["buffer_time_s"].max(), 2),
        "avg_download_time_s": round(df["download_time_s"].mean(), 3),
        "avg_elapsed_time_s": round(df["elapsed_time_s"].mean(), 3),
        "total_rebuffer_events": int(df["rebuffer_event"].max()),
        "failover_events": int(failover_mask.sum()),
        "avg_failover_time_s": round(avg_failover_time, 3),
        "failback_events": int(failback_mask.sum()),
        "avg_failback_time_s": round(avg_failback_time, 3),
        "quality_switches": int(max(quality_switches, 0)),
        "avg_bitrate_kbps": round(df["bitrate_kbps"].mean(), 2),
        "final_quality": str(df["quality"].iloc[-1]),
        "critical_buffer_segments": int((df["buffer_confidence"] == "CRITICAL").sum()),
        "very_low_buffer_segments": int((df["buffer_confidence"] == "VERY_LOW").sum()),
        "low_buffer_segments": int((df["buffer_confidence"] == "LOW").sum()),
        "good_buffer_segments": int((df["buffer_confidence"] == "GOOD").sum()),
    }

    pd.DataFrame([summary]).to_csv(
        os.path.join(output_dir, "summary.csv"),
        index=False
    )

    return summary


def plot_stream_metrics(
    throughput_window=5,
    quality_order=None,
    csv_file="logs/metrics.csv",
    output_dir="graphs",
    policy_name="UNKNOWN"
):
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_file)
    if df.empty:
        return None

    df["avg_throughput_kbps"] = (
        df["throughput_kbps"]
        .rolling(window=throughput_window, min_periods=1)
        .mean()
    )

    quality_labels = df["quality"].astype(str)
    if quality_order is None:
        quality_order = list(dict.fromkeys(quality_labels.tolist()))

    quality_codes = pd.Categorical(
        quality_labels,
        categories=quality_order,
        ordered=True
    ).codes

    plt.figure(figsize=(10, 5))
    plt.plot(df["segment"], df["buffer_time_s"])
    plt.xlabel("Segmento")
    plt.ylabel("Buffer (s)")
    plt.title("Tamanho do Buffer por Segmento")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "buffer.png"), bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(df["segment"], df["throughput_kbps"], label="Throughput")
    plt.plot(
        df["segment"],
        df["avg_throughput_kbps"],
        label=f"Media movel ({throughput_window})"
    )
    plt.xlabel("Segmento")
    plt.ylabel("Throughput (kbps)")
    plt.title("Throughput e Media Movel por Segmento")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "throughput.png"), bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.step(df["segment"], quality_codes, where="mid")
    plt.yticks(range(len(quality_order)), quality_order)
    plt.xlabel("Segmento")
    plt.ylabel("Qualidade selecionada")
    plt.title("Qualidade Selecionada por Segmento")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "quality.png"), bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(df["segment"], df["jitter_network_kbps"], label="Jitter instantaneo")
    plt.plot(df["segment"], df["jitter_ewma_kbps"], label="Jitter EWMA")
    plt.xlabel("Segmento")
    plt.ylabel("Jitter (kbps)")
    plt.title("Jitter por Segmento")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "jitter.png"), bbox_inches="tight")
    plt.close()

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle(f"Resumo da Politica {policy_name}")

    axes[0, 0].plot(df["segment"], df["throughput_kbps"], label="Throughput")
    axes[0, 0].plot(df["segment"], df["avg_throughput_kbps"], label="Media movel")
    axes[0, 0].set_title("Throughput")
    axes[0, 0].set_ylabel("kbps")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    axes[0, 1].plot(df["segment"], df["buffer_time_s"], color="tab:green")
    axes[0, 1].set_title("Buffer")
    axes[0, 1].set_ylabel("s")
    axes[0, 1].grid(True)

    axes[1, 0].step(df["segment"], quality_codes, where="mid", color="tab:orange")
    axes[1, 0].set_yticks(range(len(quality_order)))
    axes[1, 0].set_yticklabels(quality_order)
    axes[1, 0].set_title("Qualidade")
    axes[1, 0].grid(True)

    axes[1, 1].plot(df["segment"], df["jitter_ewma_kbps"], color="tab:red")
    axes[1, 1].set_title("Jitter EWMA")
    axes[1, 1].set_ylabel("kbps")
    axes[1, 1].grid(True)

    axes[2, 0].plot(df["segment"], df["download_time_s"], label="Download")
    axes[2, 0].plot(df["segment"], df["elapsed_time_s"], label="Efetivo")
    axes[2, 0].set_title("Tempo por segmento")
    axes[2, 0].set_ylabel("s")
    axes[2, 0].legend()
    axes[2, 0].grid(True)

    failover_segments = df[df["failover"].astype(str).str.lower().eq("true")]
    axes[2, 1].bar(
        failover_segments["segment"],
        failover_segments["failover_time_s"],
        color="tab:purple"
    )
    axes[2, 1].set_title("Eventos de failover")
    axes[2, 1].set_xlabel("Segmento")
    axes[2, 1].set_ylabel("s")
    axes[2, 1].grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "dashboard.png"), bbox_inches="tight")
    plt.close()

    return save_summary_metrics(df, output_dir, policy_name)


def plot_policy_comparison(summary_files, output_dir="graphs/comparison"):
    os.makedirs(output_dir, exist_ok=True)

    frames = [
        pd.read_csv(summary_file)
        for summary_file in summary_files
        if os.path.exists(summary_file)
    ]
    if not frames:
        return None

    df = pd.concat(frames, ignore_index=True)
    df.to_csv(os.path.join(output_dir, "comparison_summary.csv"), index=False)

    metrics = [
        ("avg_throughput_kbps", "Throughput medio (kbps)"),
        ("avg_buffer_s", "Buffer medio (s)"),
        ("quality_switches", "Trocas de qualidade"),
        ("total_rebuffer_events", "Eventos de rebuffer"),
        ("avg_bitrate_kbps", "Bitrate medio (kbps)"),
        ("failover_events", "Failovers"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()

    for ax, (column, title) in zip(axes, metrics):
        ax.bar(df["abr_policy"], df[column])
        ax.set_title(title)
        ax.grid(axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparison.png"), bbox_inches="tight")
    plt.close()

    return df
