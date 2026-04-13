"""
WhatsApp Service - DivineVedic AI Bot
Handles sending messages via WhatsApp Cloud API.
"""

from typing import Optional, Dict, Any, List
import requests
from loguru import logger

from app.config import settings


class WhatsAppService:
    """Service for WhatsApp Cloud API operations"""

    def __init__(self):
        self.base_url = settings.WHATSAPP_API_BASE_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize WhatsApp service"""
        if not self.access_token or not self.phone_number_id:
            logger.warning("WhatsApp credentials not set - messaging will not work")
            return False

        self._initialized = True
        logger.info("WhatsApp service initialized successfully")
        return True

    async def send_text_message(
        self,
        recipient_phone: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp user.
        """
        try:
            if not self._initialized:
                return {"success": False, "error": "WhatsApp service not initialized"}

            # Clean phone number (remove + and spaces)
            recipient_phone = recipient_phone.replace("+", "").replace(" ", "")

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "text",
                "text": {
                    "body": message,
                    "preview_url": False
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Message sent to {recipient_phone}: {result.get('messages', [{}])[0].get('id', 'unknown')}")

            return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            return {"success": False, "error": str(e)}

    async def send_template_message(
        self,
        recipient_phone: str,
        template_name: str,
        language_code: str = "hi",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a template message to a WhatsApp user.
        """
        try:
            if not self._initialized:
                return {"success": False, "error": "WhatsApp service not initialized"}

            recipient_phone = recipient_phone.replace("+", "").replace(" ", "")

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }

            if components:
                payload["template"]["components"] = components

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Template message sent to {recipient_phone}")

            return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}

        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {e}")
            return {"success": False, "error": str(e)}

    async def send_message_with_buttons(
        self,
        recipient_phone: str,
        header_text: str,
        body_text: str,
        footer_text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Send an interactive message with buttons.
        buttons format: [{"id": "1", "title": "Plan 1"}, {"id": "2", "title": "Plan 2"}]
        """
        try:
            if not self._initialized:
                return {"success": False, "error": "WhatsApp service not initialized"}

            recipient_phone = recipient_phone.replace("+", "").replace(" ", "")

            url = f"{self.base_url}/{self.phone_number_id}/messages"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Build buttons array
            button_objects = []
            for btn in buttons[:3]:  # Max 3 buttons
                button_objects.append({
                    "type": "reply",
                    "reply": {
                        "id": btn["id"],
                        "title": btn["title"][:20]  # Max 20 chars
                    }
                })

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": {"type": "text", "text": header_text},
                    "body": {"text": body_text},
                    "footer": {"text": footer_text},
                    "action": {
                        "buttons": button_objects
                    }
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Button message sent to {recipient_phone}")

            return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}

        except Exception as e:
            logger.error(f"Error sending WhatsApp button message: {e}")
            return {"success": False, "error": str(e)}

    async def send_payment_message(
        self,
        recipient_phone: str,
        plan_name: str,
        amount: int,
        payment_url: str
    ) -> Dict[str, Any]:
        """
        Send a payment link message to a WhatsApp user.
        """
        message = f"""💰 **{plan_name}**

राशि: ₹{amount}

Payment करने के लिए नीचे दिए गए link पर click करें:
🔗 {payment_url}

Payment complete होने के बाद आपका Plan तुरंत activate हो जाएगा!

🔒 आपकी जानकारी सुरक्षित है। 🙏"""

        return await self.send_text_message(recipient_phone, message)


# Singleton instance
whatsapp_service = WhatsAppService()
