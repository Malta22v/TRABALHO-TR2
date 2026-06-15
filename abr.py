def choose_quality(
    avg_throughput_kbps,
    representations,
    buffer_confidence,
    safety_factor=0.8,
    debug=False,
):

    if buffer_confidence == "CRITICAL":
        return representations[0]

    if buffer_confidence == "GOOD":
        safety_factor = 1.0

    elif buffer_confidence == "LOW":
        safety_factor = 0.8

    elif buffer_confidence == "VERY_LOW":
        safety_factor = 0.7

    safe_throughput = (
        avg_throughput_kbps * safety_factor
    )

    chosen = representations[0]

    for rep in representations:

        if rep["bitrate_kbps"] <= safe_throughput:
            chosen = rep

    if debug:

        print(
            f"Throughput médio: "
            f"{avg_throughput_kbps:.0f} kbps"
        )

        print(
            f"Disponível (com safety): "
            f"{safe_throughput:.0f} kbps"
        )

        print(
            f"Bitrate escolhido: "
            f"{chosen['bitrate_kbps']} kbps"
        )

        print(
            f"Qualidade selecionada: "
            f"{chosen['quality']}"
        )

    return chosen