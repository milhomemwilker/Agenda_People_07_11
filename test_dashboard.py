"""Valida o CRUD sem criar, modificar ou excluir entrevistas reais."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

import agenda_service as service
import dashboard


def evento_teste():
    inicio = datetime.now(service.FUSO).replace(hour=14, minute=0, second=0, microsecond=0)
    return {
        "id": "entrevista-teste", "etag": '"versao-1"', "summary": "Entrevista com Ana",
        "start": {"dateTime": inicio.isoformat()},
        "end": {"dateTime": (inicio + timedelta(hours=1)).isoformat()},
        "attendees": [{"email": "ana@example.com"}, {"email": "rh@example.com", "responseStatus": "accepted"}],
        "hangoutLink": "https://meet.google.com/teste",
        "extendedProperties": {"private": {"vaga": "Analista"}},
    }


class AgendaServiceTest(unittest.TestCase):
    def test_criacao_solicita_meet_e_notifica_convidados(self):
        registro = service.normalizar_evento(evento_teste())
        eventos = Mock()
        eventos.insert.return_value.execute.return_value = evento_teste()
        with patch.object(service, "_eventos", return_value=eventos):
            service.salvar_agendamento("Ana", "ana@example.com", "Analista", registro["inicio"], registro["fim"])
        parametros = eventos.insert.call_args.kwargs
        self.assertEqual(parametros["sendUpdates"], "all")
        self.assertEqual(parametros["conferenceDataVersion"], 1)
        self.assertEqual(parametros["body"]["extendedProperties"]["private"]["vaga"], "Analista")
        self.assertIn("createRequest", parametros["body"]["conferenceData"])

    def test_exclusao_envia_cancelamento_e_protege_versao(self):
        registro = service.normalizar_evento(evento_teste())
        eventos = Mock()
        eventos.delete.return_value.headers = {}
        with patch.object(service, "_eventos", return_value=eventos):
            service.excluir_agendamento(registro)
        self.assertEqual(eventos.delete.call_args.kwargs["eventId"], registro["id"])
        self.assertEqual(eventos.delete.call_args.kwargs["sendUpdates"], "all")
        self.assertEqual(eventos.delete.return_value.headers["If-Match"], '"versao-1"')

    def test_listagem_paginada_exclui_eventos_pessoais(self):
        eventos = Mock()
        eventos.list.return_value.execute.side_effect = [
            {"items": [evento_teste(), {"id": "pessoal", "summary": "Dentista"}], "nextPageToken": "pagina2"},
            {"items": []},
        ]
        inicio = datetime.now(service.FUSO)
        with patch.object(service, "_eventos", return_value=eventos):
            registros = service.listar_agendamentos(inicio, inicio + timedelta(days=30))
        self.assertEqual([r["id"] for r in registros], ["entrevista-teste"])
        self.assertEqual(eventos.list.call_args.kwargs["pageToken"], "pagina2")

    def test_edicao_preserva_outros_participantes_e_protege_versao(self):
        registro = service.normalizar_evento(evento_teste())
        eventos = Mock()
        eventos.patch.return_value.headers = {}
        eventos.patch.return_value.execute.return_value = evento_teste()
        with patch.object(service, "_eventos", return_value=eventos):
            service.salvar_agendamento("Ana", "nova@example.com", "Analista", registro["inicio"], registro["fim"], registro)
        corpo = eventos.patch.call_args.kwargs["body"]
        self.assertEqual(corpo["attendees"][0]["email"], "nova@example.com")
        self.assertEqual(corpo["attendees"][1], evento_teste()["attendees"][1])
        self.assertEqual(eventos.patch.return_value.headers["If-Match"], '"versao-1"')
        eventos.insert.assert_not_called()

    def test_horario_invalido_nao_acessa_google(self):
        inicio = datetime.now(service.FUSO)
        with patch.object(service, "_eventos") as conectar:
            with self.assertRaises(ValueError):
                service.salvar_agendamento("Ana", "ana@example.com", "Analista", inicio, inicio)
            conectar.assert_not_called()


class DashboardTest(unittest.TestCase):
    def test_carregar_filtrar_editar_e_excluir_com_confirmacao(self):
        registro = service.normalizar_evento(evento_teste())
        with patch.object(dashboard, "listar_agendamentos", return_value=[registro]), \
             patch.object(dashboard, "salvar_agendamento", return_value=registro) as salvar, \
             patch.object(dashboard, "excluir_agendamento") as excluir:
            app = AppTest.from_file("main.py").run(timeout=30)
            self.assertFalse(app.exception)
            app.button(key="carregar_agenda").click().run()
            self.assertEqual(app.metric[0].value, "1")
            app.text_input(key="busca_agenda").input("inexistente").run()
            self.assertEqual(app.metric[0].value, "0")
            app.text_input(key="busca_agenda").input("").run()
            app.text_input(key="nome_entrevista-teste").input("Ana Silva")
            app.button(key="salvar_entrevista-teste").click().run()
            self.assertEqual(salvar.call_args.args[0], "Ana Silva")
            self.assertTrue(app.button(key="excluir_entrevista-teste").disabled)
            excluir.assert_not_called()
            app.checkbox(key="confirmar_entrevista-teste").check().run()
            app.button(key="excluir_entrevista-teste").click().run()
            excluir.assert_called_once()
            self.assertEqual(app.metric[0].value, "0")
            self.assertFalse(app.exception)

    def test_adicionar_e_mostrar_falha_sem_apagar_lista(self):
        registro = service.normalizar_evento(evento_teste())
        with patch.object(dashboard, "salvar_agendamento", return_value=registro) as salvar, \
             patch.object(dashboard, "listar_agendamentos", side_effect=RuntimeError("offline")):
            app = AppTest.from_file("main.py").run(timeout=30)
            app.text_input(key="nome_novo").input("Ana")
            app.text_input(key="email_novo").input("ana@example.com")
            app.text_input(key="vaga_novo").input("Analista")
            app.button(key="salvar_novo").click().run()
            salvar.assert_called_once()
            self.assertEqual(app.metric[0].value, "1")
            app.button(key="carregar_agenda").click().run()
            self.assertEqual(app.metric[0].value, "1")
            self.assertTrue(app.error)
            self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
