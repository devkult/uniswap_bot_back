from fastapi import APIRouter
from presentation.api.uniswap.competitions.handlers import router as competitions_router


router = APIRouter()

router.include_router(router=competitions_router, prefix="/competitions")