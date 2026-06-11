import streamlit as st
from agents.journal_agent import JournalAgent
from services.gemini_service import GeminiService
from services.conversation_service import ConversationService
from agents.analysis_agent import AnalysisAgent
from services.analysis_service import AnalysisService

# NOVAS IMPORTAÇÕES PARA O RESUMO SEMANAL
from agents.summary_agent import SummaryAgent
from services.summary_service import SummaryService

st.set_page_config(page_title="Entre Sessões", page_icon="🫧")
st.title("🫧 Entre Sessões")
st.markdown("""
Sua memória emocional entre sessões de terapia.
Nem tudo que acontece durante a semana chega à terapia. Registre seus pensamentos antes que eles sejam esquecidos.
""")

# Criação das Abas
aba_diario, aba_resumo = st.tabs(["💬 Meu Diário", "📊 Resumo Semanal"])

# ==========================================
# ABA 1: O DIÁRIO (Chat)
# ==========================================
with aba_diario:
    llm = GeminiService()
    journal = JournalAgent(llm)
    db_service = ConversationService()

    if "conversation_id" not in st.session_state:
        new_conversation = db_service.create_conversation()
        st.session_state.conversation_id = new_conversation.id

    if "messages" not in st.session_state:
        st.session_state.messages = db_service.load_messages(st.session_state.conversation_id)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("O que aconteceu hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        db_service.save_message(st.session_state.conversation_id, "user", prompt)

        with st.chat_message("assistant"):
            response = journal.generate(st.session_state.messages) 
            st.markdown(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        db_service.save_message(st.session_state.conversation_id, "assistant", response)

# ==========================================
# ABA 2: RESUMO SEMANAL
# ==========================================
with aba_resumo:
    st.header("Seu Resumo para a Terapia")
    st.markdown("Gere um relatório consolidado dos últimos 7 dias para levar à sua sessão.")
    
    if st.button("Gerar Resumo Semanal", type="primary"):
        with st.spinner("Analisando suas memórias da última semana..."):
            try:
                # 1. Busca dados no banco
                summary_db = SummaryService()
                dados_semana = summary_db.get_weekly_data(user_id=1)
                
                if not dados_semana:
                    st.info("Ainda não há reflexões suficientes nos últimos 7 dias para gerar um resumo.")
                else:
                    # 2. Gera o relatório com IA
                    summarizer = SummaryAgent()
                    relatorio = summarizer.generate_weekly_summary(dados_semana)
                    
                    # 3. Exibe na tela
                    st.success("Resumo gerado com sucesso!")
                    st.write(f"*{relatorio['overall_message']}*")
                    st.divider()
                    
                    # Itera sobre os tópicos e cria um "acordeão" (expander) para cada um
                    for topic in relatorio["topics"]:
                        # Define uma cor ou emoji baseado na prioridade
                        icone_prioridade = "🔴" if topic["priority"] == "Alta" else "🟡" if topic["priority"] == "Média" else "🟢"
                        
                        titulo_expander = f"{icone_prioridade} {topic['theme']} (Falou {topic['frequency']}x) - Prioridade: {topic['priority']}"
                        
                        with st.expander(titulo_expander, expanded=True):
                            st.write("**Resumo:**", topic["summary"])
                            st.write("**Emoções predominantes:**", ", ".join(topic["predominant_emotions"]))
                            
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o resumo: {e}")

# ==========================================
# BARRA LATERAL (Encerrar Sessão Diária)
# ==========================================
with st.sidebar:
    st.header("Opções da Sessão")
    st.markdown("Quando terminar de refletir hoje, encerre a sessão.")
    
    if st.button("Encerrar Sessão de Hoje"):
        if len(st.session_state.messages) > 0:
            with st.spinner("Estruturando suas emoções..."):
                try:
                    analyst = AnalysisAgent()
                    resultado = analyst.analyze_conversation(st.session_state.messages)
                    
                    analysis_db = AnalysisService()
                    analysis_db.save_analysis(st.session_state.conversation_id, resultado)
                    
                    st.success("Sessão salva com sucesso!")
                    st.info(resultado["summary"])
                    st.write("**Tema Principal:**", resultado["main_theme"])
                    st.write("**Intensidade:**", f"{resultado['intensity']}/10")
                    
                    # Limpa a memória para permitir uma nova conversa amanhã
                    st.session_state.pop("conversation_id", None)
                    st.session_state.pop("messages", None)
                    st.rerun() # Recarrega a página limpando o chat
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("A conversa está vazia!")