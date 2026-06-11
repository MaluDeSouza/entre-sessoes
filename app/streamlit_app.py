import streamlit as st
from agents.journal_agent import JournalAgent
from services.gemini_service import GeminiService
from services.conversation_service import ConversationService
from agents.analysis_agent import AnalysisAgent
from services.analysis_service import AnalysisService

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
    
# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Opções da Sessão")
    st.markdown("Quando terminar de refletir, encerre a sessão para salvar seus insights emocionais.")
    
    if st.button("Encerrar Sessão", type="primary"):
        # Só analisa se houver alguma conversa
        if len(st.session_state.messages) > 0:
            with st.spinner("Analisando sua sessão e estruturando suas emoções..."):
                try:
                    # 1. Roda a análise com o Agente
                    analyst = AnalysisAgent()
                    resultado = analyst.analyze_conversation(st.session_state.messages)
                    
                    # 2. Salva no Banco de Dados
                    analysis_db = AnalysisService()
                    analysis_db.save_analysis(st.session_state.conversation_id, resultado)
                    
                    # 3. Exibe o resumo na tela para dar feedback imediato de valor ao usuário
                    st.success("Sessão salva com sucesso!")
                    st.write("**Resumo da sua sessão:**")
                    st.info(resultado["summary"])
                    
                    st.write("**Tema Principal:**", resultado["main_theme"])
                    st.write("**Intensidade Emocional:**", f"{resultado['intensity']}/10")
                    
                    # Opcional: Limpar a sessão da memória para o usuário poder iniciar uma nova
                    # st.session_state.pop("conversation_id", None)
                    # st.session_state.pop("messages", None)
                    
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar a sessão: {e}")
        else:
            st.warning("A conversa ainda está vazia. Escreva algo antes de encerrar!")