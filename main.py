from fastapi import FastAPI

from modules.vton.api.routes import router as vton_router
from modules.catalog.api.routes import router as catalog_router

app = FastAPI()

app.include_router(vton_router, prefix="/vton", tags=["vton"])
app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])


@app.get("/")
def home():
    return {"status": "running"}