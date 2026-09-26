# Захват живого потока (далее микрофон / IP-телефония) через PyAudio
import pyaudio
from typing import Generator
from config.settings import AUDIO_SAMPLE_RATE

class AudioMicStreamer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        
    def stream_mic(self, chunk_size: int = 4000) -> Generator[bytes, None, None]:
        """Бесконечный генератор байт с микрофона"""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=AUDIO_SAMPLE_RATE,
            input=True,
            frames_per_buffer=chunk_size
        )
        try:
            print("Микрофон активен. Говорите...")
            while True:
                # exception_on_overflow=False предотвращает падения при задержках процессора
                data = stream.read(chunk_size, exception_on_overflow=False)
                yield data
        finally:
            stream.stop_stream()
            stream.close()
