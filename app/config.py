"""
Application Configuration - DivineVedic AI Bot
Complete settings for WhatsApp, Razorpay, Firestore, OpenAI, and Subscription Plans
"""

import os
from dotenv import load_dotenv
from loguru import logger
from typing import Optional

load_dotenv()


class Settings:
    """Application settings with all required configurations"""

    # ---- Application Settings ----
    APP_NAME: str = os.getenv("APP_NAME", "DivineVedic AI Bot")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "default-secret-key-change-in-production")

    # ---- OpenRouter API (Qwen) ----
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen2.5-7b-instruct")
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "2000"))
    OPENROUTER_TEMPERATURE: float = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))

    # ---- WhatsApp Cloud API ----
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_WEBHOOK_URL: str = os.getenv("WHATSAPP_WEBHOOK_URL", "")
    WHATSAPP_API_BASE_URL: str = "https://graph.facebook.com/v18.0"

    # ---- Firebase / Firestore ----
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")

    # ---- Razorpay Payment Gateway ----
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    RAZORPAY_WEBHOOK_URL: str = os.getenv("RAZORPAY_WEBHOOK_URL", "")

    # ---- Subscription Plans ----
    TRIAL_DURATION_MINUTES: int = int(os.getenv("TRIAL_DURATION_MINUTES", "5"))

    # Plan 1: ₹199 - 10 minutes talk time
    PLAN_199_PRICE: int = 199
    PLAN_199_DURATION_MINUTES: int = int(os.getenv("PLAN_199_DURATION_MINUTES", "10"))

    # Plan 2: ₹499 - 30 minutes + 3 questions (Most Popular)
    PLAN_499_PRICE: int = 499
    PLAN_499_DURATION_MINUTES: int = int(os.getenv("PLAN_499_DURATION_MINUTES", "30"))
    PLAN_499_QUESTIONS: int = int(os.getenv("PLAN_499_QUESTIONS", "3"))

    # Plan 3: Pro Plan - ₹999/₹1499 - 1 month unlimited
    PLAN_PRO_PRICE: int = int(os.getenv("PLAN_PRO_PRICE", "999"))
    PLAN_PRO_PRICE_ALT: int = 1499
    PLAN_PRO_DURATION_DAYS: int = int(os.getenv("PLAN_PRO_DURATION_DAYS", "30"))

    # ---- Security ----
    WEBHOOK_SIGNATURE_VERIFICATION: bool = os.getenv("WEBHOOK_SIGNATURE_VERIFICATION", "True").lower() == "true"

    # ---- Subscription Plan Definitions ----
    PLANS: dict = {
        "trial": {
            "name": "Free Trial",
            "price": 0,
            "duration_minutes": 5,
            "questions": 0,
            "features": ["5 minute free trial", "Basic astrology queries"]
        },
        "basic": {
            "name": "Basic Plan",
            "price": 199,
            "duration_minutes": 10,
            "questions": 0,
            "features": ["10 minutes talk time", "Kundali analysis", "Basic predictions"]
        },
        "popular": {
            "name": "Most Popular Plan",
            "price": 499,
            "duration_minutes": 30,
            "questions": 3,
            "features": ["30 minutes talk time", "3 detailed questions", "Kundali + Numerology", "Puja recommendations"]
        },
        "pro": {
            "name": "Pro Plan",
            "price": 999,
            "duration_minutes": None,  # Unlimited
            "questions": None,  # Unlimited
            "features": ["1 month unlimited access", "Janam Kundali", "Puja-Mantra", "Past-Present-Future", "Expert connect"]
        }
    }

    def validate(self) -> bool:
        """Validate required settings"""
        warnings = []

        if not self.OPENROUTER_API_KEY:
            warnings.append("OPENROUTER_API_KEY is not set - AI features will use fallback responses")

        if not self.WHATSAPP_ACCESS_TOKEN:
            warnings.append("WHATSAPP_ACCESS_TOKEN is not set - WhatsApp integration will not work")

        if not self.WHATSAPP_PHONE_NUMBER_ID:
            warnings.append("WHATSAPP_PHONE_NUMBER_ID is not set - WhatsApp messages cannot be sent")

        if not self.FIREBASE_PROJECT_ID:
            warnings.append("FIREBASE_PROJECT_ID is not set - Firestore will not be available")

        if not self.RAZORPAY_KEY_ID:
            warnings.append("RAZORPAY_KEY_ID is not set - Payment gateway will not work")

        for warning in warnings:
            logger.warning(warning)

        return len(warnings) == 0

    def get_plan(self, plan_id: str) -> Optional[dict]:
        """Get plan details by plan_id"""
        return self.PLANS.get(plan_id)


# Global settings instance
settings = Settings()
