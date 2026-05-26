class BufferManager:
    def __init__(self):
        self.buffer_level: float= 0.0
        self.buffer_can_play: bool= False
        self.rebuffer_event: int = 0
        self._was_playing: bool = False

    def att_buffer(self, segment_duration: float, download_time: float) -> float:
        self.buffer_level= max(0.0, self.buffer_level + segment_duration - download_time)
        self.__att_buffer_can_play(self.buffer_level)
        self.__att_rebuffer_event()
        return self.buffer_level
    
    def __att_buffer_can_play(self, buffer_level: float)-> bool:
        if buffer_level > 0.0:
            self.buffer_can_play= True
            return self.buffer_can_play
        self.buffer_can_play= False
        return self.buffer_can_play
        
    def __att_rebuffer_event(self) -> None:
        if self._was_playing and not self.buffer_can_play:
            self.rebuffer_event += 1
        self._was_playing = self.buffer_can_play
            


    