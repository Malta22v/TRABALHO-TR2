class BufferManager:

    def __init__(self):
        self.buffer_level: float = 0.0
        self.buffer_can_play: bool = False
        self.rebuffer_event: int = 0
        self.stall_duration_s: float = 0.0
        self._was_playing: bool = False
        self.BUFFER_MAX = 30
        self.BUFFER_TARGET_S = 15
        self.BUFFER_MIN_S = 4
        self.BUFFER_CRITICAL_S = 1

    def update_buffer(
        self,
        segment_duration: float,
        download_time: float
    ) -> float:

        raw_level = self.buffer_level + segment_duration - download_time

        # Se o nível bruto ficou negativo, o buffer esgotou durante o download.
        # O tempo que ficou em zero é a magnitude do déficit.
        if raw_level < 0:
            self.stall_duration_s = round(abs(raw_level), 3)
        else:
            self.stall_duration_s = 0.0

        self.buffer_level = max(0.0, raw_level)

        self._update_buffer_can_play(self.buffer_level)
        self._update_rebuffer_event()

        return self.buffer_level

    def _update_buffer_can_play(self, buffer_level: float) -> bool:
        self.buffer_can_play = buffer_level > self.BUFFER_MIN_S
        return self.buffer_can_play

    def _update_rebuffer_event(self) -> None:
        if self._was_playing and not self.buffer_can_play:
            self.rebuffer_event += 1
        self._was_playing = self.buffer_can_play

    def download_mode(self) -> str:
        if self.buffer_level < self.BUFFER_TARGET_S:
            return "burst"
        return "on/off"

    def buffer_confidence(self) -> str:
        if self.buffer_level < self.BUFFER_CRITICAL_S:
            return "CRITICAL"
        elif self.buffer_level < self.BUFFER_MIN_S:
            return "VERY_LOW"
        elif self.buffer_level < self.BUFFER_TARGET_S:
            return "LOW"
        else:
            return "GOOD"