from io import BytesIO
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from . import auth

from .. import models
from ..database import db_dependency

router = APIRouter(prefix="/reports", tags=["reports"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


@router.get("/company/{company_id}")
def generate_report(db: db_dependency, user: user_dependency, company_id: int):
    company = db.query(models.Company).filter_by(id=company_id).first()

    if company is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")

    if company.owner_id != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = [Paragraph(f"REPORT for company {company_id}")]
    doc.build(elements)
    return Response(content=buffer.getvalue(), media_type="application/pdf")
