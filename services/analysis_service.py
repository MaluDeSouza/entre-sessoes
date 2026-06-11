import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.emotional_analysis import EmotionalAnalysis
from models.emotion import Emotion
from models.keyword import Keyword
from models.conversation import Conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.db = SessionLocal()

    def save_analysis(self, conversation_id: int, analysis_data: dict) -> EmotionalAnalysis:
        """
        Recebe o JSON gerado pelo AnalysisAgent e distribui nas tabelas
        emotional_analysis, emotions e keywords.
        """
        try:
            # 1. Salva a análise principal na tabela emotional_analysis
            new_analysis = EmotionalAnalysis(
                conversation_id=conversation_id,
                main_theme=analysis_data.get("main_theme"),
                sub_theme=analysis_data.get("sub_theme"),
                intensity=analysis_data.get("intensity"),
                analysis_json=analysis_data,  # O PostgreSQL aceita o dicionário direto aqui graças ao JSONB
                created_at=datetime.now()
            )
            
            self.db.add(new_analysis)
            self.db.commit()
            self.db.refresh(new_analysis) # Atualiza para pegar o ID gerado

            # 2. Salva as emoções individuais na tabela emotions
            emotions_list = analysis_data.get("emotions", [])
            for em_data in emotions_list:
                new_emotion = Emotion(
                    analysis_id=new_analysis.id,
                    emotion=em_data.get("emotion"),
                    score=em_data.get("score")
                )
                self.db.add(new_emotion)

             # 3. Salva as palavras-chave na tabela keywords
            keywords_list = analysis_data.get("keywords", [])
            for kw in keywords_list:
                new_keyword = Keyword(
                    analysis_id=new_analysis.id,
                    keyword=kw
                )
                self.db.add(new_keyword)

            # Comita as emoções e palavras-chave
            self.db.commit()
            
            # --- ADICIONE ESTA LINHA AQUI ---
            # Isso garante que o objeto seja recarregado na memória antes de fechar/retornar
            self.db.refresh(new_analysis)
            
            return new_analysis

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erro no banco de dados ao salvar a análise: {e}")
            raise
    def close(self):
        """
        Closes the database session safely.
        """
        self.db.close()