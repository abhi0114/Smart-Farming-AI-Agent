"""
Smart Farming AI Agent — Application Entry Point
IBM Granite + RAG powered agricultural advisory system
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    from app.config import settings
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
