from io import BytesIO
from fastapi import HTTPException, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
)

from server.api.dependenicies import user_dependency

from server.api.dependenicies import user_dependency, db_dependency
from server.database import models

router = APIRouter(prefix="/reports", tags=["reports"])


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
