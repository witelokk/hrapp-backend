from typing import Annotated
from pydantic import BaseModel, StringConstraints


class Company(BaseModel):
    id: int
    name: str
    inn: str
    kpp: str


class CreateCompanyRequest(BaseModel):
    name: str
    inn: Annotated[str, StringConstraints(min_length=10, max_length=10, pattern="\d+")]
    kpp: Annotated[str, StringConstraints(min_length=9, max_length=9, pattern="\d+")]


class EditCompanyRequest(BaseModel):
    name: str = None
    inn: Annotated[
        str, StringConstraints(min_length=10, max_length=10, pattern="\d+")
    ] = None
    kpp: Annotated[
        str, StringConstraints(min_length=9, max_length=9, pattern="\d+")
    ] = None


class CreatedCompanyId(BaseModel):
    id: int
