class JitterCalculator:

    def __init__(self, alpha=0.3):
        self.last_download_time = None
        self.jitter_ms = 0.0
        self.jitter_ewma_ms = 0.0
        self.alpha = alpha

    def update(self, download_time_s):

        if self.last_download_time is None:
            self.last_download_time = download_time_s
            return 0.0, 0.0

        self.jitter_ms = abs(
            download_time_s - self.last_download_time
        ) * 1000

        self.jitter_ewma_ms = (
            self.alpha * self.jitter_ms
            + (1 - self.alpha) * self.jitter_ewma_ms
        )

        self.last_download_time = download_time_s

        return (
            round(self.jitter_ms, 2),
            round(self.jitter_ewma_ms, 2)
        )