# Central de Recrutamento

Aplicação Streamlit para gerenciar entrevistas no Google Calendar, criar links do Google Meet e cadastrar candidatos no Google Sheets com auxílio de um assistente de IA da Groq.

## Funcionalidades

### Dashboard de agendamentos

- Consulta de entrevistas por período, com data inicial e final incluídas.
- Busca por nome, e-mail ou vaga entre as entrevistas carregadas.
- Indicadores de entrevistas no filtro, entrevistas de hoje, próximas entrevistas e reuniões com Meet.
- Tabela de agendamentos e gráfico de entrevistas por dia.
- Criação de entrevistas com solicitação de link do Google Meet.
- Edição de candidato, e-mail, vaga e datas e horários.
- Exclusão com confirmação e solicitação de cancelamento aos participantes.
- Proteção contra sobrescrever um evento alterado após a consulta.
- Guias de uso, exemplos nos campos, dicas de ajuda e legendas dos indicadores.

### Assistente de recrutamento

- Interpretação de pedidos em linguagem natural com o modelo `openai/gpt-oss-20b`, pela API da Groq.
- Agendamento de entrevistas e cadastro automático do candidato na planilha.
- Cadastro de candidatos sem criar uma entrevista.
- Exibição separada dos resultados do calendário e da planilha, incluindo falhas parciais.

**Diferença entre as telas:** o dashboard gerencia os eventos do Google Calendar. Suas inclusões, edições e exclusões não atualizam os cadastros no Google Sheets. O registro de candidatos na planilha é feito pelo assistente.

## Requisitos

- Python 3.12 recomendado, versão utilizada na validação do projeto.
- Conta Google com acesso ao calendário e à planilha desejados.
- Credenciais OAuth para aplicativo de computador, com Google Calendar API e Google Sheets API habilitadas no projeto Google Cloud.
- Chave de API da Groq para utilizar o assistente. O dashboard não utiliza a IA.

## Instalação

Abra o terminal na pasta do projeto. No Windows, usando PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem precisar ativá-lo. Se o comando `python` não estiver disponível, instale o Python e reabra o terminal. Um ambiente virtual copiado de outro computador pode precisar ser recriado.

No Linux ou macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Configuração

### Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_da_groq
PLANILHA_ID=id_da_sua_planilha_google
```

Em uma URL como `https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA/edit`, copie somente o trecho `ID_DA_PLANILHA`.

### Autorização Google

1. No projeto Google Cloud, habilite as APIs Google Calendar e Google Sheets.
2. Configure o consentimento OAuth e os usuários de teste, quando aplicável.
3. Crie uma credencial OAuth do tipo aplicativo de computador e baixe seu JSON.
4. Salve o arquivo como `credentials.json` na raiz do projeto.
5. Garanta que a conta que será autorizada tenha permissão para editar a planilha.

Na primeira operação que acessar o Google, o sistema poderá abrir o navegador para solicitar autorização. Após a autorização, o arquivo `token.json` é salvo para reutilizar o acesso. O calendário utilizado é o principal da conta autorizada.

### Estrutura da planilha

A implementação grava na aba cujo identificador numérico é **`sheetId=0`**. Essa aba precisa existir; não basta que uma aba qualquer seja a primeira visível na planilha.

Os campos são identificados pelos cabeçalhos da primeira linha, entre as colunas A e Z. A comparação ignora acentos, espaços, pontuação e diferenças entre maiúsculas e minúsculas.

| Campo | Exemplos de cabeçalhos reconhecidos |
| --- | --- |
| Nome | Nome, Nome Candidato |
| E-mail | Email, E-mail, Email Candidato |
| Vaga | Vaga, Cargo |
| Status | Status, Situação |
| Data | Data, Data Entrevista |
| Hora | Hora, Horário, Horário Entrevista |

Sugestão de cabeçalho:

```text
Nome | Email | Vaga | Status | Data Entrevista | Horário Entrevista
```

Inclua todas essas colunas para registrar os dados completos. O programa grava apenas os campos cujas colunas forem reconhecidas.

## Executar a aplicação

No Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run main.py
```

No Linux ou macOS:

```bash
.venv/bin/python -m streamlit run main.py
```

Abra o endereço exibido no terminal. A porta pode variar conforme a disponibilidade. Para definir uma porta específica, acrescente `--server.port=8502` ao comando.

## Como usar

### Consultar entrevistas

1. Abra **Agendamentos** no menu lateral.
2. Escolha a data inicial e a data final da consulta.
3. Clique em **Atualizar agendamentos**.
4. Use a busca para filtrar por candidato, e-mail ou vaga.

Ao mudar o período, clique novamente em Atualizar agendamentos para buscar os dados do Google. A busca filtra somente os registros já carregados. A tabela, o gráfico e os indicadores acompanham os filtros.

| Indicador | Significado |
| --- | --- |
| Entrevistas no filtro | Total de entrevistas no resultado atual |
| Hoje | Entrevistas do resultado atual que começam hoje |
| Próximas | Entrevistas do resultado atual cujo início ainda não chegou |
| Com Google Meet | Entrevistas do resultado atual com link de reunião disponível |

Todos os horários seguem **America/Sao_Paulo**, horário de Brasília. O painel reconhece entrevistas pelo título iniciado por `Entrevista com ` ou pela identificação interna adicionada pelo sistema. Eventos de dia inteiro não aparecem.

### Adicionar uma entrevista

Na aba **Adicionar entrevista**, preencha nome, e-mail, vaga e datas e horários de início e término. Confira os dados e clique em **Adicionar agendamento**. O término deve ser posterior ao início.

O sistema cria o evento no Google Calendar, solicita o envio do convite aos participantes e solicita um link do Google Meet. O link pode levar alguns instantes para ficar disponível; atualize a agenda para consultá-lo.

### Editar ou excluir

Na aba **Editar ou excluir**, selecione a entrevista pela data, horário e nome.

- Para editar, altere os campos e clique em **Salvar alterações**. As mudanças só são enviadas ao salvar.
- Para excluir, abra **Excluir agendamento**, confira a entrevista selecionada, marque a confirmação e clique em **Excluir definitivamente**. A tela não oferece desfazer.
- Para acessar a reunião, use **Abrir Google Meet**, quando o link estiver disponível.

As operações solicitam notificações aos participantes. Em eventos recorrentes, a edição ou exclusão afeta apenas a ocorrência selecionada. Se o evento tiver sido alterado desde a consulta, atualize a lista antes de tentar novamente.

### Enviar pedidos ao assistente

Abra **Assistente** no menu lateral, descreva o pedido e clique em **Processar solicitação**. Um pedido completo pode executar as ações e enviar convites imediatamente.

Exemplo de agendamento com cadastro na planilha:

```text
Agende uma entrevista com Ana Silva, ana@example.com, para a vaga de Analista Financeiro,
no dia 10/11/2026, das 14h às 15h, no horário de Brasília.
```

Exemplo de cadastro sem entrevista:

```text
Cadastre João Souza, joao@example.com, para a vaga de Desenvolvedor Python,
com status Em análise.
```

Se o convite for criado, mas o cadastro na planilha falhar, solicite **apenas o cadastro** para evitar duplicar a entrevista. Após agendar pelo assistente, volte ao dashboard e atualize a lista.

### Legenda das integrações

Na barra lateral, verde significa que a configuração foi encontrada; amarelo indica configuração pendente. Esses indicadores não comprovam que a conexão funciona: o acesso é verificado ao usar o serviço.

## Estrutura do projeto

```text
.
├── main.py           # Interface principal, navegação e tela do assistente
├── dashboard.py      # Dashboard, filtros, indicadores e formulários
├── agenda_service.py # Consulta, criação, edição e exclusão no Calendar
├── agent.py          # Cliente Groq, instruções e execução de ferramentas
├── google_tools.py   # OAuth Google, agendamento e cadastro no Sheets
├── styles.css        # Estilos da interface
├── test_dashboard.py # Testes do dashboard e das operações de agenda
├── test_fluxo.py     # Testes do fluxo do assistente e da interface
├── requirements.txt  # Dependências Python
└── README.md         # Documentação
```

## Testes

No Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest test_dashboard test_fluxo -v
```

No Linux ou macOS:

```bash
.venv/bin/python -m unittest test_dashboard test_fluxo -v
```

A suíte atual contém 10 testes que usam integrações simuladas e `AppTest` do Streamlit. Eles cobrem listagem paginada, filtros, criação, edição, exclusão com confirmação, validação de horários e falhas parciais. Não criam convites reais nem alteram a planilha. Essa validação não substitui verificar as permissões da conta Google utilizada.

## Cuidados com os dados

Mantenha `.env`, `credentials.json`, `token.json` e ambientes virtuais fora do controle de versão. Esses caminhos já constam no `.gitignore`. Não publique dados pessoais de candidatos. Se uma credencial for exposta, revogue-a no provedor.

## Solução de problemas

| Situação | O que verificar |
| --- | --- |
| Python não encontrado ou erro ao abrir o `.venv` | Instalação do Python e recriação do ambiente virtual |
| Agenda vazia | Período, texto da busca, conta autorizada e identificação dos eventos como entrevistas |
| Vaga não informada | Entrevistas antigas podem não ter esse dado; preencha a vaga ao editar |
| Meet em branco | Atualize a agenda; o link pode estar sendo gerado ou o evento pode não ter videoconferência |
| Falha de autorização | Permissões da conta Google, credenciais OAuth e APIs habilitadas |
| Aba da planilha não encontrada | Existência da aba com `sheetId=0` e valor de `PLANILHA_ID` |
| Evento alterado por outra pessoa | Atualize a agenda para carregar a versão mais recente antes de salvar ou excluir |
| Falha somente no cadastro | Confira a planilha e solicite apenas o cadastro pelo assistente |
