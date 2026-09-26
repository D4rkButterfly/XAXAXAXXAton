import os
import torch
import numpy as np
import gigaam
from config.settings import AUDIO_SAMPLE_RATE

class GigaAMTranscriber:
    def __init__(self):
        print("⏳ Загрузка локальной SOTA-модели Sber GigaAM-v3...")
        self.device = "cpu"
        self.model = gigaam.load_model("e2e_rnnt", device=self.device)
        print("✅ GigaAM успешно загружена и готова к работе!")
        
    def transcribe_file(self, file_path: str) -> str:
        """Распознавание любых готовых файлов с диска"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
            
        print(f"⏳ GigaAM анализирует файл: {file_path}...")
        result = self.model.transcribe(file_path)
        
        if hasattr(result, "text"):
            return result.text.strip()
        return str(result).strip()

    def transcribe_live_stream(self, audio_generator) -> None:
        """
        Прямая обработка живого потока байт (микрофон / телефония).
        Накапливает контекст и передает тензор напрямую в архитектуру кодера GigaAM.
        """
        print("🎙️ Потоковый GigaAM запущен. Говорите...")
        
        audio_buffer = bytearray()
        BYTES_PER_SECOND = AUDIO_SAMPLE_RATE * 2  # 16-bit PCM = 2 байта на семпл
        CHUNK_THRESHOLD = int(BYTES_PER_SECOND * 3.0) # Контекст по 3 секунды
        
        for chunk in audio_generator:
            audio_buffer.extend(chunk)
            
            if len(audio_buffer) >= CHUNK_THRESHOLD:
                try:
                    # Быстро переводим байты PCM в float32 тензор PyTorch
                    np_array = np.frombuffer(audio_buffer, dtype=np.int16).copy()
                    audio_tensor = torch.from_numpy(np_array).to(torch.float32) / 32768.0
                    
                    # Формируем правильную размерность для нейросети: [батч=1, количество_семплов]
                    audio_tensor = audio_tensor.unsqueeze(0).to(self.device)
                    
                    # Вычисляем фактическую длину тензора (сигнала)
                    lengths = torch.LongTensor([audio_tensor.size(1)]).to(self.device)
                    
                    # Прямой инференс через акустический кодер и декодер
                    with torch.no_grad():
                        encoded, encoded_len = self.model.forward(audio_tensor, lengths)
                        output = self.model.decoding.decode(self.model.head, encoded, encoded_len)
                    
                    # 🟢 ИСПРАВЛЕНИЕ: Вытаскиваем только чистую строку текста
                    text = ""
                    
                    # 1. Если это TranscriptionResult объект (характерно для файлов)
                    if hasattr(output, "text"):
                        text = output.text
                    
                    # 2. Если это список или кортеж (как в вашем живом потоке)
                    elif isinstance(output, (list, tuple)) and len(output) > 0:
                        # Если первый элемент — это тоже список/кортеж (двойная вложенность батча)
                        first_item = output[0]
                        if isinstance(first_item, (list, tuple)) and len(first_item) > 0:
                            text = str(first_item[0])
                        else:
                            text = str(first_item)
                    else:
                        text = str(output)
                    
                    # Финальный вывод только осмысленного текста
                    clean_text = text.strip()
                    if clean_text:
                        print(f" ⏳ [В эфире]: {clean_text}")
                        
                except Exception as e:
                    print(f"⚠️ Ошибка обработки чанка: {e}")
                
                # Полностью очищаем буфер под следующую фразу разговора
                audio_buffer.clear()
