import statistics


HIGH_BUFFER_THRESHOLD_S = 14.0
LOW_THROUGHPUT_FACTOR = 0.55
HIGH_BUFFER_THROUGHPUT_MULTIPLIER = 2.0


def median_throughput_for_hybrid(
    throughput_history,
    buffer_level
):
    values = list(throughput_history)

    if not values:
        return 0.0

    median = statistics.median(values)

    if buffer_level <= HIGH_BUFFER_THRESHOLD_S:
        return median

    minimum_expected = median * LOW_THROUGHPUT_FACTOR
    filtered_values = [
        value
        for value in values
        if value >= minimum_expected
    ]

    if len(filtered_values) >= 3:
        return statistics.median(filtered_values)

    return median


def choose_quality_hybrid(
    avg_throughput_kbps,
    representations,
    buffer_level,
    jitter_ewma_kbps,
    debug=False
):
    safe_throughput = max(avg_throughput_kbps, 1.0)
    instability_ratio = jitter_ewma_kbps / safe_throughput

    if buffer_level > HIGH_BUFFER_THRESHOLD_S:
        penalty = min(instability_ratio, 0.10)
        estimated_bandwidth = (
            avg_throughput_kbps
            * HIGH_BUFFER_THROUGHPUT_MULTIPLIER
            * (1 - penalty)
        )
        state_debug = "ALTO (>14s)"

    elif buffer_level >= 12.0:
        estimated_bandwidth = avg_throughput_kbps * 1.10
        state_debug = "TRANSICAO (12s-14s)"

    elif buffer_level >= 8.0:
        penalty = min(instability_ratio, 0.20)
        estimated_bandwidth = avg_throughput_kbps * (1 - penalty)
        state_debug = "ATENCAO (8s-12s)"

    elif buffer_level >= 4.0:
        penalty = min(instability_ratio, 0.30)
        estimated_bandwidth = avg_throughput_kbps * (1 - penalty) * 0.4
        state_debug = "PERIGO (4s-8s)"

    else:
        estimated_bandwidth = 0
        state_debug = "CRITICO (<4s)"

    chosen = representations[0]
    for rep in representations:
        if rep["bitrate_kbps"] <= estimated_bandwidth:
            chosen = rep

    if debug:
        print(f"Estado Atual      : {state_debug}")
        print(f"Taxa Instabilidade: {instability_ratio:.2f}")
        print(f"Banda Estimada    : {estimated_bandwidth:.0f} kbps")

    return chosen
