"""
Central Orchestrator - DivineVedic AI Bot
Coordinates all 3 specialized agents and manages conversation flow.

The Orchestrator:
1. Receives user messages
2. Determines which agent should handle the request
3. Routes to the appropriate agent
4. Manages session state transitions
5. Handles talk-time tracking and subscription enforcement
6. Coordinates the Satik Bhavishyavani flow
7. Manages the free trial and plan upgrades
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from app.config import settings
from app.models import (
    SessionInfo, AgentResponse, SessionState, AgentType
)
from app.agents.vedic_astrology_agent import VedicAstrologyAgent, vedic_astrology_agent
from app.agents.numerology_chaldean_agent import NumerologyChaldeanAgent, numerology_chaldean_agent
from app.agents.business_manager_agent import BusinessManagerAgent, business_manager_agent


class CentralOrchestrator:
    """Central Orchestrator that coordinates all agents"""

    def __init__(self):
        self.vedic_agent = vedic_astrology_agent
        self.numerology_agent = numerology_chaldean_agent
        self.business_agent = business_manager_agent

    async def process_message(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process a user message and return (response_text, session_updates).
        This is the main entry point for all conversation.
        """
        # Update session activity
        session_info.last_activity = time.time()
        session_info.message_count += 1

        # Check if this is a new session
        if session_info.state == SessionState.NEW:
            return await self._handle_new_session(user_message, session_info)

        # Check if awaiting name for Satik analysis
        if session_info.state == SessionState.AWAITING_NAME:
            return await self._handle_awaiting_name(user_message, session_info)

        # Check if awaiting numerology input
        if session_info.state == SessionState.AWAITING_NUMEROLOGY:
            return await self._handle_awaiting_numerology(user_message, session_info)

        # Check if awaiting plan selection
        if session_info.state == SessionState.AWAITING_PLAN_SELECTION:
            return await self._handle_awaiting_plan_selection(user_message, session_info)

        # Check if trial expired
        if session_info.trial_expired or self.business_agent.is_talk_time_expired(session_info):
            return await self._handle_expired_session(user_message, session_info)

        # Check if subscribed
        if session_info.state == SessionState.SUBSCRIBED:
            return await self._handle_subscribed_session(user_message, session_info)

        # Check if in Satik analysis mode
        if session_info.state == SessionState.SATIK_ANALYSIS:
            return await self._handle_satik_analysis(user_message, session_info)

        # Default: handle active session (trial or active)
        return await self._handle_active_session(user_message, session_info)

    async def _handle_new_session(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle first-time user interaction"""
        # Start trial
        session_info.state = SessionState.TRIAL
        session_info.trial_started_at = time.time()
        session_info.talk_time_total_seconds = settings.TRIAL_DURATION_MINUTES * 60

        # Get welcome message from business agent
        welcome = self.business_agent.get_welcome_message()

        session_updates = {
            "state": SessionState.TRIAL,
            "trial_started_at": session_info.trial_started_at,
            "talk_time_total_seconds": session_info.talk_time_total_seconds
        }

        return welcome, session_updates

    async def _handle_awaiting_name(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle user providing full name for Satik analysis"""
        session_info.user_full_name = user_message.strip()
        session_updates = {"user_full_name": session_info.user_full_name}

        # Now ask for mobile number
        response = f"""✅ आपका नाम "{session_info.user_full_name}" सेव हो गया।

अब कृपया अपना **मोबाइल नंबर** भेजें (10 अंकों का):

🔮 इसके बाद मैं आपकी पूर्ण सटीक भविष्यवाणी with Chaldean Chart तैयार करूँगा।

🔒 आपकी जानकारी सुरक्षित है। 🙏"""

        session_info.state = SessionState.AWAITING_NUMEROLOGY
        session_updates["state"] = SessionState.AWAITING_NUMEROLOGY

        return response, session_updates

    async def _handle_awaiting_numerology(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle user providing mobile number for Satik analysis"""
        # Validate mobile number
        mobile = re.sub(r'[^0-9]', '', user_message.strip())
        if len(mobile) < 10:
            return """❌ कृपया सही 10 अंकों का मोबाइल नंबर भेजें।

उदाहरण: 9876543210

🔒 आपकी जानकारी सुरक्षित है। 🙏""", {}

        session_info.user_mobile_for_numerology = mobile
        session_info.state = SessionState.SATIK_ANALYSIS
        session_updates = {
            "user_mobile_for_numerology": mobile,
            "state": SessionState.SATIK_ANALYSIS
        }

        # Now perform Satik analysis
        return await self._perform_satik_analysis(session_info)

    async def _handle_awaiting_plan_selection(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle plan selection after trial expired"""
        # Delegate to business agent
        response = await self.business_agent.process(
            user_message, session_info, session_info.conversation_history
        )

        session_updates = response.session_updates

        # If payment action required, handle it
        if response.requires_action and response.action_type == "create_payment":
            # This will be handled by the payment service
            pass

        return response.response, session_updates

    async def _handle_expired_session(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle session when trial/subscription has expired"""
        msg_lower = user_message.lower().strip()

        # If user asks for plans or tries to pay, handle it
        if msg_lower in ["plans", "plan", "pricing", "price", "दाम", "कीमत",
                          "pay 199", "pay199", "pay 499", "pay499", "pay pro", "paypro",
                          "1", "2", "pro", "basic", "popular", "unlimited"]:
            response = await self.business_agent.process(
                user_message, session_info, session_info.conversation_history
            )
            return response.response, response.session_updates

        # Show trial expired message with plans
        session_info.state = SessionState.AWAITING_PLAN_SELECTION
        session_updates = {"state": SessionState.AWAITING_PLAN_SELECTION}

        return self.business_agent.get_trial_expired_message(), session_updates

    async def _handle_subscribed_session(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle active subscribed session"""
        msg_lower = user_message.lower().strip()

        # Check for specific commands
        if msg_lower in ["status", "account", "mera status", "my status"]:
            response_text = self.business_agent.get_account_status(session_info)
            return response_text, {}

        if msg_lower in ["plans", "plan", "pricing", "upgrade"]:
            response = await self.business_agent.process(
                user_message, session_info, session_info.conversation_history
            )
            return response.response, response.session_updates

        if msg_lower in ["satik", "सटीक भविष्यवाणी", "chaldean", "chaldean chart"]:
            session_info.state = SessionState.AWAITING_NAME
            session_updates = {"state": SessionState.AWAITING_NAME}
            return """🔮 **सटीक भविष्यवाणी with Chaldean Chart**

कृपया अपना **पूरा नाम** भेजें (जैसा birth certificate पर है):

🔒 आपकी जानकारी सुरक्षित है। 🙏""", session_updates

        if msg_lower in ["numerology", "अंकशास्त्र", "mulank", "मूलांक", "bhagyank", "भाग्यांक"]:
            # Route to numerology agent
            response = await self.numerology_agent.process(
                user_message, session_info, session_info.conversation_history
            )
            return response.response, response.session_updates

        # Check question limit for ₹499 plan
        if session_info.current_plan == "popular" and session_info.questions_remaining <= 0:
            # Check if this looks like a question
            if '?' in user_message or any(word in msg_lower for word in ['क्या', 'कैसे', 'क्यों', 'कब', 'where', 'what', 'how', 'why', 'when']):
                return """❌ आपके ₹499 Plan में 3 सवाल की limit पूरी हो गई है।

लेकिन आप अभी भी सामान्य ज्योतिषीय चर्चा जारी रख सकते हैं!

👉 Pro Plan upgrade करें unlimited सवालों के लिए:
"pay pro" भेजें

🔒 आपकी जानकारी सुरक्षित है। 🙏""", {}

        # Default: route to vedic astrology agent
        response = await self.vedic_agent.process(
            user_message, session_info, session_info.conversation_history
        )

        # Update question count for popular plan
        if session_info.current_plan == "popular":
            if '?' in user_message or any(word in msg_lower for word in ['क्या', 'कैसे', 'क्यों', 'कब', 'where', 'what', 'how', 'why', 'when']):
                session_info.questions_remaining = max(0, session_info.questions_remaining - 1)
                response.session_updates["questions_remaining"] = session_info.questions_remaining

        return response.response, response.session_updates

    async def _handle_active_session(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle active trial or general session"""
        msg_lower = user_message.lower().strip()

        # Check for specific commands
        if msg_lower in ["plans", "plan", "pricing", "price", "दाम", "कीमत"]:
            response = await self.business_agent.process(
                user_message, session_info, session_info.conversation_history
            )
            return response.response, response.session_updates

        if msg_lower in ["status", "account", "mera status", "my status"]:
            response_text = self.business_agent.get_account_status(session_info)
            return response_text, {}

        if msg_lower in ["satik", "सटीक भविष्यवाणी", "chaldean", "chaldean chart"]:
            session_info.state = SessionState.AWAITING_NAME
            session_updates = {"state": SessionState.AWAITING_NAME}
            return """🔮 **सटीक भविष्यवाणी with Chaldean Chart**

कृपया अपना **पूरा नाम** भेजें (जैसा birth certificate पर है):

🔒 आपकी जानकारी सुरक्षित है। 🙏""", session_updates

        if msg_lower in ["numerology", "अंकशास्त्र", "mulank", "मूलांक", "bhagyank", "भाग्यांक"]:
            # Route to numerology agent
            response = await self.numerology_agent.process(
                user_message, session_info, session_info.conversation_history
            )
            return response.response, response.session_updates

        if msg_lower in ["help", "madad", "सहायता"]:
            response_text = self.business_agent._get_help_message()
            return response_text, {}

        # Check talk time and warn if low
        remaining_minutes = self.business_agent._calculate_remaining_minutes(session_info)
        warning = ""
        if remaining_minutes <= 2 and remaining_minutes > 0:
            warning = self.business_agent.get_talk_time_warning(remaining_minutes) + "\n\n"

        # Route to appropriate agent based on message content
        agent_response = await self._route_to_agent(user_message, session_info)

        # Add warning if needed
        full_response = warning + agent_response.response

        return full_response, agent_response.session_updates

    async def _handle_satik_analysis(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Handle Satik Bhavishyavani analysis"""
        msg_lower = user_message.lower().strip()

        # If user wants to exit satik mode
        if msg_lower in ["exit", "back", "वापस", "बाहर"]:
            session_info.state = SessionState.ACTIVE
            session_updates = {"state": SessionState.ACTIVE}
            return "✅ सटीक भविष्यवाणी mode से बाहर आ गए।\n\nअब आप सामान्य ज्योतिषीय प्रश्न पूछ सकते हैं। 🙏", session_updates

        # Perform the full Satik analysis
        return await self._perform_satik_analysis(session_info)

    async def _perform_satik_analysis(
        self,
        session_info: SessionInfo
    ) -> Tuple[str, Dict[str, Any]]:
        """Perform complete Satik Bhavishyavani with Chaldean Chart"""
        full_name = session_info.user_full_name or ""
        mobile = session_info.user_mobile_for_numerology or ""

        if not full_name or not mobile:
            return """❌ विश्लेषण के लिए नाम और मोबाइल नंबर दोनों आवश्यक हैं।

कृपया पुनः "satik" भेजें और जानकारी दें। 🙏""", {}

        # Calculate numerology values
        mulank = 0
        bhagyank = 0
        if session_info.user_dob:
            mulank = self.numerology_agent.calculate_mulank(session_info.user_dob)
            bhagyank = self.numerology_agent.calculate_bhagyank(session_info.user_dob)

        name_number = self.numerology_agent.calculate_name_number(full_name)
        mobile_energy = self.numerology_agent.calculate_mobile_number_energy(mobile)

        # Build detailed Satik analysis prompt
        satik_prompt = f"""
तुम "ज्योतिष आचार्य" हो - 100+ वर्षों के अनुभव वाले वैदिक ज्योतिष और अंकशास्त्र विशेषज्ञ।

अब तुम्हें पूर्ण **सटीक भविष्यवाणी with Chaldean Chart** करनी है।

User Details:
- पूरा नाम: {full_name}
- मोबाइल नंबर: {mobile}
- मूलांक: {mulank}
- भाग्यांक: {bhagyank}
- नाम संख्या (Chaldean): {name_number}
- मोबाइल ऊर्जा: {mobile_energy}

Chaldean Number Assignments:
1 = A, I, J, Q, Y
2 = B, K, R
3 = C, G, L, S
4 = D, M, T
5 = E, H, N, X
6 = U, V, W
7 = O, Z
8 = F, P

कृपया निम्नलिखित विस्तृत विश्लेषण दें:

1️⃣ **नाम विश्लेषण** - नाम की संख्या और उसका प्रभाव
2️⃣ **मूलांक विश्लेषण** - मूलांक {mulank} का विस्तृत विश्लेषण
3️⃣ **भाग्यांक विश्लेषण** - भाग्यांक {bhagyank} का विस्तृत विश्लेषण
4️⃣ **Chaldean Chart Analysis** - नाम के प्रत्येक अक्षर का Chaldean मान
5️⃣ **मोबाइल नंबर विश्लेषण** - मोबाइल नंबर की ऊर्जा
6️⃣ **भूतकाल भविष्यवाणी** - Past predictions
7️⃣ **वर्तमान भविष्यवाणी** - Present predictions
8️⃣ **भविष्य भविष्यवाणी** - Future predictions
9️⃣ **करियर और वित्त** - Career and finance
1️⃣0️⃣ **विवाह और संबंध** - Marriage and relationships
1️⃣1️⃣ **स्वास्थ्य** - Health predictions
1️⃣2️⃣ **उपाय और सुझाव** - Remedies and suggestions

हर section विस्तृत और सटीक हो।
भाषा: हिंदी (देवनागरी) + Hinglish
टोन: बुद्धिमान, करुणामय, आध्यात्मिक

अंत में गोपनीयता डिस्क्लेमर जोड़ें।
"""

        try:
            from app.services.qwen_service import qwen_service

            messages = [
                {"role": "user", "content": f"कृपया मेरी पूर्ण सटीक भविष्यवाणी with Chaldean Chart करें। नाम: {full_name}, मोबाइल: {mobile}"}
            ]

            analysis_text = await qwen_service.get_completion_with_retry(
                messages=messages,
                max_tokens=4000,
                temperature=0.7,
                system_prompt=satik_prompt
            )

            if not analysis_text:
                raise Exception("Empty response from Qwen API")

            session_info.satik_analysis_complete = True
            session_info.state = SessionState.ACTIVE
            session_updates = {
                "satik_analysis_complete": True,
                "state": SessionState.ACTIVE
            }

            return f"""🔮 **सटीक भविष्यवाणी with Chaldean Chart - पूर्ण रिपोर्ट**
━━━━━━━━━━━━━━━━━━━━━━━━

नाम: {full_name}
मोबाइल: {mobile}
मूलांक: {mulank} | भाग्यांक: {bhagyank} | नाम संख्या: {name_number}

━━━━━━━━━━━━━━━━━━━━━━━━

{analysis_text}

━━━━━━━━━━━━━━━━━━━━━━━━
🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी। 🙏""", session_updates

        except Exception as e:
            logger.error(f"Satik analysis error: {e}")
            return """❌ सटीक भविष्यवाणी generate करने में त्रुटि हुई।

कृपया कुछ देर बाद पुनः प्रयास करें।

🔒 आपकी जानकारी सुरक्षित है। 🙏""", {}

    async def _route_to_agent(
        self,
        user_message: str,
        session_info: SessionInfo
    ) -> AgentResponse:
        """Route message to the appropriate agent based on content"""
        msg_lower = user_message.lower().strip()

        # Numerology keywords
        numerology_keywords = [
            "numerology", "अंकशास्त्र", "mulank", "मूलांक", "bhagyank", "भाग्यांक",
            "name number", "नाम संख्या", "chaldean", "काल्डियन", "lucky number",
            "lucky color", "शुभ अंक", "शुभ रंग", "compatibility", "संगतता"
        ]

        # Check if numerology query
        if any(kw in msg_lower for kw in numerology_keywords):
            return await self.numerology_agent.process(
                user_message, session_info, session_info.conversation_history
            )

        # Default to Vedic Astrology for all other queries
        return await self.vedic_agent.process(
            user_message, session_info, session_info.conversation_history
        )

    def update_talk_time(self, session_info: SessionInfo, duration_seconds: int) -> Dict[str, Any]:
        """Update talk time usage for a session"""
        session_info.talk_time_used_seconds += duration_seconds
        return {
            "talk_time_used_seconds": session_info.talk_time_used_seconds,
            "talk_time_remaining": max(0, session_info.talk_time_total_seconds - session_info.talk_time_used_seconds)
        }

    def activate_subscription(
        self,
        session_info: SessionInfo,
        plan_id: str
    ) -> Dict[str, Any]:
        """Activate a subscription for a user"""
        plan = settings.get_plan(plan_id)
        if not plan:
            return {"error": "Invalid plan"}

        now = time.time()
        session_info.current_plan = plan_id
        session_info.state = SessionState.SUBSCRIBED
        session_info.trial_expired = False

        updates = {
            "current_plan": plan_id,
            "state": SessionState.SUBSCRIBED,
            "trial_expired": False
        }

        if plan_id == "basic":
            session_info.talk_time_total_seconds = settings.PLAN_199_DURATION_MINUTES * 60
            session_info.talk_time_used_seconds = 0
            session_info.subscription_end = now + (settings.PLAN_199_DURATION_MINUTES * 60)
            updates["talk_time_total_seconds"] = session_info.talk_time_total_seconds
            updates["talk_time_used_seconds"] = 0
            updates["subscription_end"] = session_info.subscription_end

        elif plan_id == "popular":
            session_info.talk_time_total_seconds = settings.PLAN_499_DURATION_MINUTES * 60
            session_info.talk_time_used_seconds = 0
            session_info.questions_remaining = settings.PLAN_499_QUESTIONS
            session_info.subscription_end = now + (settings.PLAN_499_DURATION_MINUTES * 60)
            updates["talk_time_total_seconds"] = session_info.talk_time_total_seconds
            updates["talk_time_used_seconds"] = 0
            updates["questions_remaining"] = session_info.questions_remaining
            updates["subscription_end"] = session_info.subscription_end

        elif plan_id == "pro":
            session_info.talk_time_total_seconds = 0  # Unlimited
            session_info.talk_time_used_seconds = 0
            session_info.questions_remaining = 0  # Unlimited
            session_info.subscription_end = now + (settings.PLAN_PRO_DURATION_DAYS * 86400)
            updates["talk_time_total_seconds"] = 0
            updates["talk_time_used_seconds"] = 0
            updates["questions_remaining"] = 0
            updates["subscription_end"] = session_info.subscription_end

        return updates


# Create singleton instance
orchestrator = CentralOrchestrator()
