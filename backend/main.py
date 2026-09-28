from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.database.init_db import init_db
from backend.routes.ai import router as ai_router
from backend.routes.voice import router as voice_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


app = FastAPI(
    lifespan=lifespan
)

app.include_router(ai_router)
app.include_router(voice_router)