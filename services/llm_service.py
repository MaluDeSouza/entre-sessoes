from abc import ABC, abstractmethod


class LLMService(ABC):

    @abstractmethod
    def generate(self, messages, audio_path: str = None):
        """
        Gera uma resposta baseada no histórico de mensagens.
        Opcionalmente aceita um caminho de arquivo de áudio para análise multimodal.
        """
        pass