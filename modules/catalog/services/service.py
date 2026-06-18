from shared.interfaces.module_interface import BaseModuleService
from modules.catalog.schemas.schemas import CatalogRequest, CatalogResponse


class CatalogService(BaseModuleService):
    """
    Pipeline (to implement):
        garment_image
          -> garment segmentation
          -> AI avatar generation
          -> catalog/studio image generation
          -> catalog_images
    """

    def process(self, request: CatalogRequest) -> CatalogResponse:
        # TODO: implement the catalog generation pipeline.
        raise NotImplementedError

    def health_check(self) -> bool:
        return True
