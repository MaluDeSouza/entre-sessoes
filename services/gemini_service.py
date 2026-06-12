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
        Retorna o texto da resposta gerada pelo Gemini de forma nativa.
        """
        if audio_path:
            # Transforma o arquivo de áudio em mídia nativa do Agno
            if audio_path.endswith(".ogg"):
                mime_type = "audio/ogg; codecs=opus"
            elif audio_path.endswith(".wav"):
                mime_type = "audio/wav"
            else:
                mime_type = None

            # Transforma o arquivo de áudio em mídia nativa com o formato explícito
            audio_media = Audio(filepath=audio_path, mime_type=mime_type)
                    
            prompt_tecnico = (
                "O usuário enviou o arquivo de áudio anexado. "
                "Processe o conteúdo falado e gere a sua resposta baseando-se UNICAMENTE "
                "nas regras, formato e persona definidos no seu System Prompt."
            )
            
            response = self.agent.run(
                prompt_tecnico,
                audio=[audio_media],
                messages=messages
            )
        else:
            # Fluxo normal de texto: mantemos a retrocompatibilidade usando o achatamento de prompt
            prompt_text = self._build_prompt(messages)
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