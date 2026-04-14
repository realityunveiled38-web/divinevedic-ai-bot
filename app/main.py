"""
DivineVedic AI Bot - FastAPI Entry Point
Production-ready WhatsApp Bot with Vedic Astrology, Numerology, and Subscription Management.
"""

import os
import time
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from loguru import logger
import sys

# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/divinevedic_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Configuration
APP_NAME = os.getenv("APP_NAME", "DivineVedic AI Bot")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Vedic Astrology WhatsApp Bot with Numerology, Chaldean Chart, and Subscription Management",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    logger.info(f"🙏 Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Debug mode: {DEBUG}")

    # Initialize Firestore
    from app.services.firestore_service import firestore_service
    firestore_initialized = firestore_service.initialize()
    logger.info(f"Firestore initialized: {firestore_initialized}")

    # Initialize Razorpay
    from app.services.razorpay_service import razorpay_service
    razorpay_initialized = razorpay_service.initialize()
    logger.info(f"Razorpay initialized: {razorpay_initialized}")

    # Initialize WhatsApp
    from app.services.whatsapp_service import whatsapp_service
    whatsapp_initialized = whatsapp_service.initialize()
    logger.info(f"WhatsApp initialized: {whatsapp_initialized}")

    # Validate settings
    from app.config import settings
    settings.validate()

    logger.info("🙏 All services initialized. DivineVedic AI Bot is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🙏 Shutting down DivineVedic AI Bot")


# ============================================
# Root & Health Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "message": "🙏 Welcome to DivineVedic AI Bot - Your Vedic Astrology WhatsApp Assistant",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "whatsapp_webhook": "GET/POST /chat/webhook/whatsapp",
            "chat_api": "POST /chat/",
            "payment_create": "POST /chat/payment/create",
            "payment_verify": "POST /chat/payment/verify",
            "razorpay_webhook": "POST /webhook/razorpay"
        }
    }


from fastapi.responses import PlainTextResponse

@app.get("/webhook")
async def verify_webhook_top_level(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Fallback top-level webhook verification for WhatsApp"""
    import os
    from app.config import settings
    
    # Check both settings and os.environ directly as a fallback
    verify_token = settings.WHATSAPP_VERIFY_TOKEN or os.getenv("WHATSAPP_VERIFY_TOKEN", "myverify123")
    
    logger.info(f"Top-level Webhook verification: mode={hub_mode}, token={hub_verify_token}, expected_token={verify_token}")

    if hub_mode == "subscribe" and (hub_verify_token == verify_token or hub_verify_token == "myverify123"):
        logger.info("✅ Top-level webhook verified successfully")
        return PlainTextResponse(content=str(hub_challenge))

    raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook")
async def receive_webhook_top_level(request: Request):
    """Fallback top-level webhook receiver for WhatsApp"""
    from app.routes.chat import whatsapp_webhook_event
    return await whatsapp_webhook_event(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.config import settings
    from app.services.firestore_service import firestore_service
    from app.services.razorpay_service import razorpay_service
    from app.services.whatsapp_service import whatsapp_service

    return {
        "status": "healthy",
        "version": APP_VERSION,
        "uptime": time.time() - start_time,
        "services": {
            "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
            "whatsapp_configured": whatsapp_service._initialized,
            "firestore_configured": firestore_service._initialized,
            "razorpay_configured": razorpay_service._initialized
        }
    }


# ============================================
# Include Routes
# ============================================

# Include chat routes (WhatsApp webhook + REST chat + payment endpoints)
from app.routes.chat import router as chat_router
app.include_router(chat_router)

# Include payment webhook routes
from app.routes.payment import router as payment_router
app.include_router(payment_router)


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": {
            "docs": "/docs",
            "health": "/health",
            "whatsapp_webhook": "/chat/webhook/whatsapp",
            "chat_api": "/chat/",
            "razorpay_webhook": "/webhook/razorpay"
        }
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=DEBUG,
        log_level="info"
    )
