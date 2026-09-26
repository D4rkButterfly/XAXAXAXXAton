import os
import torch
import torchaudio
import io
import gigaam
from config.settings import AUDIO_SAMPLE_RATE

class GigaAMTranscriber:
    def __init__(self):
        print("⏳ Загрузка локальной SOTA-модели Sber GigaAM-v3...")
        # e2e_rnnt автоматически расставляет знаки препинания и регистр
        # Для работы на CPU без видеокарты форсируем device="cpu"
        self.device = "cpu"
        self.model = gigaam.load_model("e2e_rnnt", device=self.device)
        print("✅ GigaAM успешно загружена и готова к работе!")
        
    def transcribe_file(self, file_path: str) -> str:
        """Распознавание любых файлов через встроенный инференс GigaAM"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
            
        print(f"⏳ GigaAM анализирует файл: {file_path}...")
        # Метод сам под капотом использует нужные конвертации
        text = self.model.transcribe(file_path)
        return text.strip()

    def transcribe_live_stream(self, audio_generator) -> None:
        """
        Обработка потока реального времени (микрофон / телефония).
        Накапливает контекст (~3 секунды) для точной работы модели RNN-T.
        """
        print("🎙️ Потоковый GigaAM запущен. Говорите...")
        
        audio_buffer = bytearray()
        # Расчет байт на 3 секунды для накопления контекста
        BYTES_PER_SECOND = AUDIO_SAMPLE_RATE * 2  # 16-bit PCM = 2 байта на семпл
        CHUNK_THRESHOLD = int(BYTES_PER_SECOND * 3.0) 
        
        for chunk in audio_generator:
            audio_buffer.extend(chunk)
            
            if len(audio_buffer) >= CHUNK_THRESHOLD:
                # Конвертируем PCM-байты в PyTorch тензор
                audio_int16 = torch.from_buffer(audio_buffer, dtype=torch.int16)
                audio_float32 = audio_int16.to(torch.float32) / 32768.0
                
                # Добавляем размерность батча и канала: [1, количество_семплов]
                audio_tensor = audio_float32.unsqueeze(0)
                
                # Отправляем кусок в модель
                try:
                    # Для инференса raw-тензоров используем внутренний метод модели
                    with torch.no_grad():
                        text = self.model.transcribe(audio_tensor)
                    
                    if text.strip():
                        print(f" ⏳ [В эфире]: {text.strip()}")
                except Exception as e:
                    print(f"⚠️ Ошибка обработки чанка: {e}")
                
                # Очищаем буфер под следующую фразу
                audio_buffer.clear()
