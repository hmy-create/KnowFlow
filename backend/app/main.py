from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.eval import router as eval_router


app = FastAPI(
    title="KnowFlow API",
    description="KnowFlow Enterprise Trusted Knowledge Collaboration Agent",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(eval_router)