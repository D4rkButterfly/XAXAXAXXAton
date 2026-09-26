import os
from dotenv import load_dotenv

load_dotenv()

# Настройки Vosk
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-ru-0.22")
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))

# Настройки LLM API 
LLM_API_KEY = os.getenv("GIGACHAT_CREDENTIALS", "MDFhMGRlYWUtZTE1MS03NTg4LTk2OWYtN2VmMmU1ODZlYjAyOjRjM2I2NTE0LTMxOWMtNDA1YS1hZmU5LTE1ZDc1MzVjNjZlNg==")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://sberbank.ru")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "GigaChat-2")



