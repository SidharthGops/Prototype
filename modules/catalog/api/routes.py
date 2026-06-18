from fastapi import APIRouter
from modules.catalog.schemas.schemas import CatalogRequest, CatalogResponse
from modules.catalog.services.service import CatalogService

router = APIRouter()
service = CatalogService()


@router.post("/generate", response_model=CatalogResponse)
def generate(request: CatalogRequest) -> CatalogResponse:
    return service.process(request)
