from pydantic import BaseModel


class ReportRequestVO(BaseModel):
    client_ids: list[str]


class ReportResultVO(BaseModel):
    client_id: str
    client_name: str
    status: str               # "success" | "error"
    filename: str | None = None
    letter_text: str | None = None
    error: str | None = None