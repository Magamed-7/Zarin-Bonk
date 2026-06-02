import logging
from decimal import Decimal
from decouple import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — личный финансовый ассистент банка ZarinPay.
Говори на русском языке (или на языке пользователя, если он выберет другой).
Ты дружелюбный, профессиональный и всегда помогаешь пользователю с финансовыми вопросами.

Используй предоставленный контекст о балансах, транзакциях и кредитах пользователя, чтобы давать точные ответы.
Не придумывай данные, используй только ту информацию, что передана в контексте.

Отвечай кратко и по существу. Если у пользователя есть вопросы по финансовым продуктам — консультируй его.
"""

class AIService:
    def __init__(self):
        # Claude API ключи (Anthropic)
        self.claude_api_keys = [
            config('CLAUDE_API_KEY_1', default=None),
            config('CLAUDE_API_KEY_2', default=None),
        ]
        
        # Gemini API ключи (Google) - не менее 4-х
        self.gemini_api_keys = [
            config('GEMINI_API_KEY_1', default=None),
            config('GEMINI_API_KEY_2', default=None),
            config('GEMINI_API_KEY_3', default=None),
            config('GEMINI_API_KEY_4', default=None),
        ]
        
        # Groq API ключи
        self.groq_api_keys = [
            config('GROQ_API_KEY_1', default=None),
            config('GROQ_API_KEY_2', default=None),
        ]
        
        # DeepSeek API ключи
        self.deepseek_api_keys = [
            config('DEEPSEEK_API_KEY_1', default=None),
            config('DEEPSEEK_API_KEY_2', default=None),
        ]
        
        # OpenAI (GPT) API ключи
        self.openai_api_keys = [
            config('OPENAI_API_KEY_1', default=None),
            config('OPENAI_API_KEY_2', default=None),
        ]
        
        self.current_claude_index = 0
        self.current_gemini_index = 0
        self.current_groq_index = 0
        self.current_deepseek_index = 0
        self.current_openai_index = 0
    
    def get_ai_response(self, user_message, bank_context=None):
        full_context = SYSTEM_PROMPT
        if bank_context:
            full_context += f"\n\n=== ДАННЫЕ ПОЛЬЗОВАТЕЛЯ ===\n{bank_context}\n========================"
        
        # Пробуем Claude ключ 1, потом ключ 2
        for i in range(len(self.claude_api_keys)):
            key = self.claude_api_keys[(self.current_claude_index + i) % len(self.claude_api_keys)]
            if key:
                try:
                    response = self._call_claude(key, user_message, full_context)
                    logger.info(f"AI response from Claude (key {i+1})")
                    self.current_claude_index = (self.current_claude_index + i) % len(self.claude_api_keys)
                    return response
                except Exception as e:
                    logger.warning(f"Claude (key {i+1}) error: {e}")
                    continue
        
        # Если Claude не сработал, пробуем Gemini
        for i in range(len(self.gemini_api_keys)):
            key = self.gemini_api_keys[(self.current_gemini_index + i) % len(self.gemini_api_keys)]
            if key:
                try:
                    response = self._call_gemini(key, user_message, full_context)
                    logger.info(f"AI response from Gemini (key {i+1})")
                    self.current_gemini_index = (self.current_gemini_index + i) % len(self.gemini_api_keys)
                    return response
                except Exception as e:
                    logger.warning(f"Gemini (key {i+1}) error: {e}")
                    continue
        
        # Если Gemini не сработал, пробуем Groq
        for i in range(len(self.groq_api_keys)):
            key = self.groq_api_keys[(self.current_groq_index + i) % len(self.groq_api_keys)]
            if key:
                try:
                    response = self._call_groq(key, user_message, full_context)
                    logger.info(f"AI response from Groq (key {i+1})")
                    self.current_groq_index = (self.current_groq_index + i) % len(self.groq_api_keys)
                    return response
                except Exception as e:
                    logger.warning(f"Groq (key {i+1}) error: {e}")
                    continue
        
        # Если Groq не сработал, пробуем DeepSeek
        for i in range(len(self.deepseek_api_keys)):
            key = self.deepseek_api_keys[(self.current_deepseek_index + i) % len(self.deepseek_api_keys)]
            if key:
                try:
                    response = self._call_deepseek(key, user_message, full_context)
                    logger.info(f"AI response from DeepSeek (key {i+1})")
                    self.current_deepseek_index = (self.current_deepseek_index + i) % len(self.deepseek_api_keys)
                    return response
                except Exception as e:
                    logger.warning(f"DeepSeek (key {i+1}) error: {e}")
                    continue
        
        # Если DeepSeek не сработал, пробуем OpenAI (GPT)
        for i in range(len(self.openai_api_keys)):
            key = self.openai_api_keys[(self.current_openai_index + i) % len(self.openai_api_keys)]
            if key:
                try:
                    response = self._call_openai(key, user_message, full_context)
                    logger.info(f"AI response from OpenAI (GPT) (key {i+1})")
                    self.current_openai_index = (self.current_openai_index + i) % len(self.openai_api_keys)
                    return response
                except Exception as e:
                    logger.warning(f"OpenAI (key {i+1}) error: {e}")
                    continue
        
        # Если ни один не сработал - демо-режим
        logger.warning("All AI services failed, using demo mode")
        return self._demo_response(user_message, bank_context)
    
    def _demo_response(self, user_message, bank_context):
        responses = []
        
        if bank_context:
            responses.append("Привет! Я твой личный ассистент ZarinPay. Я вижу твою финансовую информацию. Если добавите сервер заработает, я смогу дать еще более детальные консультации!")
        
        responses.extend([
            f"Отличный вопрос! Это демо-режим, но я готов помочь, как только сервер заново заработает!",
            "👋 Здравствуйте! Я ZarinPay Assistant. Сейчас я работаю в демо-режиме !",
        ])
        
        import random
        return random.choice(responses)
    
    def _call_claude(self, api_key, user_message, context):
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "assistant", "content": context},
                {"role": "user", "content": user_message}
            ]
        )
        
        return message.content[0].text
    
    def _call_gemini(self, api_key, user_message, context):
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = f"{context}\n\nПользователь: {user_message}"
        response = model.generate_content(full_prompt)
        
        return response.text
    
    def _call_groq(self, api_key, user_message, context):
        from groq import Groq
        
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
        )
        
        return chat_completion.choices[0].message.content
    
    def _call_deepseek(self, api_key, user_message, context):
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.choices[0].message.content
    
    def _call_openai(self, api_key, user_message, context):
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ]
        )
        
        return response.choices[0].message.content
