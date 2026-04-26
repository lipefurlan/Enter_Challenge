# Enter Challenge — Gerador de Relatórios de Investimentos

Sistema de geração automatizada de relatórios mensais de investimentos para clientes XP, com análise de portfólio, contexto macroeconômico e recomendações de buy/sell via IA (Rivet + GPT-4o-mini).

---

## Pré-requisitos

Antes de começar, instale:

| Ferramenta | Versão mínima | Download |
|---|---|---|
| Python | 3.11+ | https://python.org/downloads |
| Node.js | 18+ | https://nodejs.org |
| Git | qualquer | https://git-scm.com |

Você também precisa de uma **chave de API da OpenAI** (o projeto usa GPT-4o-mini para gerar as cartas).

---

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Enter_Challenge
```

### 2. Instale as dependências Python

```bash
cd web-app/backend
pip install -r requirements.txt
```

### 3. Instale as dependências Node.js (runner do Rivet)

```bash
cd ../rivet-runner
npm install
```

### 4. Configure a chave da OpenAI

```bash
cd web-app/backend
cp .env.example .env
```

Abra o arquivo `.env` e substitua pelo valor real:

```
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

> O arquivo `.env` nunca vai para o GitHub (está no `.gitignore`). O `.env.example` serve de modelo para quem clonar o projeto.

---

## Rodando o projeto

```bash
cd web-app/backend
python -m uvicorn main:app --reload --port 8000
```

Abra o navegador em: **http://localhost:8000**

---

## Como usar

1. Abra **http://localhost:8000**
2. Selecione um ou mais clientes com o checkbox
3. Clique em **"Gerar Relatórios"**
4. Aguarde o processamento (pode levar ~30s por cliente — a IA está gerando o relatório)
5. Clique em **"Baixar .docx"** para salvar o relatório

---

## Documentação da API (Swagger)

Acesse **http://localhost:8000/docs** para ver e testar todos os endpoints interativamente.

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/clients` | Lista todos os clientes disponíveis |
| `POST` | `/api/generate` | Gera relatórios para os clientes selecionados |
| `GET` | `/api/download/{filename}` | Faz download do .docx gerado |

---

## Adicionando novos clientes

Crie uma pasta em `web-app/clients/` com o nome do cliente (sem espaços) e adicione os arquivos:

```
web-app/clients/
└── joao-ferreira/
    ├── metadata.json         ← dados básicos do cliente
    ├── portfolio.txt         ← extrato da carteira (exportado da XP)
    ├── risk_profile.txt      ← perfil de risco
    ├── macro_analysis.txt    ← análise macro do mês
    ├── dividend_data.csv     ← dados de dividend yield
    └── profitability_calc.csv ← preços atual e do mês anterior
```

**Formato do `metadata.json`:**
```json
{
  "name": "João Ferreira",
  "email": "joao.ferreira@email.com",
  "advisor_name": "Antonio Bicudo"
}
```

O cliente aparecerá automaticamente na interface na próxima vez que acessar.

---

## Arquitetura

```
Enter_Challenge/
├── Enter Challenge.rivet-project   # Grafo de IA (abre no Rivet desktop)
├── web-app/
│   ├── backend/                    # API Python (FastAPI)
│   │   ├── main.py                 # Entry point — sobe o servidor
│   │   ├── routes/
│   │   │   └── report_rest.py      # Endpoints REST
│   │   ├── bo/
│   │   │   └── report_bo.py        # Lógica de negócio
│   │   ├── dao/
│   │   │   └── client_dao.py       # Acesso aos dados dos clientes
│   │   └── vo/
│   │       ├── client_vo.py        # Modelo de cliente
│   │       └── report_vo.py        # Modelo de resultado
│   ├── rivet-runner/
│   │   └── run_graph.js            # Executa o grafo Rivet (Node.js)
│   ├── public/                     # Frontend (HTML + CSS + JS)
│   └── clients/                    # Dados dos clientes
│       └── albert-da-silva/
```

### Fluxo de geração de um relatório

```
Interface Web
    └─▶ POST /api/generate
            └─▶ ReportBO.generate_reports()
                    ├─▶ ClientDAO.get_client_files()   # lê os arquivos do cliente
                    └─▶ subprocess: node run_graph.js  # executa o grafo Rivet
                            └─▶ GPT-4o-mini            # gera a carta em português
                    └─▶ python-docx → salva .docx
            └─▶ GET /api/download/{arquivo}
```

---

## Visualizando o grafo de IA

Para abrir e editar o pipeline de IA visualmente:

1. Baixe o **Rivet** em https://rivet.ironcladapp.com
2. Abra o arquivo `Enter Challenge.rivet-project`
3. Selecione o grafo **`main_challenge`** no painel lateral

---

## Problemas comuns

**`OPENAI_API_KEY` não encontrada**
> Certifique-se de que a variável está setada na mesma sessão do terminal onde rodou o `uvicorn`.

**Porta 8000 ocupada**
> Troque a porta: `python -m uvicorn main:app --port 8001`

**`node` não encontrado**
> Verifique se o Node.js está instalado e no PATH: `node --version`

**Relatório retornou vazio**
> No Rivet, verifique se o nó Chat final (carta) está com **"Use as graph partial output"** ativado nas configurações (⚙️).