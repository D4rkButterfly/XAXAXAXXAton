import os
import json
from vosk import Model, KaldiRecognizer
from config.settings import VOSK_MODEL_PATH, AUDIO_SAMPLE_RATE

class VoskTranscriber:
    def __init__(self):
        if not os.path.exists(VOSK_MODEL_PATH):
            raise FileNotFoundError(f"Модель Vosk не найдена по пути: {VOSK_MODEL_PATH}")
        print(f"Загрузка модели Vosk...")
        self.model = Model(VOSK_MODEL_PATH)
        
    def transcribe(self, audio_generator, is_live: bool = False) -> str:
        """
        Универсальный метод транскрибации. 
        Если это живой поток (is_live=True), метод может возвращать текст частями 
        или работать до прерывания. Для файлов — считывает до конца.
        """
        recognizer = KaldiRecognizer(self.model, AUDIO_SAMPLE_RATE)
        full_text = []
        
        for chunk in audio_generator:
            if recognizer.AcceptWaveform(chunk):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    full_text.append(text)
                    print(f"💬 [Распознано]: {text}")
                    # Для живого потока здесь можно сразу отправлять текст дальше
                    if is_live:
                        pass 
                        
        final_result = json.loads(recognizer.FinalResult())
        text = final_result.get("text", "")
        if text:
            full_text.append(text)
            print(f"💬 [Финал]: {text}")
            
        return " ".join(full_text).strip()
