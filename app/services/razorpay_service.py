"""
Razorpay Payment Service - DivineVedic AI Bot
Handles payment order creation, verification, and webhook processing.
"""

import time
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from loguru import logger
import razorpay

from app.config import settings
from app.services.firestore_service import firestore_service


class RazorpayService:
    """Service for Razorpay payment operations"""

    def __init__(self):
        self.client: Optional[razorpay.Client] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Razorpay client"""
        try:
            if self._initialized:
                return True

            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                logger.warning("Razorpay credentials not set - payments will not work")
                return False

            self.client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            self._initialized = True
            logger.info("Razorpay service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Razorpay: {e}")
            return False

    async def create_payment_order(
        self,
        phone_number: str,
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Create a Razorpay payment order for a subscription plan.
        Returns order details for the client to initiate payment.
        """
        try:
            if not self.client:
                return {"success": False, "error": "Razorpay not initialized"}

            # Get plan details
            plan = settings.get_plan(plan_id)
            if not plan:
                return {"success": False, "error": f"Invalid plan: {plan_id}"}

            amount = plan["price"]
            plan_name = plan["name"]

            # Create subscription record in Firestore
            sub_id = await firestore_service.create_subscription(
                phone_number=phone_number,
                plan_id=plan_id,
                amount=amount
            )

            # Create Razorpay order
            order_data = {
                "amount": amount * 100,  # Razorpay expects amount in paise
                "currency": "INR",
                "receipt": f"receipt_{sub_id}_{int(time.time())}",
                "notes": {
                    "phone_number": phone_number,
                    "plan_id": plan_id,
                    "subscription_id": sub_id,
                    "app_name": settings.APP_NAME
                }
            }

            order = self.client.order.create(data=order_data)

            # Update subscription with order ID
            if sub_id:
                await firestore_service.update_subscription(sub_id, {
                    "razorpay_order_id": order["id"]
                })

            logger.info(f"Created payment order: {order['id']} for {phone_number}")

            return {
                "success": True,
                "order_id": order["id"],
                "amount": amount,
                "currency": "INR",
                "key_id": settings.RAZORPAY_KEY_ID,
                "plan_name": plan_name,
                "subscription_id": sub_id,
                "razorpay_order": order
            }

        except Exception as e:
            logger.error(f"Error creating payment order: {e}")
            return {"success": False, "error": str(e)}

    def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature.
        Returns True if signature is valid.
        """
        try:
            if not self.client:
                return False

            # Verify signature
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })

            logger.info(f"Payment signature verified for order: {order_id}")
            return True

        except Exception as e:
            logger.error(f"Payment signature verification failed: {e}")
            return False

    async def handle_payment_success(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
        phone_number: str,
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Handle successful payment - verify signature and activate subscription.
        """
        try:
            # Verify signature
            if not self.verify_payment_signature(order_id, payment_id, signature):
                return {
                    "success": False,
                    "message": "❌ Payment verification failed. Invalid signature."
                }

            # Activate subscription
            sub_id = await self._get_subscription_by_order(order_id)
            if not sub_id:
                return {
                    "success": False,
                    "message": "❌ Subscription not found. Please contact support."
                }

            activated = await firestore_service.activate_subscription(
                sub_id=sub_id,
                payment_id=payment_id,
                plan_id=plan_id
            )

            if activated:
                plan = settings.get_plan(plan_id)
                return {
                    "success": True,
                    "message": f"""✅ Payment Successful! 🎉

💰 Amount: ₹{plan['price']}
📋 Plan: {plan['name']}
🔑 Payment ID: {payment_id}

आपका Plan activate हो गया है! अब आप सभी features use कर सकते हैं।

🔮 ज्योतिषीय प्रश्न पूछें या "help" भेजें मार्गदर्शन के लिए।

🔒 आपकी जानकारी सुरक्षित है। 🙏""",
                    "subscription_id": sub_id
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Payment verified but subscription activation failed. Please contact support."
                }

        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return {
                "success": False,
                "message": f"❌ Payment processing error: {str(e)}"
            }

    async def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Razorpay webhook events.
        """
        try:
            event = event_data.get("event", "")
            payload = event_data.get("payload", {})

            logger.info(f"Received Razorpay webhook event: {event}")

            if event == "payment.captured":
                payment = payload.get("payment", {}).get("entity", {})
                order_id = payment.get("order_id", "")
                payment_id = payment.get("id", "")

                # Update subscription
                sub_id = await self._get_subscription_by_order(order_id)
                if sub_id:
                    await firestore_service.update_subscription(sub_id, {
                        "razorpay_payment_id": payment_id,
                        "status": "active"
                    })

            elif event == "payment.failed":
                payment = payload.get("payment", {}).get("entity", {})
                order_id = payment.get("order_id", "")

                sub_id = await self._get_subscription_by_order(order_id)
                if sub_id:
                    await firestore_service.update_subscription(sub_id, {
                        "status": "failed"
                    })

            elif event == "order.paid":
                order = payload.get("order", {}).get("entity", {})
                order_id = order.get("id", "")

                sub_id = await self._get_subscription_by_order(order_id)
                if sub_id:
                    await firestore_service.update_subscription(sub_id, {
                        "status": "paid"
                    })

            return {"success": True}

        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"success": False, "error": str(e)}

    async def _get_subscription_by_order(self, order_id: str) -> Optional[str]:
        """Get subscription ID by Razorpay order ID"""
        try:
            if not firestore_service.db:
                return None

            query = (
                firestore_service.db.collection("subscriptions")
                .where("razorpay_order_id", "==", order_id)
                .limit(1)
            )
            docs = query.stream()
            for doc in docs:
                return doc.id
            return None
        except Exception as e:
            logger.error(f"Error getting subscription by order {order_id}: {e}")
            return None

    def generate_payment_link(
        self,
        phone_number: str,
        plan_id: str,
        customer_name: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a Razorpay payment link that can be sent via WhatsApp.
        """
        try:
            if not self.client:
                return {"success": False, "error": "Razorpay not initialized"}

            plan = settings.get_plan(plan_id)
            if not plan:
                return {"success": False, "error": f"Invalid plan: {plan_id}"}

            amount = plan["price"]
            plan_name = plan["name"]

            # Create order
            order_data = {
                "amount": amount * 100,
                "currency": "INR",
                "receipt": f"receipt_{phone_number}_{int(time.time())}",
                "notes": {
                    "phone_number": phone_number,
                    "plan_id": plan_id,
                    "app_name": settings.APP_NAME
                }
            }

            order = self.client.order.create(data=order_data)

            # Generate payment URL
            payment_url = f"https://razorpay.me/@{settings.RAZORPAY_KEY_ID}"

            return {
                "success": True,
                "order_id": order["id"],
                "amount": amount,
                "plan_name": plan_name,
                "payment_url": payment_url,
                "short_url": f"https://rzp.io/i/{order['id'][-6:]}" if order.get("id") else payment_url
            }

        except Exception as e:
            logger.error(f"Error generating payment link: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
razorpay_service = RazorpayService()
