import json
from openai import OpenAI
from config.settings import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME

class LLMStructurer:
    def __init__(self):
        # Инициализируем стандартный клиент OpenAI, направляя его на сервера Сбера
        # ВАЖНО для Windows/GigaChat: Сбер использует свои SSL-сертификаты Минцифры.
        # Если API выдает ошибку сертификата, в продакшене нужно установить сертификаты,
        # либо временно отключить проверку в среде (для тестов).
        self.client = OpenAI(
            api_key=LLM_API_KEY, 
            base_url=LLM_BASE_URL
        )
        
    def structure_request(self, raw_text: str) -> str:
        """Превращает неструктурированный текст в валидный JSON с намерениями и сущностями"""
        system_prompt = (
            "Ты — интеллектуальный модуль обработки команд умного дома и телефонии.\n"
            "Твоя задача — взять сырой текст распознанной речи и превратить его в структурированный JSON-запрос.\n"
            "Выдели следующие поля:\n"
            "1. intent (намерение пользователя английскими буквами в snake_case, например: 'create_task', 'call_abonent', 'check_weather', 'unknown')\n"
            "2. entities (слова-сущности в виде ключ-значение: даты, имена, объекты, локации, номера телефонов)\n"
            "3. clean_text (очищенный от мусора исходный текст)\n\n"
            "Отвечай СТРОГО в формате JSON. Любой текст вне JSON-структуры запрещен. "
            "Не используй markdown разметку, не пиши ```json."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.1,  # Минимальная температура для максимальной строгости формата
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f'{{"error": "Ошибка GigaChat API: {str(e)}"}}'
