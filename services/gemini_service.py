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
        """
        Recebe uma lista de mensagens e devolve apenas o texto da resposta.
        """

        prompt = self._build_prompt(messages)

        response = self.agent.run(prompt)

        return response.content

    def _build_prompt(self, messages):
        """
        Converte o histórico em um único prompt.
        """

        sections = []

        for message in messages:

            role = message["role"]
            content = message["content"]

            if role == "system":
                sections.append(f"Sistema:\n{content}")

            elif role == "user":
                sections.append(f"Usuário:\n{content}")

            elif role == "assistant":
                sections.append(f"Assistente:\n{content}")

        return "\n\n".join(sections)