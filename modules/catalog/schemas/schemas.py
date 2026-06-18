from typing import List
from shared.schemas.base_schemas import JobRequest, JobResponse, ImageReference


class CatalogRequest(JobRequest):
    garment_image: ImageReference
    style: str


class CatalogResponse(JobResponse):
    catalog_images: List[ImageReference]
