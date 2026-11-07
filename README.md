# Central de Recrutamento

Aplicacao web desenvolvida com Streamlit para apoiar operacoes de recrutamento por meio de linguagem natural.

A Central de Recrutamento utiliza um agente de IA da Groq para interpretar solicitacoes, criar entrevistas no Google Calendar com Google Meet e registrar candidatos em uma planilha Google Sheets.

## Funcionalidades

- Interface web responsiva em Streamlit.
- Interpretacao de pedidos em linguagem natural com o modelo `openai/gpt-oss-20b`.
- Agendamento de entrevistas no Google Calendar.
- Criacao de sala Google Meet no convite.
- Registro automatico de candidatos, vagas, status e horarios no Google Sheets.
- Cadastro de candidato sem agendamento.
- Preservacao do resultado do convite quando o registro na planilha falha.
- Testes automatizados com mocks das APIs externas.

## Tecnologias

- Python
- Streamlit
- Groq OpenAI-compatible API
- Google Calendar API
- Google Sheets API
- Google OAuth 2.0
- `python-dotenv`
- `unittest`

## Estrutura do projeto

```text
.
├── agent.py          # Configuracao do agente, modelo e ferramentas
├── google_tools.py   # Autenticacao Google e integracoes com Calendar/Sheets
├── main.py           # Interface Streamlit
├── styles.css        # Estilos da interface
├── test_fluxo.py     # Testes de fluxo e interface
├── requirements.txt  # Dependencias Python
└── README.md         # Documentacao do projeto
```

## Requisitos

- Python 3.10 ou superior.
- Conta Groq com uma chave de API.
- Conta Google.
- Projeto configurado no Google Cloud.
- Google Calendar API e Google Sheets API habilitadas.
- Uma planilha Google Sheets para os candidatos.

## Instalacao

1. Clone o repositorio:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

2. Crie e ative um ambiente virtual:

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuracao da Groq

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_da_groq
PLANILHA_ID=id_da_sua_planilha_google
```

O identificador da planilha aparece na URL:

```text
https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA/edit
```

Utilize apenas o trecho identificado como `ID_DA_PLANILHA`.

## Configuracao do Google

1. Acesse o Google Cloud Console.
2. Crie um projeto ou selecione um projeto existente.
3. Habilite:
   - Google Calendar API
   - Google Sheets API
4. Configure uma tela de consentimento OAuth.
5. Adicione sua conta Google como usuario de teste, quando necessario.
6. Crie uma credencial OAuth do tipo `Aplicativo para computador`.
7. Baixe o arquivo JSON de credenciais.
8. Renomeie o arquivo para `credentials.json` e coloque-o na raiz do projeto.
9. Compartilhe a planilha com a conta Google que sera usada pela aplicacao.

Na primeira execucao, o navegador sera aberto para solicitar autorizacao de acesso ao:

- Google Calendar.
- Google Sheets.

O arquivo `token.json` sera criado automaticamente apos a autorizacao.

## Estrutura da planilha

Na primeira aba da planilha, o sistema localiza os dados pelos nomes das colunas. Cabecalhos aceitos incluem:

| Campo | Cabecalhos aceitos |
|---|---|
| Nome | `Nome`, `Nome Candidato` |
| Vaga | `Vaga`, `Cargo` |
| Email | `Email`, `E-mail`, `Email Candidato` |
| Status | `Status`, `Situacao` |
| Data | `Data`, `Data Entrevista` |
| Hora | `Hora`, `Horario`, `Horario Entrevista` |

Recomenda-se utilizar as seguintes colunas na primeira linha:

```text
Nome | Email | Vaga | Status | Data Entrevista | Horario Entrevista
```

## Execucao

Execute a interface com:

```bash
streamlit run main.py
```

O Streamlit exibira o endereco local da aplicacao, normalmente `http://localhost:8501`.

## Exemplos de solicitacoes

Agendar uma entrevista e registrar o candidato:

```text
Agende uma entrevista com Maria Silva, maria@email.com, para a vaga de Analista Financeiro
no dia 10/11/2026 das 14h as 15h.
```

Registrar apenas um candidato:

```text
Cadastre Joao Souza, joao@email.com, para a vaga de Desenvolvedor Python com status Cadastrado.
```

## Testes

Os testes simulam o agente e as integracoes externas, portanto nao criam convites reais nem alteram a planilha configurada.

Execute:

```bash
python -m unittest test_fluxo.py
```

## Seguranca

Nunca envie para o GitHub:

- `.env`
- `credentials.json`
- `token.json`
- Chaves de API
- Tokens OAuth
- Dados pessoais de candidatos
- Ambientes virtuais

Adicione ao `.gitignore`:

```gitignore
.env
credentials.json
token.json
.venv/
.venv.backup*/
__pycache__/
*.py[cod]
```

Se uma credencial for publicada por engano, revogue-a imediatamente no provedor e gere outra.

## Limitacoes

- Os horarios devem ser informados em um formato compreendido pelo agente.
- O sistema utiliza o calendario principal da conta Google autenticada.
- A planilha precisa possuir a primeira aba como aba de destino.
- Os nomes das colunas devem corresponder aos campos reconhecidos pelo programa.
- A criacao do link do Meet pode ser assincrona; o Google pode indicar inicialmente que o link ainda esta sendo gerado.

## Contribuicoes

Contribuicoes sao bem-vindas. Para uma mudanca:

1. Crie uma branch.
2. Implemente e documente a alteracao.
3. Execute os testes.
4. Abra um Pull Request.

## Licenca

Defina neste repositorio a licenca desejada antes da publicacao. Para uso academico ou pessoal, uma licenca como MIT pode ser apropriada, desde que revise as exigencias do seu contexto.
