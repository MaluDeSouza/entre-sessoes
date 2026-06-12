import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Estrutura de dados esperada para os Insights
class InsightPattern(BaseModel):
    title: str = Field(..., description="Um título curto e impactante para o padrão descoberto")
    description: str = Field(..., description="O texto detalhado explicando a conexão, gatilho ou padrão emocional detectado")

class InsightResult(BaseModel):
    period: str = Field(..., description="O período analisado, ex: 'Últimos 30 dias'")
    insights: List[InsightPattern] = Field(..., description="Lista de 1 a 3 padrões profundos identificados")
    closing_message: str = Field(..., description="Uma mensagem acolhedora de encerramento")

# 2. Classe do Agente de Insights
class InsightAgent:
    def __init__(self):
        prompt_path = Path(__file__).parent.parent / "prompts" / "insight_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        schema_str = json.dumps(InsightResult.model_json_schema(), indent=2)
        
        json_instruction = f"""
        
        IMPORTANT: You must return ONLY a raw, valid JSON object. Do not wrap it in Markdown formatting (like ```json).
        The JSON object MUST strictly adhere to the following schema:
        {schema_str}
        """
        
        self.agent = Agent(
            model=Gemini(id=os.getenv("MODEL", "gemini-2.5-flash")),
            description="You are an expert behavioral pattern analyzer.",
            instructions=system_prompt + json_instruction
        )

    def generate_insights(self, historical_data: List[dict], period_label: str = "Últimos 30 dias") -> dict:
        """
        Recebe um longo histórico de dados (semanas/meses) e gera as descobertas.
        """
        if not historical_data:
            raise ValueError("Não há dados suficientes para gerar insights.")

        data_transcript = f"PERÍODO: {period_label}\n\nDADOS HISTÓRICOS:\n\n"
        for item in historical_data:
            data_transcript += json.dumps(item, ensure_ascii=False) + "\n"

        # Aciona o LLM
        response = self.agent.run(data_transcript)
        
        # Limpeza de markdown
        response_text = response.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            validated_data = InsightResult.model_validate_json(response_text)
            return validated_data.model_dump()
        except Exception as e:
            print(f"Pydantic validation error: {e}")
            return json.loads(response_text)