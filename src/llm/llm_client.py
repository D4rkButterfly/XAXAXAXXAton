class LLMStructurer:
    def structure_request(self, raw_text: str) -> str:
        """Будущая отправка текста в LLM. Пока работает как Mock-заглушка"""
        print(f"[LLM Layer]: Получен текст для анализа -> \"{raw_text}\"")
        # API
        return f'{{"intent": "pending", "clean_text": "{raw_text}"}}'
