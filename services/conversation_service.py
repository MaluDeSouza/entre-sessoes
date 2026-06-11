import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.conversation import Conversation
from models.message import Message
from models.user import User

# Configuração básica de logging para capturar erros do banco
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.db = SessionLocal()

    def _ensure_default_user_exists(self, user_id: int = 1):
        """
        Ensures a default user exists to prevent ForeignKeyViolation errors
        since there is no user registration flow yet.
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                default_user = User(
                    id=user_id,
                    name="MVP User",
                    email="test@entresessoes.com",
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                )
                self.db.add(default_user)
                self.db.commit()
                
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while ensuring default user exists: {e}")
            raise

    def create_conversation(self, user_id: int = 1) -> Conversation:
        """
        Creates a new conversation session for the given user.
        """
        self._ensure_default_user_exists(user_id)
        
        try:
            new_conversation = Conversation(
                user_id=user_id,
                started_at=datetime.now(),
                title="New Conversation",      
                summary=None                
            )
            
            self.db.add(new_conversation)
            self.db.commit()
            self.db.refresh(new_conversation) 
            
            return new_conversation
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while creating conversation: {e}")
            raise

    def save_message(self, conversation_id: int, role: str, content: str) -> Message:
        """
        Saves a single message (user or assistant) tied to a conversation.
        """
        try:
            new_message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=datetime.now()
            )
            
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            
            return new_message
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while saving message: {e}")
            raise

    def load_messages(self, conversation_id: int) -> list:
        """
        Retrieves all messages for a specific conversation formatted for the LLM.
        """
        try:
            messages = (
                self.db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .all()
            )
            
            # Formata a saída exatamente como o Streamlit/LLM esperam (lista de dicionários)
            return [{"role": msg.role, "content": msg.content} for msg in messages]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while loading messages: {e}")
            raise

    def close(self):
        """
        Closes the database session safely.
        """
        self.db.close()