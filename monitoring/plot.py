import matplotlib
matplotlib.use("Agg")

import os
import pandas as pd
import matplotlib.pyplot as plt


GRAPHS_DIR = "graphs"


def _failover_segments(df):
    """Retorna lista de segmentos onde houve failover."""
    return df.loc[df["failover"] == 1, "segment"].tolist()


def _draw_failover_lines(ax, failover_segs, label=True):
    """Desenha linhas verticais vermelhas em cada failover."""
    for idx, seg in enumerate(failover_segs):
        ax.axvline(
            x=seg,
            color="red",
            linestyle="--",
            linewidth=1.2,
            label="Failover" if (label and idx == 0) else None
        )


def plot_stream_metrics(
    throughput_window=5,
    quality_order=None,
    csv_path="logs/metrics.csv",
    suffix=""
):
    """
    Gera os 4 gráficos individuais a partir de um CSV de sessão.

    suffix: string opcional para diferenciar arquivos (ex: "_RATE", "_HYBRID").
    """

    os.makedirs(GRAPHS_DIR, exist_ok=True)

    df = pd.read_csv(csv_path)

    if df.empty:
        return

    failover_segs = _failover_segments(df)

    df["avg_throughput_kbps"] = (
        df["throughput_kbps"]
        .rolling(window=throughput_window, min_periods=1)
        .mean()
    )

    rebuffer_df = df[df["rebuffer_event"] > df["rebuffer_event"].shift(1).fillna(0)]

    # ------------------------------------------------------------------
    # BUFFER
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df["segment"], df["buffer_level_s"], label="Buffer")

    # Marca eventos de rebuffering
    if not rebuffer_df.empty:
        ax.scatter(
            rebuffer_df["segment"],
            rebuffer_df["buffer_level_s"],
            color="orange",
            zorder=5,
            label="Rebuffering"
        )

    _draw_failover_lines(ax, failover_segs)

    ax.set_xlabel("Segmento")
    ax.set_ylabel("Buffer (s)")
    ax.set_title("Nível do Buffer por Segmento")
    ax.legend()
    ax.grid(True)

    fig.savefig(
        f"{GRAPHS_DIR}/buffer{suffix}.png",
        bbox_inches="tight"
    )
    plt.close(fig)

    # ------------------------------------------------------------------
    # THROUGHPUT
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df["segment"], df["throughput_kbps"], label="Throughput")
    ax.plot(
        df["segment"],
        df["avg_throughput_kbps"],
        label=f"Média móvel ({throughput_window})"
    )

    _draw_failover_lines(ax, failover_segs)

    ax.set_xlabel("Segmento")
    ax.set_ylabel("Throughput (kbps)")
    ax.set_title("Throughput e Média Móvel por Segmento")
    ax.legend()
    ax.grid(True)

    fig.savefig(
        f"{GRAPHS_DIR}/throughput{suffix}.png",
        bbox_inches="tight"
    )
    plt.close(fig)

    # ------------------------------------------------------------------
    # QUALIDADE
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    quality_labels = df["quality"].astype(str)

    if quality_order is None:
        quality_order = list(dict.fromkeys(quality_labels.tolist()))

    quality_codes = pd.Categorical(
        quality_labels,
        categories=quality_order,
        ordered=True
    ).codes

    ax.step(df["segment"], quality_codes, where="mid")

    _draw_failover_lines(ax, failover_segs)

    ax.set_yticks(range(len(quality_order)))
    ax.set_yticklabels(quality_order)
    ax.set_xlabel("Segmento")
    ax.set_ylabel("Qualidade selecionada")
    ax.set_title("Qualidade Selecionada por Segmento")
    ax.legend()
    ax.grid(True)

    fig.savefig(
        f"{GRAPHS_DIR}/quality{suffix}.png",
        bbox_inches="tight"
    )
    plt.close(fig)

    # ------------------------------------------------------------------
    # JITTER
    # ------------------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df["segment"], df["jitter_network_kbps"], label="Jitter Instantâneo")
    ax.plot(df["segment"], df["jitter_ewma_kbps"], label="Jitter EWMA")

    _draw_failover_lines(ax, failover_segs)

    ax.set_xlabel("Segmento")
    ax.set_ylabel("Jitter (kbps)")
    ax.set_title("Jitter por Segmento")
    ax.legend()
    ax.grid(True)

    fig.savefig(
        f"{GRAPHS_DIR}/jitter{suffix}.png",
        bbox_inches="tight"
    )
    plt.close(fig)


def plot_policy_comparison(
    csv_paths: dict,
    quality_order=None,
    throughput_window=5
):
    """
    Gera um gráfico comparativo das políticas ABR lado a lado.

    csv_paths: dicionário {"RATE": "logs/metrics_RATE.csv", "BUFFER": ..., "HYBRID": ...}

    Exemplo de uso:
        plot_policy_comparison({
            "RATE":   "logs/metrics_RATE.csv",
            "BUFFER": "logs/metrics_BUFFER.csv",
            "HYBRID": "logs/metrics_HYBRID.csv",
        })
    """

    os.makedirs(GRAPHS_DIR, exist_ok=True)

    policy_data = {}

    for policy_name, path in csv_paths.items():
        if not os.path.exists(path):
            print(f"[plot] CSV não encontrado: {path} — pulando {policy_name}")
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["avg_throughput_kbps"] = (
            df["throughput_kbps"]
            .rolling(window=throughput_window, min_periods=1)
            .mean()
        )
        policy_data[policy_name] = df

    if not policy_data:
        print("[plot] Nenhum CSV válido encontrado para comparação.")
        return

    # Resolve quality_order global (união de todas as qualidades encontradas)
    if quality_order is None:
        all_qualities = []
        for df in policy_data.values():
            all_qualities += df["quality"].astype(str).tolist()
        quality_order = list(dict.fromkeys(all_qualities))

    fig, axes = plt.subplots(3, 1, figsize=(12, 14), sharex=False)

    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

    # --- Throughput médio ---
    ax = axes[0]
    for idx, (name, df) in enumerate(policy_data.items()):
        ax.plot(
            df["segment"],
            df["avg_throughput_kbps"],
            label=name,
            color=colors[idx % len(colors)]
        )
        for seg in _failover_segments(df):
            ax.axvline(x=seg, color=colors[idx % len(colors)],
                       linestyle=":", linewidth=1.0)

    ax.set_ylabel("Throughput médio (kbps)")
    ax.set_title("Comparação de Políticas ABR — Throughput Médio")
    ax.legend()
    ax.grid(True)

    # --- Nível do buffer ---
    ax = axes[1]
    for idx, (name, df) in enumerate(policy_data.items()):
        ax.plot(
            df["segment"],
            df["buffer_level_s"],
            label=name,
            color=colors[idx % len(colors)]
        )
        for seg in _failover_segments(df):
            ax.axvline(x=seg, color=colors[idx % len(colors)],
                       linestyle=":", linewidth=1.0)

    ax.set_ylabel("Buffer (s)")
    ax.set_title("Comparação de Políticas ABR — Nível do Buffer")
    ax.legend()
    ax.grid(True)

    # --- Qualidade selecionada ---
    ax = axes[2]
    for idx, (name, df) in enumerate(policy_data.items()):
        quality_codes = pd.Categorical(
            df["quality"].astype(str),
            categories=quality_order,
            ordered=True
        ).codes
        ax.step(
            df["segment"],
            quality_codes,
            where="mid",
            label=name,
            color=colors[idx % len(colors)]
        )
        for seg in _failover_segments(df):
            ax.axvline(x=seg, color=colors[idx % len(colors)],
                       linestyle=":", linewidth=1.0)

    ax.set_yticks(range(len(quality_order)))
    ax.set_yticklabels(quality_order)
    ax.set_xlabel("Segmento")
    ax.set_ylabel("Qualidade")
    ax.set_title("Comparação de Políticas ABR — Qualidade Selecionada")
    ax.legend()
    ax.grid(True)

    fig.tight_layout(pad=3.0)

    out_path = f"{GRAPHS_DIR}/comparison_policies.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

    print(f"[plot] Comparativo salvo em {out_path}")