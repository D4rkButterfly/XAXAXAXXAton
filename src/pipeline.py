import time
from src.audio.mic_streamer import AudioMicStreamer
from src.stt.gigaam_client import GigaAMTranscriber
from src.llm.llm_client import LLMStructurer

class VoicePipeline:
    def __init__(self):
        self.mic_streamer = AudioMicStreamer()
        self.transcriber = GigaAMTranscriber()
        self.llm = LLMStructurer()
        
    def process_file(self, file_path: str):
        """Режим для файлов (голосовые сообщения)"""
        start_time = time.time()
        try:
            # 1. Распознаем файл через GigaAM
            text = self.transcriber.transcribe_file(file_path)
            if not text:
                print("❌ Речь на аудиозаписи не обнаружена.")
                return
                
            print(f"\n📝 Текст записи: {text}")
            
            # 2. Отправляем в GigaChat
            print("🤖 Анализ текста моделью GigaChat...")
            structured_json = self.llm.structure_request(text)
            
            print("\n✨ Структурированный JSON от Сбер GigaChat:")
            print(structured_json)
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Ошибка обработки файла: {e}")

    def process_live(self):
        """Режим реального времени (Микрофон / IP-телефония)"""
        try:
            # Передаем ссылку на метод отправки в LLM прямо внутрь обработчика стрима
            audio_generator = self.mic_streamer.stream_mic(chunk_size=4000)
            
            # Модифицируем запуск: теперь gigaam_client должен уметь вызывать llm-слой на лету.
            # Для этого временно переопределим логику прямо здесь или пропатчим вызов
            print("🎙️ Потоковый ввод запущен. Говорите фразы...")
            
            # Прокси-метод, который ловит текст из GigaAM и шлет в GigaChat
            def on_text_recognized(text: str):
                print(f"\n📝 Услышано: {text}")
                print("🤖 GigaChat думает...")
                result_json = self.llm.structure_request(text)
                print(f"✨ JSON команды:\n{result_json}\n")
            
            # Чтобы это заработало красиво, передадим этот коллбек в метод транскрибации
            self.transcriber.transcribe_live_stream(audio_generator, callback=on_text_recognized)
            
        except KeyboardInterrupt:
            print("\n🛑 Потоковое распознавание остановлено.")
