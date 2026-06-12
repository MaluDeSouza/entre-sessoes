import logging
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.conversation import Conversation
from models.emotional_analysis import EmotionalAnalysis
from models.emotion import Emotion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self):
        self.db = SessionLocal()

    def get_emotions_frequency(self, user_id: int = 1, days: int = 30) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame with the frequency of each emotion 
        in the last 'days' for bar charts.
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Conta a frequência agrupada pelo nome da emoção
            results = (
                self.db.query(
                    Emotion.emotion.label("emotion_name"),
                    func.count(Emotion.id).label("frequency")
                )
                .join(EmotionalAnalysis, Emotion.analysis_id == EmotionalAnalysis.id)
                .join(Conversation, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    Conversation.started_at >= start_date
                )
                .group_by(Emotion.emotion)
                .order_by(func.count(Emotion.id).desc())
                .all()
            )
            
            # Formata para DataFrame e define a coluna X (índice)
            df = pd.DataFrame(results, columns=["Emoção", "Frequência"])
            if not df.empty:
                df.set_index("Emoção", inplace=True)
            return df

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching emotions frequency: {e}")
            raise
        finally:
            self.db.close()

    def get_intensity_timeline(self, user_id: int = 1, days: int = 30) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame with the average daily emotional intensity 
        for line charts.
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Agrupa pela data e tira a média da intensidade
            results = (
                self.db.query(
                    func.date(Conversation.started_at).label("date"),
                    func.avg(EmotionalAnalysis.intensity).label("avg_intensity")
                )
                .join(EmotionalAnalysis, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    Conversation.started_at >= start_date
                )
                .group_by(func.date(Conversation.started_at))
                .order_by(func.date(Conversation.started_at).asc())
                .all()
            )

            df = pd.DataFrame(results, columns=["Data", "Intensidade"])
            if not df.empty:
                # Converte para formato de data e seta como índice para o gráfico de linha
                df["Data"] = pd.to_datetime(df["Data"])
                df.set_index("Data", inplace=True)
            return df

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching intensity timeline: {e}")
            raise
        finally:
            self.db.close()

    def get_timeline_feed(self, user_id: int = 1, days: int = 30) -> list:
        """
        Returns a chronological list of recent sessions for the emotional feed.
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            results = (
                self.db.query(Conversation, EmotionalAnalysis)
                .join(EmotionalAnalysis, EmotionalAnalysis.conversation_id == Conversation.id)
                .filter(
                    Conversation.user_id == user_id,
                    Conversation.started_at >= start_date
                )
                .order_by(Conversation.started_at.desc()) # Ordena do mais novo pro mais antigo
                .all()
            )

            feed = []
            for conv, analysis in results:
                # Extrai o resumo salvo no json com segurança
                summary = ""
                if isinstance(analysis.analysis_json, dict):
                    summary = analysis.analysis_json.get("summary", "")
                    
                feed.append({
                    "date": conv.started_at.strftime("%d/%m/%Y %H:%M"),
                    "theme": analysis.main_theme,
                    "intensity": analysis.intensity,
                    "summary": summary
                })
            
            return feed

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching timeline feed: {e}")
            raise
        finally:
            self.db.close()