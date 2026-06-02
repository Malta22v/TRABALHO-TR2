def choose_quality(throughput_kbps, representations, safety_factor=0.8):
    """
    Escolhe a maior qualidade cujo bitrate seja menor
    que a vazão disponível com fator de segurança.
    """

    safe_throughput = throughput_kbps * safety_factor

    chosen = representations[0]

    for rep in representations:
        if rep["bitrate_kbps"] <= safe_throughput:
            chosen = rep

    return chosen