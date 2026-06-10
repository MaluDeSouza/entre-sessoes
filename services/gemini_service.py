import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini

load_dotenv()


class GeminiService:

    def __init__(self):

        self.agent = Agent(
            model=Gemini(
                id=os.getenv(
                    "MODEL",
                    "gemini-2.5-flash"
                )
            )
        )

    def generate(self, messages):

        prompt = self._build_prompt(messages)

        response = self.agent.run(prompt)
        print(type(response))
        print(response)
        return response.content

    def _build_prompt(self, messages):

        prompt = ""

        for message in messages:

            role = message["role"]
            content = message["content"]

            if role == "system":
                prompt += f"Sistema:\n{content}\n\n"

            elif role == "user":
                prompt += f"Usuário:\n{content}\n\n"

            elif role == "assistant":
                prompt += f"Assistente:\n{content}\n\n"

        return prompt

if __name__ == "__main__":

    service = GeminiService()

    resposta = service.generate(
        [
            {
                "role": "user",
                "content": "Diga apenas 'Olá Mundo'"
            }
        ]
    )

    print(resposta)