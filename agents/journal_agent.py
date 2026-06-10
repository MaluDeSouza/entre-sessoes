from pathlib import Path


class JournalAgent:
    """
    Agente responsável por conduzir uma conversa acolhedora,
    incentivando reflexão e autoconhecimento.

    Não realiza diagnóstico nem aconselhamento clínico.
    """


    def __init__(self, llm_service):
        self.llm = llm_service

        prompt_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "journal_prompt.txt"
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            self.system_prompt = file.read()


    def generate(self, conversation):

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        messages.extend(conversation)

        return self.llm.generate(messages)