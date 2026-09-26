# Потоковое чтение файлов через FFmpeg (далее мессенджеры)
import os
import subprocess
from typing import Generator
from config.settings import AUDIO_SAMPLE_RATE

class AudioFileStreamer:
    @staticmethod
    def stream_file(file_path: str, chunk_size: int = 8000) -> Generator[bytes, None, None]:
        """Универсальное чтение любого формата файла в PCM моно 16кГц"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
            
        command = [
            'ffmpeg', '-loglevel', 'quiet', '-i', file_path,
            '-f', 's16le', '-ac', '1', '-ar', str(AUDIO_SAMPLE_RATE), 'pipe:1'
        ]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            while True:
                chunk = process.stdout.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            process.stdout.close()
            process.terminate()
            process.wait()
