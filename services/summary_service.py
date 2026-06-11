import logging
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.conversation import Conversation
from models.emotional_analysis import EmotionalAnalysis
from models.emotion import Emotion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        self.db = SessionLocal()

    def get_weekly_data(self, user_id: int = 1) -> list:
        """
        Busca todas as análises emocionais do usuário nos últimos 7 dias
        e formata para o formato esperado pelo SummaryAgent.
        """
        try:
            # Calcula a data de 7 dias atrás
            seven_days_ago = datetime.now() - timedelta(days=7)

            # Busca as Conversas que possuem Análise Emocional nos últimos 7 dias
            # Fazemos um JOIN entre as duas tabelas
            results = (
                self.db.query(EmotionalAnalysis, Conversation)
                .join(Conversation, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    Conversation.started_at >= seven_days_ago
                )
                .order_by(Conversation.started_at.asc()) # Ordena do mais antigo pro mais novo na semana
                .all()
            )

            weekly_data = []
            
            # Nomes dos dias da semana em português para o relatório
            dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

            for analysis, conversation in results:
                # Busca as emoções vinculadas a esta análise específica
                emotions = self.db.query(Emotion).filter(Emotion.analysis_id == analysis.id).all()
                emotion_names = [e.emotion for e in emotions]

                # Descobre qual dia da semana foi a conversa
                dia_nome = dias_semana[conversation.started_at.weekday()]

                # Pega o resumo que o AnalysisAgent gerou no dia da conversa
                # Garantimos que, se for string, tentamos ler do JSON
                resumo_diario = ""
                if isinstance(analysis.analysis_json, dict):
                    resumo_diario = analysis.analysis_json.get("summary", "")

                weekly_data.append({
                    "dia": dia_nome,
                    "tema": analysis.main_theme,
                    "intensidade": analysis.intensity,
                    "emocoes": emotion_names,
                    "resumo_diario": resumo_diario
                })

            return weekly_data

        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar dados da semana no banco: {e}")
            raise
        finally:
            self.db.close()