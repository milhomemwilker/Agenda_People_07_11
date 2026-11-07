"""Dashboard de entrevistas com filtros e formulários de manutenção."""

from datetime import datetime, time, timedelta

import pandas as pd
from ui_helpers import legenda
import streamlit as st
from googleapiclient.errors import HttpError

from agenda_service import FUSO, excluir_agendamento, listar_agendamentos, salvar_agendamento


def mensagem_erro(erro):
    if isinstance(erro, HttpError):
        if erro.resp.status == 412:
            return "Este agendamento foi alterado. Atualize a lista antes de tentar novamente."
        if erro.resp.status in (404, 410):
            return "O evento não está mais disponível. Atualize a lista."
        if erro.resp.status in (401, 403):
            return "Verifique a autorização da conta Google e a permissão para gerenciar o calendário."
        return "Não foi possível acessar o Google Calendar. Tente novamente."
    if isinstance(erro, ValueError):
        return str(erro)
    return "Não foi possível concluir a operação. Verifique a conexão e a autorização do Google."


def formulario_agendamento(agendamento=None):
    chave = agendamento["id"] if agendamento else "novo"
    inicio = agendamento["inicio"] if agendamento else datetime.combine(
        datetime.now(FUSO).date() + timedelta(days=1), time(9), FUSO
    )
    fim = agendamento["fim"] if agendamento else inicio + timedelta(hours=1)
    legenda("Preencha todos os campos. Confira o e-mail e os horários antes de salvar.")
    with st.form(f"form_agenda_{chave}"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do candidato", value=agendamento["nome"] if agendamento else "", key=f"nome_{chave}", placeholder="Ex.: Ana Silva", help="Nome que aparecerá no título do convite da entrevista.")
        email = col2.text_input("E-mail do candidato", value=agendamento["email"] if agendamento else "", key=f"email_{chave}", placeholder="Ex.: ana@empresa.com", help="Endereço que receberá o convite. Ao alterá-lo, o novo endereço passa a ser o destinatário do candidato.")
        vaga = st.text_input("Vaga", value=agendamento["vaga"] if agendamento else "", key=f"vaga_{chave}", placeholder="Ex.: Analista Financeiro", help="Cargo para o qual o candidato será entrevistado. Em entrevistas antigas, pode ser necessário preencher esse dado.")
        col1, col2 = st.columns(2)
        dia_inicio = col1.date_input("Data de início", value=inicio.date(), format="DD/MM/YYYY", key=f"dia_inicio_{chave}", help="Dia em que a entrevista começa. Use o calendário para escolher a data.")
        hora_inicio = col1.time_input("Hora de início", value=inicio.time(), key=f"hora_inicio_{chave}", help="Horário de Brasília, no formato de 24 horas. Ex.: 14:00 para duas da tarde.")
        dia_fim = col2.date_input("Data de término", value=fim.date(), format="DD/MM/YYYY", key=f"dia_fim_{chave}", help="Normalmente é o mesmo dia do início. Altere se a entrevista terminar em outro dia.")
        hora_fim = col2.time_input("Hora de término", value=fim.time(), key=f"hora_fim_{chave}", help="O término deve ser posterior ao início. Ex.: início às 14:00 e término às 15:00.")
        legenda("Horários de Brasília (America/Sao_Paulo). Os participantes recebem os convites e as alterações por e-mail.")
        enviado = st.form_submit_button(
            "Salvar alterações" if agendamento else "Adicionar agendamento",
            type="primary", key=f"salvar_{chave}", width="stretch",
        )
    if enviado:
        try:
            with st.spinner("Salvando no Google Calendar..."):
                salvo = salvar_agendamento(
                    nome, email, vaga,
                    datetime.combine(dia_inicio, hora_inicio, FUSO),
                    datetime.combine(dia_fim, hora_fim, FUSO), agendamento,
                )
            # Atualiza a cópia da sessão somente depois da confirmação da API.
            registros = st.session_state.get("agendamentos", [])
            st.session_state.agendamentos = sorted(
                [r for r in registros if r["id"] != salvo["id"]] + [salvo], key=lambda r: r["inicio"]
            )
            st.session_state.aviso_agenda = (
                "Alterações salvas no Google Calendar. A atualização foi solicitada aos participantes."
                if agendamento else
                "Entrevista criada no Google Calendar. O envio do convite foi solicitado; o link do Meet pode levar alguns instantes para aparecer."
            )
            st.rerun()
        except Exception as erro:
            st.error(mensagem_erro(erro))


def render_dashboard():
    st.title("Dashboard de agendamentos")
    legenda("Gerencie as entrevistas do calendário principal da conta Google conectada.")
    legenda("O painel altera o Google Calendar. Os cadastros de candidatos no Google Sheets são mantidos pelo assistente.", cor="amarelo")
    with st.expander("Como usar este painel"):
        st.markdown(
            "1. Escolha o período e clique em **Atualizar agendamentos** para buscar as entrevistas.\n"
            "2. Use a busca para encontrar um candidato, e-mail ou vaga.\n"
            "3. Abra **Adicionar entrevista** para criar um convite ou **Editar ou excluir** para gerenciar uma entrevista existente."
        )
        legenda("A lista mostra entrevistas identificadas pelo sistema no calendário principal. Os demais compromissos não aparecem aqui.")
    if "aviso_agenda" in st.session_state:
        st.success(st.session_state.pop("aviso_agenda"))

    hoje = datetime.now(FUSO).date()
    st.subheader("Consultar entrevistas")
    legenda("As duas datas estão incluídas na consulta. Após mudar o período, clique em Atualizar agendamentos para buscar os dados do Google.")
    col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
    de = col1.date_input("Data inicial da consulta", value=hoje - timedelta(days=30), format="DD/MM/YYYY", key="filtro_de", help="Mostra entrevistas com início a partir desta data.")
    ate = col2.date_input("Data final da consulta", value=hoje + timedelta(days=60), format="DD/MM/YYYY", key="filtro_ate", help="Inclui as entrevistas que começam neste dia, até o fim do dia.")
    carregar = col3.button("Atualizar agendamentos", key="carregar_agenda", width="stretch", type="primary", help="Busca a versão mais recente da agenda no Google. Na primeira conexão, poderá ser necessário autorizar o acesso no navegador.")
    periodo = (de.isoformat(), ate.isoformat())
    valido = de <= ate
    if not valido:
        st.warning("A data final do filtro deve ser igual ou posterior à inicial.")
    if carregar and valido:
        try:
            with st.spinner("Buscando entrevistas no Google Calendar..."):
                registros = listar_agendamentos(
                    datetime.combine(de, time.min, FUSO), datetime.combine(ate + timedelta(days=1), time.min, FUSO)
                )
            st.session_state.agendamentos = registros
            st.session_state.periodo_agenda = periodo
            st.session_state.atualizado_agenda = datetime.now(FUSO).strftime("%d/%m/%Y às %H:%M")
        except Exception as erro:
            st.error(mensagem_erro(erro))

    registros = st.session_state.get("agendamentos", [])
    if st.session_state.get("periodo_agenda") and st.session_state.periodo_agenda != periodo:
        st.info("O período foi alterado. Clique em Atualizar agendamentos para consultar o novo intervalo.")
    registros = [r for r in registros if de <= r["inicio"].date() <= ate] if valido else []
    busca = st.text_input("Buscar candidato, e-mail ou vaga", key="busca_agenda", placeholder="Ex.: Ana, ana@empresa.com ou Analista", help="Filtra as entrevistas já carregadas. Pressione Enter ou saia do campo para aplicar. Apague o texto para mostrar todas novamente.")
    if busca.strip():
        termo = busca.strip().casefold()
        registros = [r for r in registros if termo in " ".join([r["nome"], r["email"], r["vaga"]]).casefold()]
    with st.container(horizontal=True):
        st.metric("Entrevistas no filtro", len(registros), border=True, help="Total de entrevistas que correspondem ao período e ao texto da busca.")
        st.metric("Hoje", sum(r["inicio"].date() == hoje for r in registros), border=True, help="Entrevistas do resultado atual que começam hoje, no horário de Brasília.")
        st.metric("Próximas", sum(r["inicio"] >= datetime.now(FUSO) for r in registros), border=True, help="Entrevistas do resultado atual cujo horário de início ainda não chegou.")
        st.metric("Com Google Meet", sum(bool(r["meet"]) for r in registros), border=True, help="Entrevistas do resultado atual que já possuem um link de reunião disponível.")
    legenda("Os quatro indicadores e o gráfico acompanham o período e a busca selecionados.")

    if "agendamentos" not in st.session_state:
        st.info("Clique em Atualizar agendamentos para conectar ao Google e visualizar as entrevistas.")
    elif not registros:
        st.info("Nenhuma entrevista encontrada. Limpe a busca ou amplie o período e clique em Atualizar agendamentos. Você também pode criar uma entrevista na aba Adicionar entrevista.")
    if st.session_state.get("atualizado_agenda"):
        legenda("Última consulta: " + st.session_state.atualizado_agenda)

    if registros:
        st.subheader("Entrevistas encontradas")
        legenda("Cada linha representa uma entrevista. Para alterar os dados, use a aba Editar ou excluir abaixo. Datas e horários seguem o horário de Brasília.")
        tabela = pd.DataFrame([{
            "Candidato": r["nome"], "E-mail": r["email"], "Vaga": r["vaga"] or "Não informada",
            "Início": r["inicio"].strftime("%d/%m/%Y %H:%M"),
            "Término": r["fim"].strftime("%d/%m/%Y %H:%M"),
            "Meet": r["meet"],
        } for r in registros])
        st.dataframe(tabela, hide_index=True, width="stretch", alt="Entrevistas do período filtrado")
        legenda("Vaga ‘Não informada’: dado ausente no evento; preencha ao editar. Meet em branco: link ainda não disponível ou entrevista sem videoconferência.")
        por_dia = pd.DataFrame([{"Data": r["inicio"].date(), "Entrevistas": 1} for r in registros])
        st.subheader("Distribuição por dia")
        legenda("Cada barra mostra quantas entrevistas começam naquele dia dentro do resultado atual.")
        st.bar_chart(por_dia.groupby("Data", as_index=False).sum(), x="Data", y="Entrevistas", alt="Quantidade de entrevistas por dia")

    novo, gerenciar = st.tabs(["Adicionar entrevista", "Editar ou excluir"])
    with novo:
        st.subheader("Novo agendamento")
        legenda("Ao adicionar, será criado um convite no Google Calendar com solicitação de um link do Google Meet.")
        formulario_agendamento()
    with gerenciar:
        if not registros:
            legenda("Carregue a agenda e selecione um período com entrevistas para gerenciar.")
        else:
            por_id = {r["id"]: r for r in registros}
            selecionado = st.selectbox(
                "Selecione a entrevista", options=list(por_id), key="entrevista_selecionada",
                help="Escolha pela data, pelo horário e pelo nome. O formulário abaixo exibirá os dados dessa entrevista.",
                format_func=lambda chave: f"{por_id[chave]['inicio']:%d/%m/%Y %H:%M} · {por_id[chave]['nome']}",
            )
            agendamento = por_id[selecionado]
            legenda("Altere os campos desejados e clique em Salvar alterações. As mudanças só são enviadas ao Google quando você salva.")
            if agendamento["original"].get("recurringEventId"):
                st.info("Esta entrevista é recorrente. As alterações afetam somente a ocorrência selecionada.")
            if agendamento["meet"].startswith("https://"):
                st.link_button("Abrir Google Meet", agendamento["meet"], help="Abre a sala de videoconferência desta entrevista.")
            formulario_agendamento(agendamento)
            with st.expander("Excluir agendamento"):
                st.warning("A entrevista será excluída do calendário e os participantes receberão o cancelamento.")
                legenda(f"Entrevista selecionada: {agendamento['nome']} — {agendamento['inicio']:%d/%m/%Y às %H:%M}. Marque a confirmação para habilitar o botão de exclusão. Esta tela não oferece desfazer.", cor="vermelho")
                confirmar = st.checkbox("Confirmo a exclusão desta entrevista", key=f"confirmar_{selecionado}")
                if st.button("Excluir definitivamente", disabled=not confirmar, key=f"excluir_{selecionado}"):
                    try:
                        excluir_agendamento(agendamento)
                        st.session_state.agendamentos = [r for r in st.session_state.agendamentos if r["id"] != selecionado]
                        st.session_state.aviso_agenda = "Agendamento excluído."
                        st.rerun()
                    except Exception as erro:
                        st.error(mensagem_erro(erro))

