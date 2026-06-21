class BufferManager:
    def __init__(self):
        self.buffer_level: float= 0.0
        self.buffer_can_play: bool= False
        self.rebuffer_event: int = 0
        self._was_playing: bool = False
        self.BUFFER_MAX = 30
        self.BUFFER_TARGET_S = 15
        self.BUFFER_MIN_S = 4
        self.BUFFER_CRITICAL_S = 1

    def update_buffer(self, segment_duration: float, download_time: float) -> float:
        self.buffer_level= max(0.0, self.buffer_level + segment_duration - download_time)
        self.__update_buffer_can_play(self.buffer_level)
        self.__update_rebuffer_event()
        return self.buffer_level
    
    def __update_buffer_can_play(self, buffer_level: float)-> bool:
        if buffer_level > self.BUFFER_MIN_S:
            self.buffer_can_play= True
            return self.buffer_can_play
        self.buffer_can_play= False
        return self.buffer_can_play
        
    def __update_rebuffer_event(self) -> None:
        if self._was_playing and not self.buffer_can_play:
            self.rebuffer_event += 1
        self._was_playing = self.buffer_can_play
            
    def download_mode(self) -> str:
        if self.buffer_level < self.BUFFER_TARGET_S:
            return 'burst'
        return 'on/off'
    
    def buffer_confidence(self) -> str:
        if self.buffer_level < self.BUFFER_CRITICAL_S: 
            return "CRITICAL"
        
        elif  self.buffer_level < self.BUFFER_MIN_S:
            return "VERY_LOW"
        
        elif  self.buffer_level < self.BUFFER_TARGET_S:
            return "LOW"
        else :
            return "GOOD"



    