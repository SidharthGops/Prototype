from modules.catalog.services.service import CatalogService


def test_health_check():
    service = CatalogService()
    assert service.health_check() is True
