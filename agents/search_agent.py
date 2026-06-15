import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

# Estrutura de resposta esperada
class SearchResult(BaseModel):
    answer: str = Field(..., description="A resposta narrativa, empática e analítica baseada nas memórias")
    related_themes: List[str] = Field(..., description="Lista de 1 a 3 subtemas ou emoções que apareceram nas memórias lidas")

class SearchAgent:
    def __init__(self):
        prompt_path = Path(__file__).parent.parent / "prompts" / "search_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        schema_str = json.dumps(SearchResult.model_json_schema(), indent=2)
        
        json_instruction = f"""
        
        IMPORTANT: You must return ONLY a raw, valid JSON object. Do not wrap it in Markdown formatting (like ```json).
        The JSON object MUST strictly adhere to the following schema:
        {schema_str}
        """
        
        self.agent = Agent(
            model=Gemini(id=os.getenv("MODEL", "gemini-2.5-flash")),
            description="You are an expert in analyzing emotional memory logs.",
            instructions=system_prompt + json_instruction
        )

    def answer_query(self, user_question: str, memories: List[dict]) -> dict:
        """
        Gera uma resposta analítica cruzando a pergunta do usuário com o histórico recuperado do banco.
        """
        
        # Constrói o contexto para o LLM ler
        context_data = f"PERGUNTA DO USUÁRIO: '{user_question}'\n\nMEMÓRIAS RECUPERADAS:\n"
        
        if not memories:
            context_data += "Nenhuma memória encontrada sobre este tema."
        else:
            for item in memories:
                context_data += json.dumps(item, ensure_ascii=False) + "\n"

        # Aciona o LLM
        response = self.agent.run(context_data)
        
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
            validated_data = SearchResult.model_validate_json(response_text)
            return validated_data.model_dump()
        except Exception as e:
            print(f"Pydantic validation error: {e}")
            return json.loads(response_text)