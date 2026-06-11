import streamlit as st

from agents.journal_agent import JournalAgent
from services.gemini_service import GeminiService


st.set_page_config(
    page_title="Entre Sessões",
    page_icon="🫧"
)

st.title("🫧 Entre Sessões")

st.markdown("""
Sua memória emocional entre sessões de terapia.

Nem tudo que acontece durante a semana chega à terapia.
Registre seus pensamentos antes que eles sejam esquecidos.
""")


# Inicializa serviços
llm = GeminiService()
journal = JournalAgent(llm)


# Inicializa histórico
if "messages" not in st.session_state:
    st.session_state.messages = []


# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Entrada do usuário
if prompt := st.chat_input("O que aconteceu hoje?"):

    # Salva mensagem do usuário
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Exibe mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Envia TODO o histórico para o agente
    resposta = journal.generate(
        st.session_state.messages
    )

    # Salva resposta da IA
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resposta
        }
    )

    # Exibe resposta
    with st.chat_message("assistant"):
        st.markdown(resposta)