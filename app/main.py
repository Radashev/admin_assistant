from fastapi import FastAPI

from app.api.v1.routes import router as v1_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(v1_router)


@app.get("/", tags=["system"])
def root():
    return {"app": settings.app_name, "env": settings.env, "status": "ok"}
