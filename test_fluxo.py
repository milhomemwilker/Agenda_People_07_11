"""Valida o fluxo sem enviar convites ou alterar a planilha real."""
# Converte os dados da entrevista em JSON para simular os argumentos da ferramenta.
import json
# Fornece a estrutura de testes e as verificações de resultados.
import unittest
# Cria objetos simples com atributos, semelhantes às respostas do cliente de IA.
from types import SimpleNamespace
# Mock simula dependências; patch substitui objetos temporariamente durante o teste.
from unittest.mock import Mock, patch

# Importa o módulo que contém o fluxo do agente de recursos humanos.
import agent
# Permite interagir com a aplicação Streamlit em um ambiente de teste.
from streamlit.testing.v1 import AppTest


class FluxoTest(unittest.TestCase):
    # Executa o fluxo com dependências simuladas e permite provocar falha na planilha.
    def executar(self, falha_planilha=False):
        # Dados fictícios usados tanto na chamada simulada quanto nas verificações.
        dados = dict(nome_candidato="Candidato Teste", email_candidato="teste@example.com",
                     vaga="Analista", data_hora_inicio="2026-11-10T14:00:00-03:00",
                     data_hora_fim="2026-11-10T15:00:00-03:00")
        # Representa a ferramenta de agendamento que o modelo solicitou executar.
        chamada = SimpleNamespace(function=SimpleNamespace(
            name="agendar_entrevista_com_meet", arguments=json.dumps(dados)))
        # Simula o cliente de IA e sua resposta contendo uma chamada de ferramenta.
        cliente = Mock()
        cliente.chat.completions.create.return_value = SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[chamada]))])
        # Substitui o cliente, a identificação da planilha e as integrações externas.
        # Assim, o teste não cria convites nem grava dados na planilha real.
        # As substituições são desfeitas automaticamente ao sair deste bloco.
        with patch.object(agent, "client", cliente), patch.object(agent, "ID_PLANILHA", "planilha-teste"), \
             patch.object(agent, "agendar_entrevista_com_meet", return_value="https://meet.google.com/teste") as agenda, \
             patch.object(agent, "registrar_candidato_na_planilha") as planilha:
            # Quando solicitado, faz a gravação simulada lançar uma exceção.
            if falha_planilha:
                planilha.side_effect = RuntimeError("Falha simulada")
            # Executa o fluxo real do agente utilizando as dependências simuladas.
            resultado = agent.executar_agente_rh("Agende a entrevista")
            # Confirma que o agendamento foi chamado exatamente uma vez.
            agenda.assert_called_once()
            # Confirma uma única tentativa de cadastro com os dados esperados.
            planilha.assert_called_once_with(
                "planilha-teste", dados["nome_candidato"], dados["email_candidato"],
                "Analista", "Entrevista agendada", dados["data_hora_inicio"], dados["data_hora_fim"])
            # Devolve os resultados para as verificações específicas de cada cenário.
            return resultado

    def test_agendamento_e_cadastro(self):
        # Ignora o conteúdo de cada resultado e verifica seus tipos e sua ordem.
        # O fluxo completo deve retornar primeiro o calendário e depois a planilha.
        self.assertEqual([tipo for tipo, _ in self.executar()], ["calendar", "sheets"])

    def test_falha_parcial_preserva_convite(self):
        # Uma falha na planilha deve preservar o resultado do convite já criado
        # e acrescentar um resultado de erro em seguida.
        self.assertEqual([tipo for tipo, _ in self.executar(True)], ["calendar", "erro"])

    def test_formulario_exibe_resultados(self):
        # Simula a resposta do agente para testar apenas a interação com a interface.
        with patch.object(agent, "executar_agente_rh", return_value=[
            ("calendar", "https://meet.google.com/teste"), ("sheets", "Cadastro simulado")]) as executar:
            # Carrega a aplicação e executa sua renderização inicial.
            app = AppTest.from_file("main.py").run()
            # Preenche a primeira área de texto com uma solicitação fictícia.
            app.text_area[0].input("Solicitacao de teste")
            # Clica no primeiro botão e executa novamente a aplicação.
            app.button[0].click().run()
            # Verifica que a interface não apresentou exceções.
            self.assertFalse(app.exception)
            # Espera uma mensagem de sucesso para cada um dos dois resultados.
            self.assertEqual(len(app.success), 2)
            # Confirma que o formulário enviou o texto ao agente uma única vez.
            executar.assert_called_once_with("Solicitacao de teste")


if __name__ == "__main__":
    # Inicia os testes quando este arquivo é executado diretamente pelo Python.
    unittest.main()
