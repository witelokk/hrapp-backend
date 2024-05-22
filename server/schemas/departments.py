from pydantic import BaseModel


class Department(BaseModel):
    id: int
    name: str
    company_id: int
