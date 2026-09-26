import time
from src.audio.mic_streamer import AudioMicStreamer
from src.stt.gigaam_client import GigaAMTranscriber # Подключаем GigaAM
from src.llm.llm_client import LLMStructurer

class VoicePipeline:
    def __init__(self):
        self.mic_streamer = AudioMicStreamer()
        self.transcriber = GigaAMTranscriber()
        self.llm = LLMStructurer()
        
    def process_file(self, file_path: str):
        """Режим для файлов (голосовые из мессенджеров любого формата)"""
        start_time = time.time()
        try:
            text = self.transcriber.transcribe_file(file_path)
            if text:
                print(f"\n📝 Итоговый текст (GigaAM): {text}")
                llm_result = self.llm.structure_request(text)
                print(f"🤖 LLM результат: {llm_result}")
            else:
                print("❌ Речь не обнаружена.")
        except Exception as e:
            print(f"❌ Ошибка обработки файла: {e}")

    def process_live(self):
        """Режим для живого потока (IP-телефония / Микрофон)"""
        try:
            audio_generator = self.mic_streamer.stream_mic(chunk_size=4000)
            self.transcriber.transcribe_live_stream(audio_generator)
        except KeyboardInterrupt:
            print("\n🛑 Потоковое распознавание остановлено.")
        except Exception as e:
            print(f"❌ Ошибка в живом потоке: {e}")
