import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Estrutura do relatório que o usuário idealizou
class TopicSummary(BaseModel):
    theme: str = Field(..., description="Nome do tema principal (ex: Direção, Carreira)")
    frequency: int = Field(..., description="Quantidade de vezes que o tema apareceu na semana")
    predominant_emotions: List[str] = Field(..., description="Lista com as emoções mais marcantes do tema")
    priority: str = Field(..., description="Prioridade para levar à terapia: 'Alta', 'Média' ou 'Baixa'")
    summary: str = Field(..., description="Resumo narrativo unificando os acontecimentos relacionados a este tema")

class WeeklyReport(BaseModel):
    topics: List[TopicSummary] = Field(..., description="Lista de tópicos discutidos na semana")
    overall_message: str = Field(..., description="Uma mensagem curta e acolhedora de abertura do relatório semanal")

# 2. Classe do Agente de Resumo
class SummaryAgent:
    def __init__(self):
        # Carrega as instruções do prompt que acabamos de criar
        prompt_path = Path(__file__).parent.parent / "prompts" / "summary_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        # Extrai o esquema JSON do Pydantic para ensinar a IA
        schema_str = json.dumps(WeeklyReport.model_json_schema(), indent=2)
        
        json_instruction = f"""
        
        IMPORTANT: You must return ONLY a raw, valid JSON object. Do not wrap it in Markdown formatting (like ```json).
        The JSON object MUST strictly adhere to the following schema:
        {schema_str}
        """
        
        self.agent = Agent(
            model=Gemini(id=os.getenv("MODEL", "gemini-2.5-flash")),
            description="You are an expert psychological data summarizer.",
            instructions=system_prompt + json_instruction
        )

    def generate_weekly_summary(self, weekly_data: List[dict]) -> dict:
        """
        Recebe a lista de dados brutos da semana e retorna o relatório estruturado.
        """
        if not weekly_data:
            raise ValueError("Não há dados na semana para resumir.")

        # Converte os dados do banco para texto para o LLM analisar
        data_transcript = "DADOS DA SEMANA:\n\n"
        for item in weekly_data:
            data_transcript += json.dumps(item, ensure_ascii=False) + "\n"

        # Aciona o modelo
        response = self.agent.run(data_transcript)
        
        # Nossa trava de segurança anti-markdown
        response_text = response.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            validated_data = WeeklyReport.model_validate_json(response_text)
            return validated_data.model_dump()
        except Exception as e:
            print(f"Pydantic validation error: {e}")
            return json.loads(response_text)