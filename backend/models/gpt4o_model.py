from .base import BaseModel
import httpx
import os

class GPT4OModel(BaseModel):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_id = "gpt-4o"
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}], 
            "temperature": 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()