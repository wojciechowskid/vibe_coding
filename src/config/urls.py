from fastapi import APIRouter

from app.auth_context.infrastructure.urls import router as auth_router
from app.probe_context.infrastructure.urls import router as probe_router

router = APIRouter(prefix='/api/v1')
router.include_router(auth_router, prefix='/auth', tags=['Auth'])
router.include_router(probe_router, prefix='/probe', tags=['Probe'])
