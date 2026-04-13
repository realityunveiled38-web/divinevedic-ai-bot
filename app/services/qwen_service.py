"""
Qwen API Service - DivineVedic AI Bot
Handles all interactions with Qwen via OpenRouter API.
"""

import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

from app.config import settings


class QwenService:
    """Service for Qwen AI API operations via OpenRouter"""

    def __init__(self):
        self.api_url = settings.OPENROUTER_API_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.max_tokens = settings.OPENROUTER_MAX_TOKENS
        self.temperature = settings.OPENROUTER_TEMPERATURE
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Qwen service"""
        if not self.api_key:
            logger.warning("OpenRouter API key not set - Qwen service will not work")
            return False

        self._initialized = True
        logger.info("Qwen service initialized successfully")
        return True

    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Get completion from Qwen API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Override max tokens (optional)
            temperature: Override temperature (optional)
            system_prompt: System prompt to prepend (optional)
            
        Returns:
            Response text or None on error
        """
        try:
            if not self._initialized:
                logger.error("Qwen service not initialized")
                return None

            # Build messages list
            final_messages = messages.copy()
            
            # Add system prompt if provided
            if system_prompt:
                final_messages.insert(0, {"role": "system", "content": system_prompt})

            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": final_messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://divinevedic.ai",  # Required by OpenRouter
                "X-Title": "DivineVedic AI Bot"  # Required by OpenRouter
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # Extract response text
                response_text = result["choices"][0]["message"]["content"]
                
                if not response_text:
                    logger.warning("Empty response from Qwen API")
                    return None

                logger.info(f"Qwen API responded: {len(response_text)} chars")
                return response_text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Qwen API: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error from Qwen API: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected response format from Qwen API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Qwen API: {e}")
            return None

    async def get_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        retries: int = 2
    ) -> Optional[str]:
        """
        Get completion with automatic retry on failure.
        
        Args:
            messages: List of message dicts
            max_tokens: Override max tokens
            temperature: Override temperature
            system_prompt: System prompt
            retries: Number of retry attempts
            
        Returns:
            Response text or None after all retries
        """
        for attempt in range(retries + 1):
            response = await self.get_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt
            )
            if response is not None:
                return response
            
            if attempt < retries:
                logger.warning(f"Retry attempt {attempt + 1}/{retries} for Qwen API")
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        logger.error(f"All {retries + 1} attempts failed for Qwen API")
        return None


# Singleton instance
qwen_service = QwenService()
