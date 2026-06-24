class JitterCalculator:

    def __init__(self, alpha=0.3):
        self.last_throughput = None
        self.jitter_kbps = 0.0
        self.jitter_ewma_kbps = 0.0
        self.alpha = alpha

    def update(self, throughput_kbps):

        if self.last_throughput is None:
            self.last_throughput = throughput_kbps
            return 0.0, 0.0

        # Calcula a variação absoluta da capacidade da rede
        self.jitter_kbps = abs(
            throughput_kbps - self.last_throughput
        )

        # Filtro EWMA para suavizar os picos de instabilidade
        self.jitter_ewma_kbps = (
            self.alpha * self.jitter_kbps
            + (1 - self.alpha) * self.jitter_ewma_kbps
        )

        self.last_throughput = throughput_kbps

        return (
            round(self.jitter_kbps, 2),
            round(self.jitter_ewma_kbps, 2)
        )