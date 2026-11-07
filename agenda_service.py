"""Operações do dashboard no calendário principal da conta Google conectada."""

import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from google_tools import autenticar_google

FUSO = ZoneInfo("America/Sao_Paulo")
PREFIXO = "Entrevista com "


def _eventos():
    return build("calendar", "v3", credentials=autenticar_google()).events()


def _entrevista(evento):
    return evento.get("summary", "").startswith(PREFIXO) or (
        evento.get("extendedProperties", {}).get("private", {}).get("people_entrevista") == "1"
    )


def normalizar_evento(evento):
    """Mantém o evento original para preservar participantes e detectar alterações."""
    dados = evento.get("extendedProperties", {}).get("private", {})
    convidados = [p for p in evento.get("attendees", []) if not p.get("self") and not p.get("resource")]
    return {
        "id": evento["id"],
        "nome": dados.get("nome_candidato") or evento.get("summary", "").removeprefix(PREFIXO),
        "email": dados.get("email_candidato") or (convidados[0].get("email", "") if convidados else ""),
        "vaga": dados.get("vaga", ""),
        "inicio": datetime.fromisoformat(evento["start"]["dateTime"].replace("Z", "+00:00")).astimezone(FUSO),
        "fim": datetime.fromisoformat(evento["end"]["dateTime"].replace("Z", "+00:00")).astimezone(FUSO),
        "meet": evento.get("hangoutLink", ""),
        "url": evento.get("htmlLink", ""),
        "original": evento,
    }


def listar_agendamentos(inicio, fim):
    """Lista todas as páginas do período; eventos pessoais não entram no painel."""
    eventos = _eventos()
    pagina = None
    resultado = []
    while True:
        resposta = eventos.list(
            calendarId="primary", timeMin=inicio.isoformat(), timeMax=fim.isoformat(),
            singleEvents=True, orderBy="startTime", showDeleted=False,
            maxResults=250, pageToken=pagina,
        ).execute()
        for evento in resposta.get("items", []):
            if _entrevista(evento) and "dateTime" in evento.get("start", {}) and "dateTime" in evento.get("end", {}):
                resultado.append(normalizar_evento(evento))
        pagina = resposta.get("nextPageToken")
        if not pagina:
            return resultado


def validar_dados(nome, email, vaga, inicio, fim):
    if not nome.strip() or not vaga.strip():
        raise ValueError("Informe o nome do candidato e a vaga.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()):
        raise ValueError("Informe um e-mail válido.")
    if inicio.tzinfo is None or fim.tzinfo is None or fim <= inicio:
        raise ValueError("O término deve ser posterior ao início, com fuso horário definido.")


def salvar_agendamento(nome, email, vaga, inicio, fim, agendamento=None):
    """Cria ou edita um evento e notifica seus participantes pelo Google Calendar."""
    validar_dados(nome, email, vaga, inicio, fim)
    if agendamento and not _entrevista(agendamento["original"]):
        raise ValueError("O evento selecionado não é uma entrevista gerenciada pelo painel.")
    nome, email, vaga = nome.strip(), email.strip(), vaga.strip()
    eventos = _eventos()
    original = agendamento["original"] if agendamento else {}
    privados = dict(original.get("extendedProperties", {}).get("private", {}))
    privados.update(people_entrevista="1", nome_candidato=nome, email_candidato=email, vaga=vaga)
    participantes = [dict(p) for p in original.get("attendees", [])]
    if agendamento:
        for participante in participantes:
            if participante.get("email", "").lower() == agendamento["email"].lower():
                if participante.get("email", "").lower() != email.lower():
                    participante["email"] = email
                    participante["responseStatus"] = "needsAction"
                break
        else:
            participantes.append({"email": email})
    else:
        participantes = [{"email": email}]
    corpo = {
        "summary": PREFIXO + nome,
        "start": {"dateTime": inicio.isoformat(), "timeZone": str(FUSO)},
        "end": {"dateTime": fim.isoformat(), "timeZone": str(FUSO)},
        "attendees": participantes,
        "extendedProperties": {**original.get("extendedProperties", {}), "private": privados},
    }
    if agendamento:
        requisicao = eventos.patch(calendarId="primary", eventId=agendamento["id"], body=corpo, sendUpdates="all")
        # Impede sobrescrever uma alteração feita depois que a lista foi carregada.
        if original.get("etag"):
            requisicao.headers["If-Match"] = original["etag"]
    else:
        corpo["description"] = "Entrevista de alinhamento com o time da People."
        corpo["conferenceData"] = {"createRequest": {
            "requestId": str(uuid.uuid4()), "conferenceSolutionKey": {"type": "hangoutsMeet"},
        }}
        requisicao = eventos.insert(calendarId="primary", body=corpo, conferenceDataVersion=1, sendUpdates="all")
    return normalizar_evento(requisicao.execute())


def excluir_agendamento(agendamento):
    """Exclui apenas a ocorrência selecionada e envia o cancelamento aos convidados."""
    if not _entrevista(agendamento["original"]):
        raise ValueError("O evento selecionado não é uma entrevista gerenciada pelo painel.")
    requisicao = _eventos().delete(calendarId="primary", eventId=agendamento["id"], sendUpdates="all")
    if agendamento["original"].get("etag"):
        requisicao.headers["If-Match"] = agendamento["original"]["etag"]
    requisicao.execute()
