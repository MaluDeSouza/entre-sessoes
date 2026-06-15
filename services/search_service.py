import logging
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.conversation import Conversation
from models.emotional_analysis import EmotionalAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.db = SessionLocal()

    def search_memories(self, user_id: int, search_term: str) -> list:
        """
        Vasculha o banco de dados em busca de conversas que correspondam
        ao termo pesquisado (ex: "Direção", "Carreira", "Ansiedade").
        """
        try:
            # O % ao redor do termo permite buscar a palavra em qualquer parte do texto (ilike ignora maiúsculas/minúsculas)
            term = f"%{search_term}%"

            results = (
                self.db.query(Conversation, EmotionalAnalysis)
                .join(EmotionalAnalysis, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    or_(
                        EmotionalAnalysis.main_theme.ilike(term),
                        EmotionalAnalysis.sub_theme.ilike(term)
                    )
                )
                .order_by(Conversation.started_at.desc()) # Retorna da mais recente para a mais antiga
                .all()
            )

            formatted_results = []
            for conv, analysis in results:
                # Extrai o resumo salvo com segurança
                summary = ""
                if isinstance(analysis.analysis_json, dict):
                    summary = analysis.analysis_json.get("summary", "")

                formatted_results.append({
                    "data": conv.started_at.strftime("%d/%m/%Y %H:%M"),
                    "tema": analysis.main_theme,
                    "intensidade": analysis.intensity,
                    "resumo": summary
                })

            return formatted_results

        except SQLAlchemyError as e:
            logger.error(f"Erro no banco de dados durante a busca: {e}")
            raise
        finally:
            self.db.close()