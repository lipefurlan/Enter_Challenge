import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from bo.report_bo import ReportBO, OUTPUT_DIR
from dao.client_dao import ClientDAO
from vo.client_vo import ClientVO
from vo.report_vo import ReportRequestVO, ReportResultVO


router = APIRouter(prefix="/api", tags=["reports"])

_dao = ClientDAO()
_bo = ReportBO(_dao)


@router.get("/clients", response_model=list[ClientVO])
async def list_clients():
    """Retorna todos os clientes disponíveis na pasta /clients."""
    return _dao.list_clients()


@router.post("/generate", response_model=list[ReportResultVO])
async def generate_reports(body: ReportRequestVO):
    """
    Recebe uma lista de IDs de clientes, roda o grafo Rivet para cada um
    (em paralelo) e retorna os resultados com o nome do arquivo .docx gerado.
    """
    if not body.client_ids:
        raise HTTPException(status_code=400, detail="Informe ao menos um client_id.")
    return await _bo.generate_reports(body.client_ids)


@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download do arquivo .docx gerado."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf",
    )
