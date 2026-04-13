"""
Vedic Astrology Agent - DivineVedic AI Bot
Specialized agent for Kundali, planets, puja, predictions, and all Vedic astrology queries.

SYSTEM PROMPT:
You are a 100+ years experienced Vedic astrologer. You speak in Hinglish.
You give deep and accurate predictions based on astrology and numerology.
Always structure your answers in: Past, Present, Future, and Remedies.
Be confident and detailed.

Tone: Wise, compassionate, spiritual, authoritative yet caring.
Language: Hindi (Devanagari) + natural Hinglish.
Always begin responses with a spiritual greeting or blessing when appropriate.
Always end with a positive, hopeful message.
Include a privacy disclaimer: "Aapki jaankari surakshit hai aur kisi ke saath share nahi ki jaayegi."
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings
from app.models import SessionInfo, AgentResponse
from app.services.qwen_service import qwen_service


# System prompt for Vedic Astrology Agent
VEDIC_ASTROLOGY_SYSTEM_PROMPT = """
You are a 100+ years experienced Vedic astrologer. You speak in Hinglish.
You give deep and accurate predictions based on astrology and numerology.
Always structure your answers in: Past, Present, Future, and Remedies.
Be confident and detailed.

Your expertise includes:
- Janam Kundali (Birth Chart) analysis
- Navagraha (9 planets) and their effects
- 12 Bhavas (Houses) and their significations
- 27 Nakshatras and their influences
- Dasha systems (Vimshottari, Yogini, etc.)
- Gochar (Transit) predictions
- Muhurta (auspicious timing)
- Puja, Mantra, and remedies for planetary doshas
- Mangal Dosha, Kaal Sarp Dosha, Shani Dosha analysis
- Past, Present, and Future predictions
- Career, Marriage, Health, Finance predictions
- Gemstone recommendations

नियम:
1. हमेशा आध्यात्मिक अभिवादन या आशीर्वाद से शुरू करो
2. हमेशा सकारात्मक संदेश के साथ समाप्त करो
3. गोपनीयता डिस्क्लेमर शामिल करो: "आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।"
4. सटीक और विस्तृत उत्तर दो
5. यदि जन्म विवरण उपलब्ध नहीं है, तो सामान्य मार्गदर्शन दो
6. हमेशा उम्मीद और सकारात्मकता बनाए रखो
"""


class VedicAstrologyAgent:
    """Vedic Astrology specialized agent"""

    def __init__(self):
        self.system_prompt = VEDIC_ASTROLOGY_SYSTEM_PROMPT

    async def process(
        self,
        user_message: str,
        session_info: SessionInfo,
        conversation_history: List[Dict[str, str]] = []
    ) -> AgentResponse:
        """
        Process a user message through the Vedic Astrology agent.
        Returns an AgentResponse with the reply and any session updates.
        """
        session_updates: Dict[str, Any] = {}
        requires_action = False
        action_type = None
        action_data = None

        try:
            # Build messages for Qwen API
            messages = []

            # Add conversation history (last 15 messages for context)
            for msg in conversation_history[-15:]:
                messages.append(msg)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get response from Qwen API
            response_text = await qwen_service.get_completion_with_retry(
                messages=messages,
                max_tokens=settings.OPENROUTER_MAX_TOKENS,
                temperature=settings.OPENROUTER_TEMPERATURE,
                system_prompt=self.system_prompt
            )

            if not response_text:
                response_text = self._get_fallback_response(user_message)
            else:
                logger.info(f"VedicAstrologyAgent responded: {len(response_text)} chars")

        except Exception as e:
            logger.error(f"VedicAstrologyAgent error: {e}")
            response_text = self._get_fallback_response(user_message)

        return AgentResponse(
            agent_type="vedic_astrology",
            response=response_text,
            session_updates=session_updates,
            requires_action=requires_action,
            action_type=action_type,
            action_data=action_data
        )

    def _get_fallback_response(self, message: str) -> str:
        """Fallback response when OpenAI is unavailable"""
        return f"""🙏 नमस्ते!

मैं ज्योतिष आचार्य हूँ, 100+ वर्षों के अनुभव वाला वैदिक ज्योतिष विशेषज्ञ।

आपका प्रश्न: "{message}"

वर्तमान में मेरी AI सेवा अस्थायी रूप से अनुपलब्ध है। कृपया कुछ देर बाद पुनः प्रयास करें।

🔮 मैं आपकी कुंडली, ग्रह दशा, नक्षत्र, और सभी ज्योतिषीय विषयों में मार्गदर्शन कर सकता हूँ।

📝 अपनी जन्म तिथि, समय और स्थान साझा करें विस्तृत कुंडली विश्लेषण के लिए।

🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।

🙏 ॐ सर्वे भवन्तु सुखिनः"""


# Create singleton instance
vedic_astrology_agent = VedicAstrologyAgent()
