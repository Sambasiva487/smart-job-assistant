from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, generate
import os

app = FastAPI(
    title="Smart Job Assistant API",
    description="AI-powered job application analysis using Claude",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(generate.router, prefix="/generate", tags=["Generation"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
