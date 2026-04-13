"""
Payment Routes - DivineVedic AI Bot
Razorpay webhook endpoint for payment events.
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.services.razorpay_service import razorpay_service
from app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/webhook", tags=["Webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    """
    Razorpay webhook endpoint for payment events.
    Handles: payment.captured, payment.failed, order.paid
    """
    try:
        # Get raw body for signature verification
        raw_body = await request.body()
        body = await request.json()

        # Verify webhook signature if configured
        if settings.WEBHOOK_SIGNATURE_VERIFICATION and settings.RAZORPAY_WEBHOOK_SECRET:
            signature = request.headers.get("X-Razorpay-Signature", "")
            if not verify_razorpay_signature(raw_body, signature):
                logger.warning("Invalid Razorpay webhook signature")
                return JSONResponse(
                    content={"error": "Invalid signature"},
                    status_code=401
                )

        event = body.get("event", "")
        logger.info(f"Received Razorpay webhook event: {event}")

        # Handle the webhook event
        result = await razorpay_service.handle_webhook_event(body)

        # Send notification to user based on event
        payload = body.get("payload", {})

        if event == "payment.captured":
            payment = payload.get("payment", {}).get("entity", {})
            phone_number = payment.get("notes", {}).get("phone_number", "")
            plan_id = payment.get("notes", {}).get("plan_id", "")

            if phone_number:
                plan = settings.get_plan(plan_id) if plan_id else None
                plan_name = plan["name"] if plan else "Your Plan"
                await whatsapp_service.send_text_message(
                    phone_number,
                    f"""✅ Payment Successful! 🎉

💰 Plan: {plan_name}
🔑 Payment ID: {payment.get("id", "")}

आपका Plan activate हो गया है!

🔮 अब ज्योतिषीय प्रश्न पूछें या "help" भेजें।

🔒 आपकी जानकारी सुरक्षित है। 🙏"""
                )

        elif event == "payment.failed":
            payment = payload.get("payment", {}).get("entity", {})
            phone_number = payment.get("notes", {}).get("phone_number", "")

            if phone_number:
                await whatsapp_service.send_text_message(
                    phone_number,
                    """❌ Payment Failed

क्षमा करें, आपका payment process नहीं हो सका।

कृपया पुनः प्रयास करें या "plans" भेजें नए payment link के लिए।

🔒 आपकी जानकारी सुरक्षित है। 🙏"""
                )

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        logger.error(f"Error processing Razorpay webhook: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)


def verify_razorpay_signature(raw_body: bytes, signature: str) -> bool:
    """Verify Razorpay webhook signature"""
    import hmac
    import hashlib

    try:
        expected = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"Error verifying Razorpay signature: {e}")
        return False
