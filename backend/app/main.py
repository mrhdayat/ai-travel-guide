from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.core.config import settings
# Temporarily disable database imports for demo
# from app.core.database import engine, Base
# from app.api import plan, vision, chat, auth
# from app.services.ai_service import AIService

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Temporarily disable database initialization
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # Initialize AI service
    # app.state.ai_service = AIService()

    yield

    # Shutdown
    # await engine.dispose()

app = FastAPI(
    title="AI Travel Guide API",
    description="API untuk Panduan Wisata AI Multimodal",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers - temporarily disabled for demo
# app.include_router(plan.router, prefix="/api", tags=["travel-planning"])
# app.include_router(vision.router, prefix="/api", tags=["vision"])
# app.include_router(chat.router, prefix="/api", tags=["chat"])
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {
        "message": "Selamat datang di AI Travel Guide API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "demo_mode",
            "ai_service": "demo_mode"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
