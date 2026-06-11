import streamlit as st
from agents.journal_agent import JournalAgent
from services.gemini_service import GeminiService


from services.conversation_service import ConversationService 

st.set_page_config(page_title="Entre Sessões", page_icon="🫧")
st.title("🫧 Entre Sessões")
st.markdown("""
Sua memória emocional entre sessões de terapia.
Nem tudo que acontece durante a semana chega à terapia. Registre seus pensamentos antes que eles sejam esquecidos.
""")

# Inicializa serviços do LLM e Agente
llm = GeminiService()
journal = JournalAgent(llm)

# 2. Inicializa o serviço de persistência
db_service = ConversationService()

# 3. Gerenciamento da Conversation no Banco
if "conversation_id" not in st.session_state:
    # Cria a sessão no banco de dados
    new_conversation = db_service.create_conversation()
    # Salva o ID gerado na memória do Streamlit
    st.session_state.conversation_id = new_conversation.id

# 4. Recupera o histórico de mensagens do banco
# Dessa forma, se a pessoa der F5, as mensagens não somem!
if "messages" not in st.session_state:
    st.session_state.messages = db_service.load_messages(st.session_state.conversation_id)

# Exibe o histórico na interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("O que aconteceu hoje?"):
    
    # --- FLUXO DO USUÁRIO ---
    # A) Exibe e salva a mensagem na memória da tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # B) Salva a mensagem no banco de dados permanentemente
    db_service.save_message(st.session_state.conversation_id, "user", prompt)

    # --- FLUXO DO AGENTE (LLM) ---
    with st.chat_message("assistant"):
        # C) Chama o Gemini passando o prompt atual ou o histórico 
        # (Ajuste o nome do método ".generate()" para o que você usa no JournalAgent)
        response = journal.generate(st.session_state.messages) 
        
        st.markdown(response)
        
    # D) Salva a resposta do Agente na memória da tela e no banco de dados
    st.session_state.messages.append({"role": "assistant", "content": response})
    db_service.save_message(st.session_state.conversation_id, "assistant", response)