import os
import sys

from dotenv import load_dotenv
load_dotenv()  # carrega o .env automaticamente

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes.report_rest import router

PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))

app = FastAPI(
    title="XP — Gerador de Relatórios Mensais",
    description="API para geração automatizada de relatórios de investimentos por cliente.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Arquivos estáticos (CSS, JS) em /static — sem conflito com /api
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))