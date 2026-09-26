from src.audio.file_streamer import AudioFileStreamer
from src.audio.mic_streamer import AudioMicStreamer
from src.stt.vosk_client import VoskTranscriber
from src.llm.llm_client import LLMStructurer

class VoicePipeline:
    def __init__(self):
        self.mic_streamer = AudioMicStreamer()
        self.transcriber = VoskTranscriber()
        self.llm = LLMStructurer()
        
    def process_file(self, file_path: str):
        """Режим 1: Транскрибация файла (Голосовые сообщения / Записи)"""
        print(f"\n🚀 Старт обработки файла: {file_path}")
        try:
            generator = AudioFileStreamer.stream_file(file_path)
            text = self.transcriber.transcribe(generator, is_live=False)
            
            if text:
                # Передача текста в слой LLM
                llm_result = self.llm.structure_request(text)
                print(f"✨ Результат: {llm_result}")
        except Exception as e:
            print(f"❌ Ошибка обработки файла: {e}")

    def process_live(self):
        """Режим 2: Живой поток (Микрофон / IP-телефония)"""
        print("\n🚀 Старт живого потока. Для остановки нажмите Ctrl+C")
        try:
            generator = self.mic_streamer.stream_mic()
            # Будет работать бесконечно, выводя текст в консоль на ходу
            self.transcriber.transcribe(generator, is_live=True)
        except KeyboardInterrupt:
            print("\n🛑 Живой поток остановлен пользователем.")
