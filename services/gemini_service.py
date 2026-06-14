import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.media import Audio
from services.llm_service import LLMService

load_dotenv()


class GeminiService(LLMService):

    def __init__(self):
        # Instancia o agente usando o modelo definido na env
        self.agent = Agent(
            model=Gemini(
                id=os.getenv(
                    "MODEL",
                    "gemini-2.5-flash"
                )
            )
        )

    def generate(self, messages: list, audio_path: str = None) -> str:
        """
        Recebe o histórico de mensagens e opcionalmente um caminho de áudio.
        Retorna o texto da resposta gerada pelo Gemini, garantindo a mesma persona.
        """
        # 1. Usa o MESMO construtor de prompt para texto e áudio!
        # Isso garante que as regras do JournalAgent nunca sejam ignoradas.
        prompt_text = self._build_prompt(messages)

        if audio_path:
            # Mapeia o MIME type
            if audio_path.endswith(".ogg"):
                mime_type = "audio/ogg"
            elif audio_path.endswith(".wav"):
                mime_type = "audio/wav"
            else:
                mime_type = None

            audio_media = Audio(filepath=audio_path, mime_type=mime_type)
            
            # 2. Envia o roteiro formatado exatamente igual ao texto, mas com o áudio anexado
            response = self.agent.run(
                prompt_text,
                audio=[audio_media]
            )
        else:
            # Fluxo normal de texto puro
            response = self.agent.run(prompt_text)

        return response.content
        
    def _build_prompt(self, messages):
        """
        Converte o histórico em um único prompt (utilizado apenas para o fluxo de texto legacy).
        """
        sections = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                sections.append(f"Sistema:\\n{content}")
            elif role == "user":
                sections.append(f"Usuário:\\n{content}")
            elif role == "assistant":
                sections.append(f"Assistente:\\n{content}")

        return "\n\n".join(sections)