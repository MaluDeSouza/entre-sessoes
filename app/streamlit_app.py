import streamlit as st

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

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("O que aconteceu hoje?"):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    resposta = (
        "Obrigado por compartilhar isso comigo.\n\n"
        "Gostaria de entender melhor o que aconteceu. "
        "Pode me contar um pouco mais?"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resposta
        }
    )

    with st.chat_message("assistant"):
        st.markdown(resposta)