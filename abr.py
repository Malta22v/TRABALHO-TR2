def choose_quality(
    avg_throughput_kbps,
    representations,
    buffer_confidence,
    safety_factor=0.8,
    debug=False,
):
    """
    Escolhe a maior qualidade cujo bitrate seja menor
    que a vazão disponível com fator de segurança.
    """
    reference_quality_bitrate = [
    {"bitrate_kbps": 200, "quality": "240p"},
    {"bitrate_kbps": 400, "quality": "360p"},
    {"bitrate_kbps": 600, "quality": "480p"},
    {"bitrate_kbps": 900, "quality": "720p"},
    {"bitrate_kbps": 1200, "quality": "1080p"}
]
    if  buffer_confidence =='CRITICAL':
        return representations[0]
    
    if buffer_confidence =='GOOD':
        safety_factor=1.0
    elif buffer_confidence =='LOW':
        safety_factor=0.8
    elif buffer_confidence =='VERY_LOW':
        safety_factor=0.7
            
    safe_throughput = avg_throughput_kbps * safety_factor
    chosen = representations[0]
    
    for i,rep in enumerate(representations):
        if reference_quality_bitrate[i]["bitrate_kbps"] <= safe_throughput:
            chosen = rep

    if debug:
        print(f"Throughput médio: {avg_throughput_kbps:.0f} kbps")
        print(f"bitrate_kbps : {rep["bitrate_kbps"]}")
        print(f"Disponível (com safety): {safe_throughput:.0f} kbps")
        print(f"Qualidade selecionada: {chosen['quality']}")

    return chosen
