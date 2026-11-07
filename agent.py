
"""
AGENTE DE RECRUTAMENTO - RECURSOS HUMANOS (RH)

Objetivo:
Interpretar solicitações dos usuários utilizando inteligência
artificial e disponibilizar ferramentas para operações no Google.

Serviços previstos:
1. Google Calendar: agendamento de entrevistas.
2. Google Meet: geração de links para entrevistas.
3. Google Sheets: registro de candidatos.

IMPORTANTE:
Esta versão executa as chamadas de agendamento de entrevistas.
O registro de candidatos ainda precisa ser tratado na execução.
"""

# ============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================

# Biblioteca nativa do Python utilizada para acessar
# informações e variáveis de ambiente do sistema operacional.
import os
import json

# Biblioteca nativa que permite trabalhar com caracteres
# Unicode, incluindo a remoção de acentos.
import unicodedata

# Importa a função que lê as variáveis definidas no arquivo .env.
# Isso evita escrever chaves de API diretamente no código.
from dotenv import load_dotenv

# Importa o cliente OpenAI.
#
# Apesar do nome OpenAI, este cliente também pode se comunicar
# com serviços que oferecem APIs compatíveis, como a Groq.
from openai import OpenAI

# Importa três funções definidas no arquivo google_tools.py.
#
# autenticar_google:
# Realiza a autenticação nos serviços Google.
#
# agendar_entrevista_com_meet:
# Agenda uma entrevista e solicita um link do Google Meet.
#
# registrar_candidato_na_planilha:
# Registra os dados do candidato no Google Sheets.
#
# ATENÇÃO:
# A importação disponibiliza as funções, mas não as executa.
from google_tools import (
    autenticar_google,
    agendar_entrevista_com_meet,
    registrar_candidato_na_planilha
)


# ============================================================
# 2. CONFIGURAÇÃO DAS VARIÁVEIS DE AMBIENTE
# ============================================================

# Lê o arquivo .env e disponibiliza suas configurações
# por meio das variáveis de ambiente do programa.
#
# Exemplo de conteúdo do arquivo .env:
#
# GROQ_API_KEY=sua_chave_aqui
# PLANILHA_ID=identificador_da_planilha
#
# O arquivo .env não deve ser publicado no GitHub.
load_dotenv()

# Busca a chave de acesso à API da Groq.
#
# os.getenv():
# Retorna o valor da variável informada.
#
# Se GROQ_API_KEY não existir, o resultado será None.
groq_api_key = os.getenv("GROQ_API_KEY")


# ============================================================
# 3. CONFIGURAÇÃO DO CLIENTE DE INTELIGÊNCIA ARTIFICIAL
# ============================================================

# Cria o cliente responsável pela comunicação com a Groq.
#
# api_key:
# Chave utilizada para autenticar as requisições.
#
# base_url:
# Endereço do servidor que receberá as solicitações.
#
# A Groq oferece uma interface compatível com a API OpenAI.
#
# EXPRESSÃO CONDICIONAL:
# Se groq_api_key possuir um valor, cria o cliente.
# Caso contrário, atribui None à variável client.
#
# Criar o cliente não significa enviar uma mensagem à IA.
client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
) if groq_api_key else None

# Cria outro nome para o mesmo objeto armazenado em client.
#
# Não cria um novo cliente nem uma nova conexão.
# As duas variáveis apontam para a mesma instância.
#
# OBSERVAÇÃO:
# Esta variável não é utilizada no restante do código.
openai = client


# ============================================================
# 4. CONFIGURAÇÃO DO MODELO E DA PLANILHA
# ============================================================

# Define qual modelo de inteligência artificial será utilizado.
#
# O identificador deve corresponder a um modelo disponibilizado
# pela Groq para a conta utilizada.
MODELO_GROQ = "openai/gpt-oss-20b"

# Recupera o identificador da planilha Google Sheets.
#
# O ID identifica qual planilha receberá os registros.
#
# Exemplo de URL:
# https://docs.google.com/spreadsheets/d/ABC123/edit
#
# Nesse exemplo, o ID seria ABC123.
#
# os.environ.get() funciona de maneira semelhante a os.getenv().
ID_PLANILHA = os.environ.get("PLANILHA_ID")
# ERRO CORRIGIDO: main.py importava PLANILHA_ID, mas o módulo só
# exportava ID_PLANILHA. O alias mantém os dois nomes sincronizados.
PLANILHA_ID = ID_PLANILHA


# ============================================================
# 5. DEFINIÇÃO DAS FERRAMENTAS DO AGENTE
# ============================================================

# FERRAMENTAS é uma lista de dicionários Python.
#
# Cada dicionário descreve uma função que a inteligência
# artificial poderá solicitar durante uma conversa.
#
# IMPORTANTE:
# Descrever uma ferramenta não significa executá-la.
#
# O modelo pode solicitar uma chamada, mas o programa Python
# precisa interpretar essa solicitação e executar a função.
FERRAMENTAS = [

    # --------------------------------------------------------
    # FERRAMENTA 1: AGENDAMENTO DE ENTREVISTAS
    # --------------------------------------------------------

    {
        # Informa que a ferramenta representa uma função.
        "type": "function",

        # Contém os detalhes da função disponibilizada.
        "function": {

            # Nome que a IA utilizará para solicitar a função.
            "name": "agendar_entrevista_com_meet",

            # Descrição da finalidade da ferramenta.
            #
            # A IA utiliza esta informação para decidir
            # quando solicitar a execução da função.
            "description": (
                "Agendar uma entrevista com o candidato "
                "e gerar um link do Google Meet."
            ),

            # Define a estrutura dos argumentos esperados.
            #
            # O formato segue uma estrutura de JSON Schema.
            "parameters": {

                # object significa um objeto com campos nomeados.
                "type": "object",

                # Define os campos aceitos pela ferramenta.
                "properties": {

                    # Primeiro argumento: nome do candidato.
                    "nome_candidato": {
                        "type": "string",
                        "description": "Nome do candidato"
                    },

                    # Segundo argumento: e-mail do candidato.
                    "email_candidato": {
                        "type": "string",
                        "description": "Email do candidato"
                    },

                    # Terceiro argumento: início da entrevista.
                    "data_hora_inicio": {
                        "type": "string",
                        "description": (
                            "Data e hora de início da entrevista "
                            "no formato ISO 8601 "
                            "(ex: '2023-10-01T14:00:00')."
                        )
                    },

                    # Quarto argumento: término da entrevista.
                    "data_hora_fim": {
                        "type": "string",
                        "description": (
                            "Data e hora de término da entrevista "
                            "no formato ISO 8601 "
                            "(ex: '2023-10-01T15:00:00')."
                        )
                    }
                },

                # Lista de campos obrigatórios.
                #
                # A IA deverá fornecer esses quatro campos
                # quando solicitar esta ferramenta.
                "required": [
                    "nome_candidato",
                    "email_candidato",
                    "data_hora_inicio",
                    "data_hora_fim"
                ]
            }
        }
    },

    # --------------------------------------------------------
    # FERRAMENTA 2: REGISTRO DE CANDIDATOS
    # --------------------------------------------------------

    {
        "type": "function",

        "function": {

            # Nome da função responsável pelo registro.
            "name": "registrar_candidato_na_planilha",

            # Explica para a IA quando utilizar a ferramenta.
            "description": (
                "Registrar o nome, email, vaga e status "
                "do candidato na planilha do Google Sheets."
            ),

            # Define os argumentos esperados.
            "parameters": {

                "type": "object",

                "properties": {

                    # Nome do candidato.
                    "nome": {
                        "type": "string",
                        "description": "Nome do candidato"
                    },

                    # E-mail do candidato.
                    "email": {
                        "type": "string",
                        "description": "Email do candidato"
                    },

                    # Vaga à qual o candidato está concorrendo.
                    #
                    # É opcional no esquema apresentado à IA.
                    "vaga": {
                        "type": "string",
                        "description": (
                            "Vaga de interesse do candidato "
                            "(opcional)"
                        )
                    },

                    # Situação do candidato no processo seletivo.
                    #
                    # Exemplos:
                    # - Inscrito
                    # - Em análise
                    # - Entrevista agendada
                    # - Aprovado
                    # - Reprovado
                    "status": {
                        "type": "string",
                        "description": (
                            "Status do candidato no "
                            "processo seletivo (opcional)"
                        )
                    }
                },

                # Somente nome e email são obrigatórios
                # nesta definição da ferramenta.
                #
                # ATENÇÃO:
                # Se a função Python exigir vaga e status,
                # será necessário fornecer valores padrão
                # ou alterar a definição da ferramenta.
                #
                # O ID da planilha também deverá ser
                # informado na execução da função Python.
                "required": ["nome", "email"]
            }
        }
    }
]


# ============================================================
# 6. DEFINIÇÃO DO PROMPT DO AGENTE
# ============================================================

# PROMPT contém as instruções de comportamento da IA.
#
# Essas instruções serão enviadas como mensagem de sistema.
#
# O prompt define:
# - O papel do agente.
# - Quais informações devem ser solicitadas.
# - Quando utilizar as ferramentas.
# - A necessidade de confirmação.
# - O formato desejado das respostas.
#
# IMPORTANTE:
# Instruções no prompt não substituem validações no Python.
PROMPT = (

    # Define a identidade e o objetivo do agente.
    "Você é um assistente virtual especializado em "
    "agendar entrevistas e registrar candidatos. "

    "Siga as instruções abaixo para interagir com "
    "o usuário e executar as ações necessárias.\n\n"

    # \n representa uma quebra de linha.
    # \n\n representa duas quebras de linha.
    "Regras:\n"

    # Solicita informações básicas do candidato.
    "1. Sempre solicite o nome e email do candidato.\n"

    # Define os dados necessários para agendamento.
    "2. Para agendar uma entrevista, peça a data e hora "
    "de início e término no formato ISO 8601.\n"

    # Define os dados utilizados no registro.
    "3. Para registrar um candidato, peça a vaga e "
    "o status do candidato (opcional).\n"

    # Orienta a IA a utilizar as ferramentas disponíveis.
    "4. Use as ferramentas disponíveis para realizar "
    "as ações solicitadas pelo usuário.\n"

    # Orienta a solicitar informações que estiverem faltando.
    "5. Se o usuário fornecer informações incompletas, "
    "solicite os dados faltantes.\n"

    # Define a necessidade de confirmação.
    #
    # ATENÇÃO:
    # Esta regra ainda precisa ser implementada no Python
    # para impedir operações sem autorização do usuário.
    "6. Sempre confirme com o usuário antes de executar "
    "qualquer ação.\n\n"

    # Apresenta as ferramentas ao agente.
    "Ferramentas disponíveis:\n"

    "- agendar_entrevista_com_meet: Agendar uma entrevista "
    "com o candidato e gerar um link do Google Meet.\n"

    "- registrar_candidato_na_planilha: Registrar o nome, "
    "email, vaga e status do candidato na planilha "
    "do Google Sheets.\n\n"

    # Solicita um formato estruturado de resposta.
    #
    # OBSERVAÇÃO:
    # O modelo também possui um mecanismo próprio
    # para solicitar ferramentas (tool_calls).
    #
    # Exigir JSON textual em todas as respostas pode
    # causar conflitos com perguntas normais ao usuário.
    "Formato de resposta:\n"

    "Sempre responda em JSON com os campos 'action' "
    "(nome da ferramenta) e 'parameters' "
    "(argumentos da função). "

    "Exemplo:\n"

    "{\n"

    '  "action": "agendar_entrevista_com_meet",\n'

    '  "parameters": {\n'

    # CORREÇÃO:
    # O código original repetia nome_candidato.
    # A duplicidade foi retirada deste exemplo.
    '      "nome_candidato": "João Silva",\n'

    '      "email_candidato": "joao.silva@example.com",\n'

    '      "data_hora_inicio": "2023-10-01T14:00:00",\n'

    '      "data_hora_fim": "2023-10-01T15:00:00"\n'

    "  }\n"

    "}"
)


# ============================================================
# 7. FUNÇÃO DE NORMALIZAÇÃO DE TEXTO
# ============================================================

def normalizar(texto):
    """
    Normaliza um texto para facilitar comparações.

    Operações:
    1. Decompõe caracteres acentuados.
    2. Remove marcas Unicode combinantes.
    3. Converte o resultado para letras minúsculas.

    Exemplo:
        Entrada:  "AGENDAR ENTREVISTA"
        Saída:    "agendar entrevista"

        Entrada:  "João"
        Saída:    "joao"

    Atenção:
    Esta função não faz tokenização.
    Tokenizar significa dividir um texto em unidades.
    """

    # NFKD decompõe caracteres Unicode.
    #
    # Exemplo conceitual:
    # "ã" pode ser decomposto em:
    # "a" + marca de til.
    sem_acento = unicodedata.normalize("NFKD", texto)

    # Percorre cada caractere do texto decomposto.
    #
    # unicodedata.combining(letra):
    # Identifica marcas Unicode combinantes.
    #
    # not:
    # Inverte a condição.
    #
    # join():
    # Une os caracteres que passaram pelo filtro.
    #
    # lower():
    # Converte letras maiúsculas em minúsculas.
    return "".join(
        letra
        for letra in sem_acento
        if not unicodedata.combining(letra)
    ).lower()


# ============================================================
# 8. FUNÇÃO PRINCIPAL DO AGENTE DE RECRUTAMENTO
# ============================================================

# O agendamento inclui os dados que serão registrados na planilha.
FERRAMENTAS[0]["function"]["parameters"]["properties"].update({
    "vaga": {"type": "string", "description": "Vaga da entrevista"},
    "status": {"type": "string", "description": "Status do candidato; padrão: Entrevista agendada"},
})
FERRAMENTAS[0]["function"]["parameters"]["required"].append("vaga")

PROMPT = (
    "Você é um assistente de recrutamento. Execute apenas as ações solicitadas. "
    "Para agendar, solicite nome, email, vaga e início e fim da entrevista se faltarem. "
    "Use datas ISO 8601 e o fuso America/Sao_Paulo. Não invente dados. "
    "O agendamento já registra automaticamente o candidato na planilha; não chame "
    "a ferramenta de cadastro separadamente para a mesma entrevista. "
    "Para cadastrar sem entrevista, solicite nome, email e vaga; o status padrão é Cadastrado. "
    "Use tool_calls para executar as ferramentas. Quando faltarem dados, responda "
    "em português com uma pergunta clara, sem JSON."
)


def executar_agente_rh(mensagem_usuario):
    """
    Recebe a mensagem do usuário e consulta a IA.

    Parâmetro:
        mensagem_usuario:
            Texto enviado pelo usuário.

    Funcionamento atual:
        1. Verifica se existe um cliente configurado.
        2. Envia a mensagem para o modelo.
        3. Disponibiliza as definições das ferramentas.
        4. Recebe a resposta do modelo.
        5. Identifica possíveis chamadas de ferramentas.
        6. Retorna o conteúdo textual da resposta.

    Limitação:
        As ferramentas solicitadas ainda não são executadas.
    """

    # --------------------------------------------------------
    # ETAPA 1: VERIFICAR A CONFIGURAÇÃO DA API
    # --------------------------------------------------------

    # Verifica se o cliente não foi criado.
    #
    # is None:
    # Testa se a variável possui o valor especial None.
    if client is None:

        # ERRO CORRIGIDO: o retorno anterior não correspondia ao formato
        # esperado pela interface. Agora é retornada uma lista de tuplas
        # ("erro", mensagem), que main.py consegue renderizar corretamente.
        #
        # return encerra imediatamente a função.
        return [("erro", (
                "Configure a chave GROQ_API_KEY "
                "no arquivo .env para usar o agente."
            ))]

    # --------------------------------------------------------
    # ETAPA 2: ENVIAR A SOLICITAÇÃO PARA A IA
    # --------------------------------------------------------

    # Envia uma requisição ao modelo da Groq.
    #
    # Esta é a parte do código que efetivamente
    # se comunica com o serviço de inteligência artificial.
    resposta = client.chat.completions.create(

        # Identifica qual modelo deve processar a mensagem.
        model=MODELO_GROQ,

        # Define as mensagens enviadas ao modelo.
        messages=[

            # Mensagem de sistema:
            # Contém as regras e orientações do agente.
            {
                "role": "system",
                "content": PROMPT
            },

            # Mensagem do usuário:
            # Contém a solicitação que será interpretada.
            {
                "role": "user",
                "content": mensagem_usuario
            }
        ],

        # Envia as definições das ferramentas disponíveis.
        #
        # A IA pode escolher uma ferramenta com base
        # na solicitação do usuário.
        tools=FERRAMENTAS,

        # Permite ao modelo decidir se deseja
        # solicitar uma chamada de ferramenta.
        #
        # auto:
        # O modelo decide se utiliza ou não ferramentas.
        tool_choice="auto"
    )

    # --------------------------------------------------------
    # ETAPA 3: EXTRAIR A MENSAGEM DA RESPOSTA
    # --------------------------------------------------------

    # choices:
    # Lista de respostas geradas pelo modelo.
    #
    # [0]:
    # Seleciona a primeira resposta da lista.
    #
    # message:
    # Objeto que contém o conteúdo textual e
    # eventuais solicitações de ferramentas.
    mensagem = resposta.choices[0].message

    # --------------------------------------------------------
    # ETAPA 4: IDENTIFICAR CHAMADAS DE FERRAMENTAS
    # --------------------------------------------------------

    # tool_calls contém as ferramentas solicitadas pela IA.
    #
    # Se nenhuma ferramenta foi solicitada,
    # a expressão "or []" fornece uma lista vazia.
    #
    # Exemplo:
    # A IA pode solicitar:
    # agendar_entrevista_com_meet(...)
    #
    # IMPORTANTE:
    # Esta linha apenas identifica as solicitações.
    # Nenhuma função do Google é executada aqui.
    tools_calls = mensagem.tool_calls or []

    # --------------------------------------------------------
    # ETAPA 5: PREPARAR O RESULTADO
    # --------------------------------------------------------

    # Cria uma lista contendo uma tupla.
    #
    # "texto":
    # Identifica o tipo de conteúdo.
    #
    # mensagem.content:
    # Contém a resposta textual da IA.
    #
    # or:
    # Se o conteúdo estiver vazio ou for None,
    # utiliza a mensagem alternativa.
    #
    # ATENÇÃO:
    # Quando a IA solicita uma ferramenta, o conteúdo
    # textual pode estar vazio. Isso não significa
    # necessariamente que ocorreu um erro.
    resultado = []
    if not tools_calls:
        return [("texto", mensagem.content or "Descreva o cadastro ou a entrevista desejada.")]

    # --------------------------------------------------------
    # ETAPA 6: DEVOLVER O RESULTADO
    # --------------------------------------------------------

    # Retorna a lista preparada anteriormente.
    #
    # Exemplo de retorno:
    #
    # [
    #     ("texto", "Qual é o nome do candidato?")
    # ]
    #
    # Executa as chamadas de agendamento antes de devolver o resultado.
    for chamada in tools_calls:
        nome = chamada.function.name
        try:
            args = json.loads(chamada.function.arguments)
            if not isinstance(args, dict):
                raise ValueError("Argumentos inválidos.")
            if nome not in {"agendar_entrevista_com_meet", "registrar_candidato_na_planilha"}:
                raise ValueError("Ferramenta desconhecida.")
            obrigatorios = (
                ("nome_candidato", "email_candidato", "vaga", "data_hora_inicio", "data_hora_fim")
                if nome == "agendar_entrevista_com_meet" else ("nome", "email", "vaga")
            )
            faltantes = [campo for campo in obrigatorios if not isinstance(args.get(campo), str) or not args[campo].strip()]
            if faltantes:
                raise ValueError("Informe: " + ", ".join(faltantes))
            if not ID_PLANILHA:
                raise ValueError("Configure PLANILHA_ID no arquivo .env.")
        except (ValueError, TypeError) as erro:
            resultado.append(("erro", str(erro)))
            continue

        if nome == "agendar_entrevista_com_meet":
            try:
                link_meet = agendar_entrevista_com_meet(
                    args["nome_candidato"], args["email_candidato"],
                    args["data_hora_inicio"], args["data_hora_fim"],
                    vaga=args["vaga"],
                )
            except Exception as erro:
                resultado.append(("erro", f"Não foi possível concluir o agendamento: {erro}"))
                continue
            resultado.append(("calendar", link_meet or "Convite criado. O link do Meet ainda está sendo gerado pelo Google."))
            try:
                registrar_candidato_na_planilha(
                    ID_PLANILHA, args["nome_candidato"], args["email_candidato"],
                    args["vaga"], args.get("status") or "Entrevista agendada",
                    args["data_hora_inicio"], args["data_hora_fim"],
                )
                resultado.append(("sheets", "Candidato, vaga e status registrados na planilha."))
            except Exception as erro:
                resultado.append(("erro", f"O convite foi criado, mas o cadastro na planilha falhou: {erro}. Solicite apenas o cadastro para tentar novamente."))

        elif nome == "registrar_candidato_na_planilha":
            try:
                registrar_candidato_na_planilha(
                    ID_PLANILHA, args["nome"], args["email"],
                    args["vaga"], args.get("status") or "Cadastrado",
                )
                resultado.append(("sheets", "Candidato registrado na planilha."))
            except Exception as erro:
                resultado.append(("erro", f"Não foi possível registrar o candidato: {erro}"))

    return resultado
        
