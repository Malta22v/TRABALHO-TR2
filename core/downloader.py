import requests
import time
from datetime import datetime


CHUNK_SIZE = 1024  # bytes por chunk


def download_segment(base_url, url_path, quality):
    """
    Baixa um segmento via HTTP com leitura chunked.

    Além das métricas globais (throughput, download_time), calcula o
    jitter intra-segmento: variação do intervalo de chegada entre chunks
    consecutivos dentro do mesmo segmento. Esse valor reflete instabilidade
    real da rede no nível do TCP, não apenas entre segmentos.

    Retorna
    -------
    dict com:
        quality             : qualidade solicitada
        bytes_received      : total de bytes do segmento
        download_time_s     : duração total do download
        throughput_kbps     : vazão média do segmento
        jitter_intra_ms     : jitter médio intra-segmento (ms)
        timestamp           : ISO 8601 do início do download
    """

    full_url = f"{base_url}{url_path}"

    chunk_times = []   # timestamps de chegada de cada chunk
    total_bytes = 0

    timestamp = datetime.now().isoformat()
    start_time = time.perf_counter()

    with requests.get(full_url, stream=True, timeout=5) as response:

        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):

            if not chunk:
                continue

            chunk_times.append(time.perf_counter())
            total_bytes += len(chunk)

    end_time = time.perf_counter()

    download_time = end_time - start_time

    throughput_kbps = (
        (total_bytes * 8) / download_time / 1000
        if download_time > 0
        else 0.0
    )

    # Jitter intra-segmento: média dos |delta[i] - delta[i-1]| entre chunks.
    # Requer ao menos 3 chunks para ter 2 intervalos comparáveis.
    jitter_intra_ms = _compute_intra_jitter_ms(chunk_times)

    return {
        "quality": quality,
        "bytes_received": total_bytes,
        "download_time_s": round(download_time, 3),
        "throughput_kbps": round(throughput_kbps, 2),
        "jitter_intra_ms": round(jitter_intra_ms, 2),
        "timestamp": timestamp
    }


def _compute_intra_jitter_ms(chunk_times):
    """
    Calcula o jitter médio entre intervalos de chegada de chunks (RFC 3550).

    Fórmula: média de |D(i) - D(i-1)| onde D(i) = t[i] - t[i-1].
    Retorna 0.0 se não houver chunks suficientes.
    """

    if len(chunk_times) < 3:
        return 0.0

    intervals = [
        (chunk_times[i] - chunk_times[i - 1]) * 1000  # converte para ms
        for i in range(1, len(chunk_times))
    ]

    jitter_values = [
        abs(intervals[i] - intervals[i - 1])
        for i in range(1, len(intervals))
    ]

    return sum(jitter_values) / len(jitter_values)