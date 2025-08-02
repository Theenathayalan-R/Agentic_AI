from fastapi import APIRouter

from app.api.v1.endpoints import domains, datasets, feedback

api_router = APIRouter()
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])