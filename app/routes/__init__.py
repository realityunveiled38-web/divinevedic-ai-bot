"""
Routes Package - DivineVedic AI Bot
"""

from app.routes.chat import router as chat_router
from app.routes.payment import router as payment_router

__all__ = ["chat_router", "payment_router"]
