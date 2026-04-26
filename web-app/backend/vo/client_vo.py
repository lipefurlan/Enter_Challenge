from pydantic import BaseModel


class ClientVO(BaseModel):
    id: str
    name: str
    email: str
    advisor_name: str