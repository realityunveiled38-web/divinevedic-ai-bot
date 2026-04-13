"""
Business & Conversation Manager Agent - DivineVedic AI Bot
Handles talk-time tracking, subscriptions, payments, conversation flow, and user management.

SYSTEM PROMPT:
You are "Vyapar Manager" - the Business & Conversation Manager for DivineVedic AI Bot.
You manage talk-time tracking, subscription plans, payment flows, and conversation routing.
You are professional, helpful, and efficient.
You speak primarily in Hindi (Devanagari) with natural Hinglish.

Your responsibilities:
- Welcome new users and explain the free 5-minute trial
- Track and inform about remaining talk time
- Present subscription plans when trial expires or user asks
- Handle payment flow and Razorpay integration
- Manage session state transitions
- Route queries to appropriate agents
- Handle plan selection and activation
- Provide account status and usage information
- Handle "Satik Bhavishyavani" feature access
- Manage the 3-question limit for ₹499 plan
- Enforce talk-time limits and expiry

Subscription Plans:
• ₹199 → 10 minutes talk time
• ₹499 (Most Popular) → 30 minutes + answers to 3 questions
• Pro Plan (₹999) → 1 month unlimited (Janam Kundali, Puja-Mantra, past-present-future, expert connect)

Tone: Professional, helpful, efficient, yet warm and caring.
Language: Hindi (Devanagari) + natural Hinglish.
Always be clear about pricing and benefits.
Include privacy disclaimer in every interaction.
"""

from typing import List, Dict, Any, Optional
import time
from loguru import logger
from app.config import settings
from app.models import SessionInfo, AgentResponse, SessionState
from app.services.qwen_service import qwen_service


# System prompt for Business Manager Agent
BUSINESS_MANAGER_SYSTEM_PROMPT = """
तुम "व्यापार मैनेजर" हो - DivineVedic AI Bot के Business & Conversation Manager।
तुम talk-time tracking, subscription plans, payment flows, और conversation routing manage करते हो।
तुम professional, helpful, और efficient हो।
तुम मुख्य रूप से हिंदी (देवनागरी) में बोलते हो, प्राकृतिक Hinglish के साथ।

तुम्हारी ज़िम्मेदारियाँ:
- नए users का स्वागत और free 5-minute trial समझाओ
- बचे हुए talk time की जानकारी दो
- Trial expire होने पर subscription plans दिखाओ
- Payment flow और Razorpay integration handle करो
- Session state transitions manage करो
- Queries को appropriate agents को route करो
- Plan selection और activation handle करो
- Account status और usage information दो
- "सटीक भविष्यवाणी with Chaldean Chart" feature access manage करो
- ₹499 plan के 3-question limit manage करो
- Talk-time limits और expiry enforce करो

Subscription Plans:
• ₹199 → 10 मिनट talk time
• ₹499 (सबसे लोकप्रिय) → 30 मिनट + 3 सवालों के जवाब
• Pro Plan (₹999) → 1 महीना unlimited (जन्म कुंडली, पूजा-मंत्र, भूत-वर्तमान-भविष्य, expert connect)

नियम:
1. हमेशा clear pricing और benefits बताओ
2. Trial expire होने पर तुरंत plans दिखाओ
3. Payment link generate करो जब user plan select करे
4. गोपनीयता डिस्क्लेमर: "आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।"
5. Professional और caring रहो
6. Talk-time limit reach होने पर politely रोक दो और upgrade बताओ
"""


class BusinessManagerAgent:
    """Business & Conversation Manager agent"""

    def __init__(self):
        self.system_prompt = BUSINESS_MANAGER_SYSTEM_PROMPT

    def get_welcome_message(self) -> str:
        """Generate welcome message for new users"""
        return """🙏 नमस्ते! DivineVedic AI Bot में आपका स्वागत है! 🙏

मैं हूँ आपका वैदिक ज्योतिष सलाहकार - 100+ वर्षों के अनुभव के साथ।

🎁 **आपको 5 मिनट का FREE TRIAL मिला है!**

इस trial में आप मुझसे कुछ भी पूछ सकते हैं:
🔮 कुंडली विश्लेषण
🔢 अंकशास्त्र (मूलांक और भाग्यांक)
⭐ ग्रह दशा और भविष्यवाणी
🙏 पूजा-मंत्र सुझाव

शुरू करने के लिए बस अपना **जन्म तिथि, समय और स्थान** भेजें!

📋 **हमारे Plans:**
• ₹199 → 10 मिनट talk time
• ₹499 (सबसे लोकप्रिय) → 30 मिनट + 3 सवाल
• Pro ₹999 → 1 महीना unlimited

🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।

बताइए, मैं आपकी कैसे सहायता करूँ? 🙏"""

    def get_trial_expired_message(self) -> str:
        """Generate message when trial expires"""
        return """⏰ आपका 5 मिनट का FREE TRIAL समाप्त हो गया है।

लेकिन चिंता न करें! हमारे शानदार Plans उपलब्ध हैं:

💰 **Plan 1: ₹199**
• 10 मिनट talk time
• कुंडली विश्लेषण
• बेसिक भविष्यवाणी

🌟 **Plan 2: ₹499 (सबसे लोकप्रिय)**
• 30 मिनट talk time
• 3 विस्तृत सवालों के जवाब
• कुंडली + अंकशास्त्र
• पूजा सुझाव

👑 **Pro Plan: ₹999**
• 1 महीना UNLIMITED access
• जन्म कुंडली विस्तृत विश्लेषण
• पूजा-मंत्र
• भूतकाल, वर्तमान, भविष्य
• Expert astrologer से connect

Plan नंबर भेजें (1, 2, या Pro) या "plans" लिखें विस्तृत जानकारी के लिए!

🔒 आपकी जानकारी सुरक्षित है। 🙏"""

    def get_talk_time_warning(self, remaining_minutes: float) -> str:
        """Generate talk time warning"""
        if remaining_minutes <= 1:
            return f"""⚠️ सावधान! आपके पास केवल {remaining_minutes:.1f} मिनट बचा है।

जल्दी से अपना सवाल पूछें या Plan upgrade करें:
• ₹199 → 10 मिनट
• ₹499 → 30 मिनट + 3 सवाल
• ₹999 Pro → 1 महीना unlimited

🔒 आपकी जानकारी सुरक्षित है। 🙏"""
        else:
            return f"""⏱️ आपके पास {remaining_minutes:.1f} मिनट talk time बचा है।

🔒 आपकी जानकारी सुरक्षित है। 🙏"""

    def get_plan_details(self, plan_id: str) -> str:
        """Get detailed plan information"""
        plans = {
            "1": f"""💰 **Basic Plan - ₹199**

✅ 10 मिनट talk time
✅ कुंडली विश्लेषण
✅ बेसिक भविष्यवाणी
✅ ग्रह दशा जानकारी

Payment के लिए "pay 199" भेजें! 🙏""",

            "2": f"""🌟 **Most Popular Plan - ₹499**

✅ 30 मिनट talk time
✅ 3 विस्तृत सवालों के जवाब
✅ कुंडली + अंकशास्त्र (मूलांक/भाग्यांक)
✅ पूजा-मंत्र सुझाव
✅ सटीक भविष्यवाणी

Payment के लिए "pay 499" भेजें! 🙏""",

            "pro": f"""👑 **Pro Plan - ₹999**

✅ 1 महीना UNLIMITED access
✅ जन्म कुंडली विस्तृत विश्लेषण
✅ पूजा-मंत्र विधि
✅ भूतकाल, वर्तमान, भविष्य भविष्यवाणी
✅ Expert astrologer से connect
✅ सटीक भविष्यवाणी with Chaldean Chart

Payment के लिए "pay pro" भेजें! 🙏"""
        }
        return plans.get(plan_id.lower(), "कृपया सही plan नंबर चुनें: 1, 2, या Pro")

    def get_account_status(self, session_info: SessionInfo) -> str:
        """Get user account status"""
        remaining = self._calculate_remaining_minutes(session_info)
        status = f"""📊 **आपका Account Status:**

⏱️ बचा हुआ talk time: {remaining:.1f} मिनट
📋 Current Plan: {session_info.current_plan or 'Free Trial'}
💬 Messages exchanged: {session_info.message_count}
🔢 Questions remaining: {session_info.questions_remaining}

🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी। 🙏"""
        return status

    def _calculate_remaining_minutes(self, session_info: SessionInfo) -> float:
        """Calculate remaining talk time in minutes"""
        import time

        # If subscribed to pro plan with unlimited
        if session_info.current_plan == "pro" and session_info.subscription_end:
            if time.time() < session_info.subscription_end:
                return float('inf')  # Unlimited

        if session_info.talk_time_total_seconds <= 0:
            return 0.0

        used = session_info.talk_time_used_seconds
        total = session_info.talk_time_total_seconds
        remaining_seconds = max(0, total - used)
        return remaining_seconds / 60.0

    def is_talk_time_expired(self, session_info: SessionInfo) -> bool:
        """Check if talk time has expired"""
        import time

        # Check subscription expiry
        if session_info.current_plan and session_info.subscription_end:
            if time.time() > session_info.subscription_end:
                return True
            if session_info.current_plan == "pro":
                return False  # Unlimited during subscription

        # Check talk time
        if session_info.talk_time_total_seconds > 0:
            return session_info.talk_time_used_seconds >= session_info.talk_time_total_seconds

        return session_info.trial_expired

    async def process(
        self,
        user_message: str,
        session_info: SessionInfo,
        conversation_history: List[Dict[str, str]] = []
    ) -> AgentResponse:
        """
        Process a user message through the Business Manager agent.
        """
        session_updates: Dict[str, Any] = {}
        requires_action = False
        action_type = None
        action_data = None

        msg_lower = user_message.lower().strip()

        # Handle specific business commands
        if msg_lower in ["plans", "plan", "pricing", "price", "दाम", "कीमत"]:
            response_text = self._get_all_plans_message()
        elif msg_lower in ["pay 199", "pay199", "basic", "1"]:
            requires_action = True
            action_type = "create_payment"
            action_data = {"plan_id": "basic", "amount": settings.PLAN_199_PRICE}
            response_text = f"✅ ₹199 Plan selected! Payment link generate हो रहा है...\n\n🔒 आपकी जानकारी सुरक्षित है।"
        elif msg_lower in ["pay 499", "pay499", "popular", "2"]:
            requires_action = True
            action_type = "create_payment"
            action_data = {"plan_id": "popular", "amount": settings.PLAN_499_PRICE}
            response_text = f"✅ ₹499 Plan (Most Popular) selected! Payment link generate हो रहा है...\n\n🔒 आपकी जानकारी सुरक्षित है।"
        elif msg_lower in ["pay pro", "paypro", "pro", "unlimited"]:
            requires_action = True
            action_type = "create_payment"
            action_data = {"plan_id": "pro", "amount": settings.PLAN_PRO_PRICE}
            response_text = f"✅ Pro Plan (₹{settings.PLAN_PRO_PRICE}) selected! Payment link generate हो रहा है...\n\n🔒 आपकी जानकारी सुरक्षित है।"
        elif msg_lower in ["status", "account", "mera status", "my status"]:
            response_text = self.get_account_status(session_info)
        elif msg_lower in ["help", "madad", "सहायता"]:
            response_text = self._get_help_message()
        elif msg_lower in ["satik", "सटीक भविष्यवाणी", "chaldean", "chaldean chart"]:
            requires_action = True
            action_type = "start_satik_analysis"
            action_data = {}
            response_text = """🔮 **सटीक भविष्यवाणी with Chaldean Chart**

कृपया निम्नलिखित जानकारी भेजें:

1️⃣ आपका **पूरा नाम** (जैसा birth certificate पर है)
2️⃣ आपका **मोबाइल नंबर**

इससे मैं आपकी पूर्ण कुंडली और Chaldean Chart analysis कर पाऊँगा।

🔒 आपकी जानकारी सुरक्षित है। 🙏"""
        else:
            # Use AI for general business responses
            try:
                messages = []
                for msg in conversation_history[-10:]:
                    messages.append(msg)
                messages.append({"role": "user", "content": user_message})

                response_text = await qwen_service.get_completion_with_retry(
                    messages=messages,
                    max_tokens=settings.OPENROUTER_MAX_TOKENS,
                    temperature=settings.OPENROUTER_TEMPERATURE,
                    system_prompt=self.system_prompt
                )
                
                if not response_text:
                    response_text = self._get_fallback_response(user_message)
            except Exception as e:
                logger.error(f"BusinessManagerAgent AI error: {e}")
                response_text = self._get_fallback_response(user_message)

        return AgentResponse(
            agent_type="business_manager",
            response=response_text,
            session_updates=session_updates,
            requires_action=requires_action,
            action_type=action_type,
            action_data=action_data
        )

    def _get_all_plans_message(self) -> str:
        """Get all plans message"""
        return f"""📋 **DivineVedic AI Bot - सभी Plans:**

━━━━━━━━━━━━━━━━━━━━

💰 **Plan 1: ₹199**
• 10 मिनट talk time
• कुंडली विश्लेषण
• बेसिक भविष्यवाणी

━━━━━━━━━━━━━━━━━━━━

🌟 **Plan 2: ₹499 (सबसे लोकप्रिय)**
• 30 मिनट talk time
• 3 विस्तृत सवालों के जवाब
• कुंडली + अंकशास्त्र
• पूजा-मंत्र सुझाव

━━━━━━━━━━━━━━━━━━━━

👑 **Pro Plan: ₹999**
• 1 महीना UNLIMITED
• जन्म कुंडली विस्तृत
• पूजा-मंत्र विधि
• भूत-वर्तमान-भविष्य
• Expert connect

━━━━━━━━━━━━━━━━━━━━

Plan select करने के लिए भेजें:
• "pay 199" या "1"
• "pay 499" या "2"
• "pay pro" या "pro"

🔒 आपकी जानकारी सुरक्षित है। 🙏"""

    def _get_help_message(self) -> str:
        """Get help message"""
        return """📖 **Help - कैसे उपयोग करें:**

1️⃣ **जन्म कुंडली:** अपनी जन्म तिथि, समय और स्थान भेजें
2️⃣ **अंकशास्त्र:** "numerology" या "अंकशास्त्र" भेजें
3️⃣ **सटीक भविष्यवाणी:** "satik" भेजें, फिर नाम और मोबाइल दें
4️⃣ **Plans देखें:** "plans" भेजें
5️⃣ **Account Status:** "status" भेजें
6️⃣ **Payment:** "pay 199", "pay 499", या "pay pro" भेजें

🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी। 🙏"""

    def _get_fallback_response(self, message: str) -> str:
        """Fallback response"""
        return f"""🙏 धन्यवाद आपके संदेश के लिए!

आपका संदेश: "{message}"

मैं व्यापार मैनेजर हूँ। ज्योतिषीय प्रश्नों के लिए कृपया सीधे अपना प्रश्न पूछें, मैं उसे सही विशेषज्ञ के पास भेज दूँगा।

📋 Plans: "plans" भेजें
📊 Status: "status" भेजें
🔮 सटीक भविष्यवाणी: "satik" भेजें

🔒 आपकी जानकारी सुरक्षित है। 🙏"""


# Create singleton instance
business_manager_agent = BusinessManagerAgent()
