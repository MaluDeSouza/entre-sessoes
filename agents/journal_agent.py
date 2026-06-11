from pathlib import Path


class JournalAgent:
    """
    Agente responsável por conduzir uma conversa acolhedora,
    incentivando reflexão e autoconhecimento.

    Não realiza diagnóstico nem aconselhamento clínico.
    """

    def __init__(self, llm_service):
        self.llm = llm_service
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        """
        Carrega o prompt do sistema a partir de arquivo externo.
        """
        prompt_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "journal_prompt.txt"
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    def generate(self, conversation_history):
        """
        Recebe o histórico completo da conversa e envia para o LLM.

        conversation_history deve ser uma lista no formato:

        [
            {"role": "user", "content": "Olá"},
            {"role": "assistant", "content": "Olá! Como você está?"},
            {"role": "user", "content": "Hoje tive um dia difícil."}
        ]
        """

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        messages.extend(conversation_history)

        response = self.llm.generate(messages)

        return response