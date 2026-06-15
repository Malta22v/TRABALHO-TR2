def choose_quality_buffer(
    buffer_level,
    representations
):

    if buffer_level < 4:
        return representations[0]  # 240p

    elif buffer_level < 8:
        return representations[1]  # 360p

    elif buffer_level < 12:
        return representations[2]  # 480p

    elif buffer_level < 16:
        return representations[3]  # 720p

    return representations[4]      # 1080p