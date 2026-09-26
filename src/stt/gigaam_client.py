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

    def transcribe_live_stream(self, audio_generator, callback=None) -> None:
        """Обработка потока реального времени с отправкой в LLM через callback"""
        print("🎙️ Потоковый GigaAM запущен. Говорите...")
        
        audio_buffer = bytearray()
        BYTES_PER_SECOND = AUDIO_SAMPLE_RATE * 2
        CHUNK_THRESHOLD = int(BYTES_PER_SECOND * 3.0) 
        
        for chunk in audio_generator:
            audio_buffer.extend(chunk)
            
            if len(audio_buffer) >= CHUNK_THRESHOLD:
                try:
                    np_array = np.frombuffer(audio_buffer, dtype=np.int16).copy()
                    audio_tensor = torch.from_numpy(np_array).to(torch.float32) / 32768.0
                    audio_tensor = audio_tensor.unsqueeze(0).to(self.device)
                    lengths = torch.LongTensor([audio_tensor.size(1)]).to(self.device)
                    
                    with torch.no_grad():
                        encoded, encoded_len = self.model.forward(audio_tensor, lengths)
                        output = self.model.decoding.decode(self.model.head, encoded, encoded_len)
                    
                    text = ""
                    if hasattr(output, "text"): text = output.text
                    elif isinstance(output, (list, tuple)) and len(output) > 0: text = str(output)
                    else: text = str(output)
                    
                    clean_text = text.strip()
                    if clean_text:
                        # 🟢 ИСПРАВЛЕНИЕ: Вместо простого print() отдаем текст в LLM-коллбек
                        if callback:
                            callback(clean_text)
                        else:
                            print(f" ⏳ [В эфире]: {clean_text}")
                        
                except Exception as e:
                    print(f"⚠️ Ошибка обработки чанка: {e}")
                
                audio_buffer.clear()

