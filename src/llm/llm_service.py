# src/llm/llm_service.py
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


class LLMService:
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.client = MistralClient(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                ChatMessage(role="user", content=prompt)
            ],
        )
        return response.choices[0].message.content