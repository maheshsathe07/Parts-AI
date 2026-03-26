import certifi_win32
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.parts import router as parts_router
import uvicorn
from config import settings
from tools.web_search import close_http_client
from tools.youtube_search import close_youtube_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup/shutdown events.
    Ensures HTTP clients are properly closed on shutdown.
    """
    yield
    # Cleanup: close HTTP connection pools
    await close_http_client()
    await close_youtube_http_client()


app = FastAPI(
    title="Auto Parts AI Research API",
    description="AI-powered automotive parts research for the US market using Groq LLaMA-3",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parts_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)