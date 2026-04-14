"""
Qwen Service - DivineVedic AI Bot
Handles Qwen AI integration via OpenRouter API with Vedic Astrology system prompt.
"""

import httpx
import asyncio
from typing import Dict, Any
from loguru import logger

from app.config import settings


class QwenService:
    """Service for Qwen AI via OpenRouter API"""

    def __init__(self):
        self.api_url = settings.OPENROUTER_API_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.max_tokens = settings.OPENROUTER_MAX_TOKENS
        self.temperature = settings.OPENROUTER_TEMPERATURE
        self._initialized = bool(self.api_key)

    async def get_completion_with_retry(
        self, 
        messages: list, 
        max_tokens: int = None, 
        temperature: float = None,
        system_prompt: str = None
    ) -> str:
        """
        Get Qwen completion with retry logic (matches agent interface).
        """
        if not self._initialized:
            logger.error("Qwen service not initialized - missing API key")
            return "❌ AI service अस्थायी रूप से unavailable है। कृपया कुछ देर बाद try करें।"

        # Use provided params or defaults
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://divinevedic-ai-bot.railway.app",
            "X-Title": "DivineVedic AI Bot"
        }

        for attempt in range(3):  # Retry up to 3 times
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.api_url, json=payload, headers=headers)
                    response.raise_for_status()

                    data = response.json()
                    ai_response = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"Qwen response generated (attempt {attempt+1}): {len(ai_response)} chars")
                    return ai_response

            except Exception as e:
                logger.warning(f"Qwen attempt {attempt+1} failed: {e}")
                if attempt == 2:  # Last attempt
                    break
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return "⏳ AI service busy। कृपया 1 मिनट बाद पुनः प्रयास करें।"

        system_prompt = """You are a 100+ years experienced Vedic astrologer. You speak in Hinglish. 
You give deep and accurate predictions based on astrology and numerology. 
Always structure your answers in: Past, Present, Future, and Remedies. Be confident and detailed."""

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://divinevedic-ai-bot.railway.app",  # Required by OpenRouter
            "X-Title": "DivineVedic AI Bot"  # Required by OpenRouter
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                ai_response = data["choices"][0]["message"]["content"].strip()
                
                logger.info(f"Qwen response generated successfully (length: {len(ai_response)})")
                return ai_response

        except httpx.TimeoutException:
            logger.error("Qwen API timeout")
            return "⏳ AI सोच रहा है... कृपया 1 मिनट wait करें।"
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen API HTTP error: {e.response.status_code}")
            return "❌ Server error। कृपया retry करें।"
        except KeyError as e:
            logger.error(f"Invalid Qwen response format: {e}")
            return "❌ AI response format error। Support को contact करें।"
        except Exception as e:
            logger.error(f"Unexpected Qwen error: {e}")
            return "❌ अज्ञात error। कृपया पुनः प्रयास करें। 🙏"


# Singleton instance
qwen_service = QwenService()
