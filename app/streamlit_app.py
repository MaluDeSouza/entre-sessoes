import streamlit as st
import os
from agents.journal_agent import JournalAgent
from services.gemini_service import GeminiService
from services.conversation_service import ConversationService
from agents.analysis_agent import AnalysisAgent
from services.analysis_service import AnalysisService

# NOVAS IMPORTAÇÕES PARA O RESUMO SEMANAL
from agents.summary_agent import SummaryAgent
from services.summary_service import SummaryService
from services.dashboard_service import DashboardService
from services.insight_service import InsightService

st.set_page_config(page_title="Entre Sessões", page_icon="🫧")
st.title("🫧 Entre Sessões")
st.markdown("""
Sua memória emocional entre sessões de terapia.
Nem tudo que acontece durante a semana chega à terapia. Registre seus pensamentos antes que eles sejam esquecidos.
""")

# Criação das Abas
aba_diario, aba_resumo, aba_dashboard, aba_padroes = st.tabs([
    "💬 Meu Diário", 
    "📊 Resumo Semanal", 
    "📈 Dashboard", 
    "🧠 Meus Padrões"
])

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

    # ==========================================
    # ENTRADA DE ÁUDIO (Versão 2.0)
    # ==========================================
    if "audio_processado" not in st.session_state:
        st.session_state.audio_processado = False
        
    audio_value = st.audio_input("Ou grave um áudio de desabafo:")
    
    if audio_value and not st.session_state.audio_processado:
        # 1. Cria a pasta temp e salva o arquivo de áudio fisicamente
        os.makedirs("temp", exist_ok=True)
        audio_path = "temp/user_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(audio_value.getbuffer())
        
        # 2. Exibe o envio no chat visual e salva no banco de dados (ConversationService)
        audio_marker = "🎤 [Áudio enviado pelo usuário]"
        st.session_state.messages.append({"role": "user", "content": audio_marker})
        with st.chat_message("user"):
            st.markdown(audio_marker)
            
        db_service.save_message(st.session_state.conversation_id, "user", audio_marker)

        # 3. Chama o Agente passando o caminho do arquivo de áudio!
        with st.chat_message("assistant"):
            with st.spinner("Ouvindo seu áudio atentamente..."):
                response = journal.generate(st.session_state.messages, audio_path=audio_path)
                st.markdown(response)
                
        # 4. Salva a resposta do assistente no banco
        st.session_state.messages.append({"role": "assistant", "content": response})
        db_service.save_message(st.session_state.conversation_id, "assistant", response)
        
        # Dá um pequeno refresh na interface para limpar o gravador
        st.session_state.audio_processado = True
        st.rerun()

    # ==========================================
    # ENTRADA DE TEXTO (Mantemos o fluxo original)
    # ==========================================
    if prompt := st.chat_input("O que aconteceu hoje?"):
        # (Seu código original de input de texto continua aqui exatamente igual)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        db_service.save_message(st.session_state.conversation_id, "user", prompt)

        with st.chat_message("assistant"):
            with st.spinner("Digitando..."):
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
# ABA 3: DASHBOARD & TIMELINE (Copie e cole isso abaixo da aba_resumo)
# ==========================================
with aba_dashboard:
    st.header("📈 Seu Painel Emocional")
    st.markdown("Visualize a variação das suas emoções e acompanhe o histórico das suas reflexões.")

    # Instancia o serviço que acabou de funcionar no nosso teste
    dashboard_service = DashboardService()

    # --- PARTE 1: DASHBOARD (Versão 0.4) ---
    st.subheader("Análise Gráfica")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Evolução da Intensidade Média**")
        df_intensity = dashboard_service.get_intensity_timeline()
        if not df_intensity.empty:
            # Uma única linha desenha o gráfico de linha!
            st.line_chart(df_intensity)
        else:
            st.info("Ainda não há dados suficientes de intensidade.")

    with col2:
        st.markdown("**Emoções Mais Frequentes**")
        df_emotions = dashboard_service.get_emotions_frequency()
        if not df_emotions.empty:
            # Uma única linha desenha o gráfico de barras!
            st.bar_chart(df_emotions)
        else:
            st.info("Ainda não há dados suficientes de emoções.")

    st.divider()

    # --- PARTE 2: TIMELINE FEED (Versão 0.5) ---
    st.header("⏳ Timeline de Reflexões")
    st.markdown("Seu histórico de sessões em ordem cronológica (das mais recentes para as mais antigas).")

    feed = dashboard_service.get_timeline_feed()

    if not feed:
        st.info("Nenhuma reflexão encontrada na timeline.")
    else:
        for item in feed:
            # Cria um "card" visual para cada sessão da linha do tempo
            with st.container(border=True):
                st.caption(f"🗓️ {item['date']} | 🏷️ Tema: **{item['theme']}** | ⚡ Intensidade: {item['intensity']}/10")
                st.write(item['summary'])

# ==========================================
# ABA 4: MEUS PADRÕES (Insights - Versão 1.0)
# ==========================================
with aba_padroes:
    st.header("🧠 Padrões e Insights Profundos")
    st.markdown("Deixe a IA analisar seu último mês e revelar conexões invisíveis entre suas emoções e acontecimentos. Ideal para levar à terapia.")

    # Usamos o botão para acionar o serviço
    if st.button("Descobrir Meus Padrões (Últimos 30 dias)", type="primary"):
        with st.spinner("Analisando semanas de conversas em busca de padrões..."):
            try:
                insight_service = InsightService()
                resultado = insight_service.generate_and_save_insights(user_id=1, days=30)

                if not resultado:
                    st.info("Ainda não há reflexões suficientes nos últimos 30 dias para gerar insights profundos.")
                else:
                    st.success("Padrões comportamentais mapeados com sucesso!")
                    
                    # Exibe cada insight em um cartão estilizado
                    for item in resultado["insights"]:
                        with st.container(border=True):
                            st.subheader(f"💡 {item['title']}")
                            st.write(item['description'])
                    
                    st.divider()
                    st.write(f"*{resultado['closing_message']}*")

            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar os insights: {e}")
                
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