"""Monta a interface Streamlit da Central de Recrutamento."""

import os  # Verifica se os arquivos de configuração estão disponíveis.
from pathlib import Path  # Encontra o CSS ao lado deste arquivo.

from ui_helpers import legenda
import streamlit as st  # Componentes visuais e estado da página.
from dashboard import render_dashboard

# Importamos o modelo, o ID da planilha e a função que processa pedidos.
from agent import MODELO_GROQ, PLANILHA_ID, executar_agente_rh

# Configuramos o título, ícone e largura da aplicação.
st.set_page_config(
    page_title="Central de Recrutamento",
    page_icon="\U0001F4BC",
    layout="wide"
)

# O CSS separado define cores, espaçamentos, cartões e botões.
css_path = Path(__file__).with_name("styles.css")
css = css_path.read_text(encoding="utf-8")
st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)

# Estes indicadores mostram se as configurações principais estão presentes.
groq_configurado = bool(os.environ.get("GROQ_API_KEY"))
google_configurado = os.path.exists("credentials.json")
planilha_configurada = bool(PLANILHA_ID)

# A barra lateral resume o nome do sistema, integrações e modelo utilizado.
with st.sidebar:
    st.markdown('<div class="brand-mark">TALENT WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown("## Central de RH")
    legenda("Assistente de recrutamento")
    pagina = st.radio("Navegação", ["Agendamentos", "Assistente"], key="pagina", help="Agendamentos: consulte e gerencie entrevistas por formulário. Assistente: descreva em texto um pedido de agendamento ou cadastro.")
    legenda("Agendamentos: visualizar, adicionar, editar e excluir. Assistente: enviar pedidos em texto e registrar candidatos na planilha.")
    st.divider()

    st.markdown("#### Integrações")
    # Cada par associa o nome de uma integração à sua configuração.
    for label, configurado in (
        ("Assistente de IA", groq_configurado),
        ("Google Workspace", google_configurado),
        ("Planilha de candidatos", planilha_configurada),
    ):
        # A classe CSS muda a cor do indicador conforme o estado.
        estado = "Configurado" if configurado else "Verificar configuração"
        classe = "ok" if configurado else "off"
        st.markdown(
            f'<div class="status-line"><span class="status-dot {classe}"></span>'
            f'<span>{label}</span></div>',
            unsafe_allow_html=True
        )
        if not configurado:
            legenda(estado, cor="amarelo")
    legenda("Verde: configuração encontrada.", cor="verde")
    legenda("Amarelo: configuração pendente.", cor="amarelo")
    legenda("A conexão é verificada ao usar o serviço.")

    st.divider()
    legenda("Modelo de IA")
    st.code(MODELO_GROQ, language=None)
    legenda("O assistente usa este modelo pela Groq Cloud para interpretar seus pedidos.")

if pagina == "Agendamentos":
    render_dashboard()
    st.stop()

# A área principal apresenta o propósito da aplicação.
st.markdown('<div class="eyebrow">OPERAÇÕES DE TALENT ACQUISITION</div>', unsafe_allow_html=True)
st.title("Gestão de recrutamento")
st.markdown(
    '<div class="page-subtitle">Agende entrevistas e mantenha os dados dos candidatos '
    'organizados em um único fluxo.</div>',
    unsafe_allow_html=True
)

# Os dois cartões explicam o que o Calendar e a planilha fazem.
st.markdown("### Integrações disponíveis")
col_calendar, col_sheets = st.columns(2)
with col_calendar:
    with st.container(border=True):
        st.markdown('<div class="integration-title">Agenda e entrevistas</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="integration-copy">Crie convites de entrevista no Google Calendar '
            'com link do Google Meet.</div>',
            unsafe_allow_html=True
        )
with col_sheets:
    with st.container(border=True):
        st.markdown('<div class="integration-title">Gestão de candidatos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="integration-copy">Registre candidatos, vagas e status diretamente '
            'na planilha conectada.</div>',
            unsafe_allow_html=True
        )

# O formulário aceita pedidos de agendamento, cadastro ou ambos.
st.markdown("### Nova solicitação")
st.markdown(
    "Descreva as ações desejadas e inclua os dados do candidato, a vaga e os horários "
    "quando aplicável. Ao agendar uma entrevista, o candidato também é registrado "
    "automaticamente na planilha."
)
with st.expander("O que posso pedir ao assistente?"):
    st.markdown(
        "- **Agendar uma entrevista:** informe nome, e-mail, vaga, data e horários de início e término. O pedido cria o convite e registra o candidato na planilha.\n"
        "- **Cadastrar um candidato:** informe nome, e-mail e vaga. Você também pode indicar o status, como ‘Em análise’.\n"
        "- **Editar ou excluir uma entrevista:** abra Agendamentos no menu lateral e selecione a entrevista."
    )
    legenda("Confira os dados antes de enviar. Ao processar um pedido completo, o assistente pode executar as ações e enviar convites aos participantes.", cor="amarelo")

# O formulário só envia o texto quando o botão é pressionado.
with st.form("solicitacao_recrutamento"):
    prompt_usuario = st.text_area(
        "Instruções",
        key="prompt_input",
        height=150,
        help="Escreva em linguagem natural. Se faltarem dados necessários, o assistente poderá pedi-los na resposta.",
        placeholder=(
            "Ex.: Agende uma entrevista com Ana Silva, ana@empresa.com, em 10/11/2026, "
            "das 14h às 15h (horário de Brasília), para a vaga de Analista Financeiro, e registre "
            "o candidato na planilha."
        )
    )
    submitted = st.form_submit_button(
        "Processar solicitação",
        type="primary",
        width="stretch",
        key="processar_solicitacao"
    )

# A variável submitted informa se o usuário enviou o formulário.
if submitted:
    if not prompt_usuario.strip():
        # Um pedido vazio não chama o modelo nem os serviços Google.
        st.session_state.pop("resultado_processamento", None)
        st.warning("Escreva uma instrução antes de continuar.")
    else:
        # A função do agente retorna resultados ou erros para serem exibidos.
        with st.spinner("Processando a solicitação..."):
            try:
                st.session_state.resultado_processamento = executar_agente_rh(prompt_usuario)
            except Exception as erro:
                st.session_state.resultado_processamento = [
                    ("erro", f"Não foi possível concluir a solicitação: {erro}")
                ]

# O resultado fica na sessão para continuar visível após a atualização da tela.
if "resultado_processamento" in st.session_state:
    st.markdown("### Resultado da solicitação")
    legenda("Confira o retorno de cada serviço. Se o convite foi criado e apenas o cadastro falhou, solicite somente o cadastro para evitar uma entrevista duplicada.")
    resultado = st.session_state.resultado_processamento
    # ERRO PROTEGIDO: algumas falhas podem devolver None.
    # CORREÇÃO: o aviso impede a interface de tentar percorrer
    # um resultado inexistente e orienta o usuário a tentar novamente.
    if resultado is None:
        st.warning("Não há resultado disponível. Envie a solicitação novamente.")
    for tipo, conteudo in resultado or []:
        if tipo == "calendar":
            st.success(f"**Google Calendar e Meet**  \n{conteudo}")
        elif tipo == "sheets":
            st.success(f"**Google Sheets**  \n{conteudo}")
        elif tipo == "texto":
            st.info(conteudo)
        elif tipo == "erro":
            st.error(conteudo)

