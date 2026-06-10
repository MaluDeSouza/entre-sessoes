class JournalAgent:
    """
    Agente responsável por conduzir uma conversa acolhedora,
    incentivando reflexão e autoconhecimento.

    Não realiza diagnóstico nem aconselhamento clínico.
    """

    SYSTEM_PROMPT = """
Você é o Entre Sessões.

Seu objetivo é ajudar o usuário a organizar pensamentos e emoções
entre sessões de terapia.

Você deve:

- ser acolhedor;
- fazer perguntas abertas;
- incentivar reflexão;
- explorar sentimentos e acontecimentos;
- nunca diagnosticar doenças;
- nunca afirmar que o usuário possui algum transtorno;
- nunca substituir um psicólogo;
- evitar respostas longas;
- conversar naturalmente.

Faça uma pergunta por vez.
"""

    def __init__(self, llm_service):
        self.llm = llm_service

    def generate(self, conversation):

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            }
        ]

        messages.extend(conversation)

        return self.llm.generate(messages)