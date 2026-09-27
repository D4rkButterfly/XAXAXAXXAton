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
    
    def fill_template_fields(self, raw_text: str, template_description: str, field_names: list) -> dict:
        from datetime import date
        today = date.today().strftime("%d.%m.%Y")

        system_prompt = (
            f"Ты заполняешь отчёт по шаблону.\n"
            f"Описание шаблона: {template_description}\n"
            f"Нужные поля: {', '.join(field_names)}\n"
            f"Сегодняшняя дата: {today}\n\n"
            "Правила:\n"
            "1. Если поле подразумевает дату, а в тексте прямая дата не названа — "
            f"подставь сегодняшнюю дату ({today}), если это уместно по смыслу.\n"
            "2. Если поле подразумевает сумму, количество или итог (например 'итого', "
            "'сумма', 'общее количество') — самостоятельно посчитай на основе чисел "
            "из текста (сложи, умножь на цену, если она указана, посчитай количество "
            "перечисленных позиций и т.д.). Указывай только результат, без вычислений в тексте.\n"
            "3. Если данных для поля действительно нет и вычислить нельзя — пустая строка.\n"
            "4. Числа пиши цифрами, не прописью.\n\n"
            "Верни ТОЛЬКО JSON вида {\"поле\": \"значение\"} для каждого поля. "
            "Без markdown, без пояснений вне JSON."
        )
        response = self.client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_text}],
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()
        print(f"🔍 Сырой ответ GigaChat: {raw}")

        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "", 1).strip()

        import json
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"❌ Не удалось распарсить JSON: {e}\nОтвет был: {raw}")
            return {name: "" for name in field_names}
