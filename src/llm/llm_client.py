import json
import httpx
from openai import OpenAI
from config.settings import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME
import uuid
import httpx

def get_access_token(auth_key: str) -> str:
    resp = httpx.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Authorization": f"Basic {auth_key}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"scope": "GIGACHAT_API_PERS"},  # или CORP/B2B — смотри тариф
        verify=False
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

class LLMStructurer:
    def __init__(self):
        # Инициализируем стандартный клиент OpenAI, направляя его на сервера Сбера
        # ВАЖНО для Windows/GigaChat: Сбер использует свои SSL-сертификаты Минцифры.
        # Если API выдает ошибку сертификата, в продакшене нужно установить сертификаты,
        # либо временно отключить проверку в среде (для тестов).
        access_token = get_access_token(LLM_API_KEY)
        self.client = OpenAI(
            api_key= access_token, 
            base_url=LLM_BASE_URL,
            http_client=httpx.Client(verify=False)
        )
    def fill_template_fields(self, raw_text: str, template_description: str, field_names: list) -> dict:
        system_prompt = (
            f"Ты заполняешь отчёт по шаблону.\n"
            f"Описание шаблона: {template_description}\n"
            f"Нужные поля: {', '.join(field_names)}\n"
            "На основе текста ниже верни ТОЛЬКО JSON вида {\"поле\": \"значение\"} "
            "для каждого поля. Если данных нет — пустая строка. Без markdown."
        )
        response = self.client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text}],
            temperature=0.3
        )
        print(f"🔍 Сырой ответ GigaChat: {response.choices[0].message.content.strip()}")
        import json
        return json.loads(response.choices[0].message.content.strip())
    
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
                temperature=0.3,  # Минимальная температура для максимальной строгости формата
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f'{{"error": "Ошибка GigaChat API: {str(e)}"}}'
