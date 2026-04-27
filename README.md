# Enter Challenge — Automated Investment Report Generator

Automated monthly investment report generation system for XP Investimentos clients, combining portfolio analysis, macroeconomic context, and AI-powered buy/sell recommendations (Rivet + GPT-4o-mini).

---

## Deliverables

| File | Description |
|---|---|
| `Enter - Short Report.pdf` | Short report covering original MVP issues, improvement rationale, and next steps |
| `relatorio_albert-da-silva.pdf` | Sample generated letter for Albert da Silva |
| `relatorio_felipe-furlan.pdf` | Sample generated letter for Felipe Furlan |

> **Note on sample clients:** Albert and Felipe share the same portfolio structure and risk profile — Felipe was created to validate multi-client support. The difference is that Felipe's total assets and invested amounts are doubled, simulating a higher-volume client.

---

## Prerequisites

| Tool | Min version | Download |
|---|---|---|
| Python | 3.11+ | https://python.org/downloads |
| Node.js | 18+ | https://nodejs.org |
| Git | any | https://git-scm.com |

> On Windows 11, you can install all three via **winget**:
> ```bash
> winget install Git.Git
> winget install Python.Python.3.11
> winget install OpenJS.NodeJS
> ```

You will also need an **OpenAI API key** (the project uses GPT-4o-mini to generate the letters).

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Enter_Challenge
```

### 2. Install Python dependencies

```bash
pip install -r web-app/backend/requirements.txt
```

### 3. Install Node.js dependencies (Rivet runner)

```bash
cd web-app/rivet-runner && npm install && cd ../..
```

### 4. Configure the OpenAI key

```bash
cp web-app/backend/.env.example web-app/backend/.env
```

Open `.env` and replace with your actual key:

```
OPENAI_API_KEY=sk-proj-your-key-here
```

> The `.env` file is never pushed to GitHub (listed in `.gitignore`). The `.env.example` serves as a template for anyone cloning the project.

---

## Running the project

```bash
cd web-app/backend
python -m uvicorn main:app --reload --port 8000
```

Open your browser at: **http://localhost:8000**

---

## How to use

1. Open **http://localhost:8000**
2. Select one or more clients using the checkboxes
3. Click **"Gerar Relatórios"**
4. Wait for processing (~30s per client — the AI is generating the report)
5. Click **"Baixar .pdf"** to download the report

---

## API Documentation (Swagger)

Access **http://localhost:8000/docs** to view and test all endpoints interactively.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/clients` | List all available clients |
| `POST` | `/api/generate` | Generate reports for selected clients |
| `GET` | `/api/download/{filename}` | Download the generated PDF |

---

## Adding new clients

Create a folder under `web-app/clients/` with the client's name (no spaces) and add the following files:

```
web-app/clients/
└── joao-ferreira/
    ├── metadata.json          ← basic client info
    ├── portfolio.txt          ← portfolio statement (exported from XP)
    ├── risk_profile.txt       ← risk profile
    ├── macro_analysis.txt     ← monthly macro analysis
    ├── dividend_data.csv      ← dividend yield data
    └── profitability_calc.csv ← current and last month prices
```

**`metadata.json` format:**
```json
{
  "name": "Joao Ferreira",
  "email": "joao.ferreira@email.com",
  "advisor_name": "Antonio Bicudo"
}
```

The client will appear automatically in the interface on next load.

---

## Architecture

```
Enter_Challenge/
├── Enter Challenge.rivet-project   # AI graph (open in Rivet desktop)
├── web-app/
│   ├── backend/                    # Python API (FastAPI)
│   │   ├── main.py                 # Entry point
│   │   ├── routes/
│   │   │   └── report_rest.py      # REST endpoints
│   │   ├── bo/
│   │   │   └── report_bo.py        # Business logic + PDF export
│   │   ├── dao/
│   │   │   └── client_dao.py       # Client data access
│   │   └── vo/
│   │       ├── client_vo.py        # Client model
│   │       └── report_vo.py        # Report result model
│   ├── rivet-runner/
│   │   └── run_graph.js            # Runs the Rivet graph (Node.js)
│   ├── public/                     # Frontend (HTML + CSS + JS)
│   └── clients/                    # Client data folders
│       ├── albert-da-silva/
│       └── felipe-furlan/
```

### Report generation flow

```
Web Interface
    └─▶ POST /api/generate
            └─▶ ReportBO.generate_reports()
                    ├─▶ ClientDAO.get_client_files()   # reads client files
                    └─▶ subprocess: node run_graph.js  # runs Rivet graph
                            └─▶ GPT-4o-mini            # generates letter in Portuguese
                    └─▶ fpdf2 → saves .pdf
            └─▶ GET /api/download/{filename}
```

---

## Viewing the AI graph

To open and edit the AI pipeline visually:

1. Download **Rivet** at https://rivet.ironcladapp.com
2. Open the file `Enter Challenge.rivet-project`
3. Select the graph **`main_challenge`** in the side panel

---

## Troubleshooting

**`OPENAI_API_KEY` not found**
> Make sure the variable is set in the same terminal session where you ran `uvicorn`.

**Port 8000 already in use**
> Change the port: `python -m uvicorn main:app --port 8001`

**`node` not found**
> Verify Node.js is installed and in PATH: `node --version`

**Report returned empty**
> In Rivet, check that the final Chat node (letter) has **"Use as graph partial output"** enabled in settings (⚙️).