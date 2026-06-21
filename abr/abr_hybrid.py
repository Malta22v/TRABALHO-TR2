def choose_quality_hybrid(
    avg_throughput_kbps,
    representations,
    buffer_level,
    jitter_ewma_ms,
    debug=False
):

    jitter_penalty = min(
        jitter_ewma_ms / 1000.0,
        0.25
    )

    estimated_bandwidth = (
        avg_throughput_kbps
        * (1 - jitter_penalty)
    )

    if buffer_level < 4:
        estimated_bandwidth *= 0.7

    elif buffer_level < 8:
        estimated_bandwidth *= 0.85

    chosen = representations[0]

    for rep in representations:

        if rep["bitrate_kbps"] <= estimated_bandwidth:
            chosen = rep

    if debug:

        print("DECISÃO HYBRID")
        print(
            f"Throughput médio : "
            f"{avg_throughput_kbps:.0f} kbps"
        )

        print(
            f"Jitter EWMA      : "
            f"{jitter_ewma_ms:.1f} ms"
        )

        print(
            f"Buffer           : "
            f"{buffer_level:.2f} s"
        )

        print(
            f"Bandwidth estim. : "
            f"{estimated_bandwidth:.0f} kbps"
        )

        print(
            f"Qualidade        : "
            f"{chosen['quality']}"
        )

    return chosen