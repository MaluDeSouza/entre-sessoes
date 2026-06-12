import logging
import json
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.conversation import Conversation
from models.emotional_analysis import EmotionalAnalysis
from models.insight import Insight
from agents.insight_agent import InsightAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightService:
    def __init__(self):
        self.db = SessionLocal()

    def generate_and_save_insights(self, user_id: int = 1, days: int = 30) -> dict:
        """
        Busca as conversas dos últimos X dias, passa pelo InsightAgent,
        e salva o resultado na tabela insights.
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # 1. Busca as sessões do período no banco
            results = (
                self.db.query(Conversation, EmotionalAnalysis)
                .join(EmotionalAnalysis, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    Conversation.started_at >= start_date
                )
                .order_by(Conversation.started_at.asc())
                .all()
            )

            if not results:
                return None

            # 2. Formata os dados reais do usuário para o Agente
            historical_data = []
            for conv, analysis in results:
                # Extrai o resumo salvo no json com segurança
                summary = ""
                if isinstance(analysis.analysis_json, dict):
                    summary = analysis.analysis_json.get("summary", "")
                    
                historical_data.append({
                    "data": conv.started_at.strftime("%d/%m/%Y"),
                    "tema": analysis.main_theme,
                    "intensidade": analysis.intensity,
                    "resumo": summary
                })

            # 3. Gera os insights com a IA
            agent = InsightAgent()
            period_label = f"Últimos {days} dias"
            resultado_insights = agent.generate_insights(historical_data, period_label=period_label)

            # 4. Salva o padrão descoberto no banco de dados, na tabela insights
            novo_insight = Insight(
                created_at=datetime.now(),
                text=json.dumps(resultado_insights, ensure_ascii=False), # Salva como texto JSON
                period=period_label
            )
            self.db.add(novo_insight)
            self.db.commit()
            self.db.refresh(novo_insight)
            
            return resultado_insights

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erro no banco de dados ao gerar insights: {e}")
            raise
        finally:
            self.db.close()