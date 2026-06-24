def choose_quality_buffer(
    buffer_level,
    representations
):
    """
    Política Buffer-Based ABR.

    Seleciona a qualidade com base no nível atual do buffer.
    A busca é feita por nome de qualidade (campo 'quality'), tornando
    a função robusta a mudanças de ordem ou quantidade de representações
    vindas do manifest.

    Thresholds:
        < 4s   → menor qualidade disponível (evitar rebuffering)
        < 8s   → 25% inferior da lista
        < 12s  → 50% (meio da lista)
        < 16s  → 75% superior
        >= 16s → maior qualidade disponível
    """

    if not representations:
        return None

    n = len(representations)

    # Ordena pelo bitrate para garantir a ordem crescente de qualidade,
    # independente da ordem em que o manifest retornou as representações.
    sorted_reps = sorted(representations, key=lambda r: r["bitrate_kbps"])

    def pick(index):
        return sorted_reps[max(0, min(index, n - 1))]

    if buffer_level < 4:
        return pick(0)

    elif buffer_level < 8:
        return pick(n // 4)

    elif buffer_level < 12:
        return pick(n // 2)

    elif buffer_level < 16:
        return pick(3 * n // 4)

    return pick(n - 1)