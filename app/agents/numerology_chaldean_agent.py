"""
Numerology & Chaldean Expert Agent - DivineVedic AI Bot
Specialized agent for Mulank, Bhagyank, Chaldean Chart, Name Analysis, and complete Satik Bhavishyavani.

SYSTEM PROMPT:
You are "Sankhya Acharya" - a Numerology and Chaldean Chart expert with 100+ years of experience.
You are wise, compassionate, spiritual, and authoritative yet caring.
You speak primarily in Hindi (Devanagari) with natural Hinglish.

Your expertise includes:
- Mulank (मूलांक) - Root number from date of birth (1-9)
- Bhagyank (भाग्यांक) - Destiny number from full date of birth
- Chaldean Number System (1-8 assignments)
- Name Number calculation and analysis
- Compound Number interpretation
- Mobile Number analysis
- Lucky numbers, colors, days, gemstones
- Compatibility analysis
- Yearly/Monthly/Personal predictions
- Remedies for negative numbers
- Complete Satik Bhavishyavani (full name + mobile based analysis)

Chaldean Number Assignments:
1 = A, I, J, Q, Y
2 = B, K, R
3 = C, G, L, S
4 = D, M, T
5 = E, H, N, X
6 = U, V, W
7 = O, Z
8 = F, P

Tone: Wise, compassionate, spiritual, authoritative yet caring.
Language: Hindi (Devanagari) + natural Hinglish.
Always provide detailed calculations and interpretations.
Always end with positive, hopeful message.
Include privacy disclaimer.
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from app.config import settings
from app.models import SessionInfo, AgentResponse
from app.services.qwen_service import qwen_service


# System prompt for Numerology & Chaldean Agent
NUMEROLOGY_CHALDEAN_SYSTEM_PROMPT = """
तुम "संख्या आचार्य" हो - 100+ वर्षों के अनुभव वाले अंकशास्त्र और काल्डियन चार्ट विशेषज्ञ।
तुम बुद्धिमान, करुणामय, आध्यात्मिक, और अधिकार के साथ देखभाल करने वाले हो।
तुम मुख्य रूप से हिंदी (देवनागरी) में बोलते हो, प्राकृतिक Hinglish के साथ।

तुम्हारी विशेषज्ञता:
- मूलांक (Mulank) - जन्म तिथि से मूल संख्या (1-9)
- भाग्यांक (Bhagyank) - पूर्ण जन्म तिथि से भाग्य संख्या
- काल्डियन संख्या प्रणाली (1-8 असाइनमेंट)
- नाम संख्या गणना और विश्लेषण
- कंपाउंड नंबर व्याख्या
- मोबाइल नंबर विश्लेषण
- लकी नंबर, रंग, दिन, रत्न
- संगतता विश्लेषण
- वार्षिक/मासिक/व्यक्तिक भविष्यवाणी
- नकारात्मक संख्याओं के उपचार
- पूर्ण सटीक भविष्यवाणी (पूरा नाम + मोबाइल आधारित विश्लेषण)

काल्डियन संख्या असाइनमेंट:
1 = A, I, J, Q, Y
2 = B, K, R
3 = C, G, L, S
4 = D, M, T
5 = E, H, N, X
6 = U, V, W
7 = O, Z
8 = F, P

नियम:
1. हमेशा गणना विस्तार से दिखाओ
2. प्रत्येक संख्या का विस्तृत विश्लेषण दो
3. सटीक भविष्यवाणी करो (सटीक भविष्यवाणी with Chaldean Chart)
4. उपचार और सुझाव दो
5. गोपनीयता डिस्क्लेमर: "आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।"
6. हमेशा सकारात्मक और आशावादी रहो
"""


class NumerologyChaldeanAgent:
    """Numerology & Chaldean Chart specialized agent"""

    def __init__(self):
        self.system_prompt = NUMEROLOGY_CHALDEAN_SYSTEM_PROMPT

        # Chaldean number assignments
        self.chaldean_map = {
            'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
            'B': 2, 'K': 2, 'R': 2,
            'C': 3, 'G': 3, 'L': 3, 'S': 3,
            'D': 4, 'M': 4, 'T': 4,
            'E': 5, 'H': 5, 'N': 5, 'X': 5,
            'U': 6, 'V': 6, 'W': 6,
            'O': 7, 'Z': 7,
            'F': 8, 'P': 8
        }

    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client"""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def calculate_mulank(self, birth_date: str) -> int:
        """
        Calculate Mulank (Root Number) from birth date.
        Mulank = Day of birth reduced to single digit (1-9)
        """
        try:
            # Extract day from date (DD/MM/YYYY or DD-MM-YYYY)
            parts = birth_date.replace('-', '/').split('/')
            day = int(parts[0])
            return self._reduce_to_single_digit(day)
        except Exception as e:
            logger.error(f"Error calculating Mulank: {e}")
            return 0

    def calculate_bhagyank(self, birth_date: str) -> int:
        """
        Calculate Bhagyank (Destiny Number) from full date of birth.
        Bhagyank = Sum of all digits of full date reduced to single digit (1-9)
        """
        try:
            parts = birth_date.replace('-', '/').split('/')
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            total = day + month + year
            return self._reduce_to_single_digit(total)
        except Exception as e:
            logger.error(f"Error calculating Bhagyank: {e}")
            return 0

    def calculate_name_number(self, name: str) -> int:
        """
        Calculate Name Number using Chaldean system.
        """
        total = 0
        for char in name.upper():
            if char in self.chaldean_map:
                total += self.chaldean_map[char]
        return self._reduce_to_single_digit(total)

    def calculate_mobile_number_energy(self, mobile: str) -> Dict[str, Any]:
        """
        Calculate mobile number energy/compatibility.
        """
        try:
            digits = [int(d) for d in mobile if d.isdigit()]
            total = sum(digits)
            reduced = self._reduce_to_single_digit(total)

            # Count frequency of each number
            frequency = {}
            for d in digits:
                frequency[d] = frequency.get(d, 0) + 1

            return {
                "total_sum": total,
                "reduced_number": reduced,
                "frequency": frequency,
                "dominant_number": max(frequency, key=frequency.get) if frequency else 0
            }
        except Exception as e:
            logger.error(f"Error calculating mobile energy: {e}")
            return {}

    def _reduce_to_single_digit(self, num: int) -> int:
        """Reduce a number to single digit (1-9), keeping master numbers 11, 22, 33"""
        if num in [11, 22, 33]:
            return num
        while num > 9 and num not in [11, 22, 33]:
            num = sum(int(d) for d in str(num))
        return num if num > 0 else 1

    async def process(
        self,
        user_message: str,
        session_info: SessionInfo,
        conversation_history: List[Dict[str, str]] = []
    ) -> AgentResponse:
        """
        Process a user message through the Numerology & Chaldean agent.
        """
        session_updates: Dict[str, Any] = {}
        requires_action = False
        action_type = None
        action_data = None

        # Pre-calculate numerology if data is available
        numerology_data = {}
        if session_info.user_dob:
            mulank = self.calculate_mulank(session_info.user_dob)
            bhagyank = self.calculate_bhagyank(session_info.user_dob)
            numerology_data["mulank"] = mulank
            numerology_data["bhagyank"] = bhagyank

        if session_info.user_full_name:
            name_number = self.calculate_name_number(session_info.user_full_name)
            numerology_data["name_number"] = name_number

        if session_info.user_mobile_for_numerology:
            mobile_energy = self.calculate_mobile_number_energy(session_info.user_mobile_for_numerology)
            numerology_data["mobile_energy"] = mobile_energy

        try:
            # Build context with pre-calculated data
            context_info = ""
            if numerology_data:
                context_info = f"\n\nUser Numerology Data (pre-calculated):\n{numerology_data}"

            messages = [
                {"role": "system", "content": self.system_prompt + context_info}
            ]

            # Add conversation history
            for msg in conversation_history[-15:]:
                messages.append(msg)

            messages.append({"role": "user", "content": user_message})

            # Get response from Qwen API
            response_text = await qwen_service.get_completion_with_retry(
                messages=messages,
                max_tokens=settings.OPENROUTER_MAX_TOKENS,
                temperature=settings.OPENROUTER_TEMPERATURE,
                system_prompt=self.system_prompt + context_info
            )

            if not response_text:
                response_text = self._get_fallback_response(user_message, numerology_data)
            else:
                logger.info(f"NumerologyChaldeanAgent responded: {len(response_text)} chars")

        except Exception as e:
            logger.error(f"NumerologyChaldeanAgent error: {e}")
            response_text = self._get_fallback_response(user_message, numerology_data)

        return AgentResponse(
            agent_type="numerology_chaldean",
            response=response_text,
            session_updates=session_updates,
            requires_action=requires_action,
            action_type=action_type,
            action_data=action_data
        )

    def _get_fallback_response(self, message: str, numerology_data: Dict) -> str:
        """Fallback response when OpenAI is unavailable"""
        mulank = numerology_data.get("mulank", "अज्ञात")
        bhagyank = numerology_data.get("bhagyank", "अज्ञात")

        return f"""🙏 नमस्ते!

मैं संख्या आचार्य हूँ, 100+ वर्षों के अनुभव वाला अंकशास्त्र विशेषज्ञ।

आपका प्रश्न: "{message}"

📊 आपकी संख्या जानकारी:
- मूलांक: {mulank}
- भाग्यांक: {bhagyank}

वर्तमान में मेरी AI सेवा अस्थायी रूप से अनुपलब्ध है। कृपया कुछ देर बाद पुनः प्रयास करें।

🔮 सटीक भविष्यवाणी with Chaldean Chart के लिए अपना पूरा नाम और मोबाइल नंबर साझा करें।

🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।

🙏 ॐ सर्वे भवन्तु सुखिनः"""


# Create singleton instance
numerology_chaldean_agent = NumerologyChaldeanAgent()
