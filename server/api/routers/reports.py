from fastapi import HTTPException, status
from fastapi.responses import Response
from fastapi.routing import APIRouter

from server.services.reports_service import CompanyNotExistsError, ForbiddenError
from server.api.dependenicies import user_dependency, reports_service_dependency

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/company/{company_id}")
def generate_report(
    reports_service: reports_service_dependency, user: user_dependency, company_id: int
):
    try:
        report = reports_service.generate_report(user["id"], company_id)
    except CompanyNotExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Company does not exist")
    except ForbiddenError:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return Response(content=report, media_type="application/pdf")
