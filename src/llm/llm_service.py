# src/llm/llm_service.py
import google.generativeai as genai

class LLMService:
    def __init__(self, api_key: str, model="gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text