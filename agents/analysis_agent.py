import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

class EmotionDetail(BaseModel):
    emotion: str = Field(..., description="Name of the emotion (e.g., anxiety, joy, fear, frustration)")
    score: float = Field(..., description="Intensity of this specific emotion from 0.0 to 10.0")

class AnalysisResult(BaseModel):
    main_theme: str = Field(..., description="The main topic discussed by the user (e.g., career, driving, relationship)")
    sub_theme: Optional[str] = Field(None, description="A sub-topic, if applicable")
    intensity: float = Field(..., description="Overall emotional intensity of the session from 0.0 to 10.0")
    emotions: List[EmotionDetail] = Field(..., description="List of the main emotions detected in the user")
    keywords: List[str] = Field(..., description="Up to 5 important keywords from the conversation")
    summary: str = Field(..., description="A short and direct summary of what happened, focused on what should be brought to therapy")

class AnalysisAgent:
    def __init__(self):
        # Lê o prompt do arquivo externo
        # Ajuste o caminho dependendo de onde a pasta prompts está localizada
        prompt_path = Path(__file__).parent.parent / "prompts" / "analysis_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        schema_str = json.dumps(AnalysisResult.model_json_schema(), indent=2)
        
        # Adiciona a instrução estrita para forçar a saída como JSON limpo e estruturado
        json_instruction = f"""
        
        IMPORTANT: You must return ONLY a raw, valid JSON object. Do not wrap it in Markdown formatting (like ```json).
        The JSON object MUST strictly adhere to the following schema:
        {schema_str}
        """
        
        # Inicializa o agente sem o argumento 'response_model' que estava causando o erro
        self.agent = Agent(
            model=Gemini(id=os.getenv("MODEL", "gemini-2.5-flash")),
            description="You are an expert psychological data analyst.",
            instructions=system_prompt + json_instruction
        )
        
    def analyze_conversation(self, messages: List[dict]) -> dict:
            """
            Receives the conversation history and returns the structured analysis.
            """
            if not messages:
                raise ValueError("The conversation history is empty.")

            # Converte a lista de dicionários em um texto contínuo para o prompt do LLM
            chat_transcript = "CONVERSATION TRANSCRIPT:\n\n"
            for msg in messages:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                chat_transcript += f"{role}: {content}\n"

            # Aciona o Agno passando o texto da conversa
            response = self.agent.run(chat_transcript)
        
            # Limpa a resposta caso o LLM ainda assim mande formatação de código markdown
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            try:
                # O Pydantic valida se a string JSON obedece exatamente à nossa classe AnalysisResult
                validated_data = AnalysisResult.model_validate_json(response_text)
                # Converte de volta para um dicionário Python limpo
                return validated_data.model_dump()
            except Exception as e:
                # Fallback direto caso a validação falhe
                print(f"Pydantic validation error: {e}")
                return json.loads(response_text)