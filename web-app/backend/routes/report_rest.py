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
    """Returns all clients available in the /clients folder."""
    return _dao.list_clients()


@router.post("/generate", response_model=list[ReportResultVO])
async def generate_reports(body: ReportRequestVO):
    """
    Receives a list of client IDs, runs the Rivet graph for each one
    (in parallel) and returns the results with the generated PDF filename.
    """
    if not body.client_ids:
        raise HTTPException(status_code=400, detail="Provide at least one client_id.")
    return await _bo.generate_reports(body.client_ids)


@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download the generated PDF report."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf",
    )
