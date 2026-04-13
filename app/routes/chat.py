"""
Chat Routes - DivineVedic AI Bot
WhatsApp Cloud API webhook and chat endpoint with full conversation logic.
"""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.models import SessionInfo, SessionState
from app.agents.orchestrator import orchestrator
from app.services.firestore_service import firestore_service
from app.services.razorpay_service import razorpay_service
from app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/chat", tags=["Chat"])


# ============================================
# WhatsApp Webhook Routes
# ============================================

@router.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(
    hub_mode: Optional[str] = None,
    hub_token: Optional[str] = None,
    hub_challenge: Optional[str] = None
):
    """
    WhatsApp Cloud API webhook verification endpoint.
    GET request for verification.
    """
    logger.info(f"WhatsApp webhook verification: mode={hub_mode}, token={hub_token}")

    if (
        hub_mode == "subscribe"
        and hub_token == settings.WHATSAPP_VERIFY_TOKEN
    ):
        logger.info("WhatsApp webhook verified successfully")
        return int(hub_challenge) if hub_challenge else 200

    logger.warning("WhatsApp webhook verification failed")
    return Response(status_code=403)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook_event(request: Request):
    """
    WhatsApp Cloud API webhook event handler.
    POST request for incoming messages and status updates.
    """
    try:
        body = await request.json()
        logger.info(f"Received WhatsApp webhook: {body}")

        # Extract message from webhook payload
        entry = body.get("entry", [])
        if not entry:
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        for entry_item in entry:
            changes = entry_item.get("changes", [])
            for change in changes:
                value = change.get("value", {})

                # Check for messages
                messages = value.get("messages", [])
                if messages:
                    for message in messages:
                        await handle_whatsapp_message(message, value)

                # Check for status updates
                statuses = value.get("statuses", [])
                if statuses:
                    for status in statuses:
                        await handle_message_status(status)

        return JSONResponse(content={"status": "received"}, status_code=200)

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)


async def handle_whatsapp_message(message: dict, value: dict):
    """Handle an incoming WhatsApp message"""
    try:
        phone_number = message.get("from", "")
        message_type = message.get("type", "text")

        # Only handle text messages
        if message_type != "text":
            await whatsapp_service.send_text_message(
                phone_number,
                "🙏 कृपया text message भेजें। मैं आपका ज्योतिष सलाहकार हूँ।"
            )
            return

        user_message = message.get("text", {}).get("body", "").strip()
        if not user_message:
            return

        logger.info(f"Message from {phone_number}: {user_message}")

        # Get or create user profile
        user = await firestore_service.get_user(phone_number)
        if not user:
            await firestore_service.create_user(phone_number)

        # Get or create session
        sessions = await firestore_service.get_active_sessions(phone_number)
        if sessions:
            session_data = sessions[0]
            session_info = firestore_service.dict_to_session_info(session_data)
        else:
            session_id = f"session_{phone_number}_{int(time.time())}"
            session_data = await firestore_service.create_session(session_id, phone_number)
            session_info = firestore_service.dict_to_session_info(session_data)

        # Store user message in conversation history
        await firestore_service.add_message_to_session(
            session_info.session_id, "user", user_message
        )

        # Process message through orchestrator
        response_text, session_updates = await orchestrator.process_message(
            user_message, session_info
        )

        # Update session in Firestore
        if session_updates:
            await firestore_service.update_session(session_info.session_id, session_updates)

        # Store assistant response in conversation history
        await firestore_service.add_message_to_session(
            session_info.session_id, "assistant", response_text
        )

        # Update user message count
        await firestore_service.increment_user_messages(phone_number)

        # Track talk time for active sessions
        if session_info.state in [SessionState.TRIAL, SessionState.ACTIVE, SessionState.SUBSCRIBED]:
            # Estimate talk time based on message length (rough estimate: 1 char = 0.1 seconds)
            estimated_duration = max(5, len(user_message) * 0.1)
            talk_time_update = orchestrator.update_talk_time(session_info, int(estimated_duration))
            await firestore_service.update_session(
                session_info.session_id,
                {"talk_time_used_seconds": talk_time_update["talk_time_used_seconds"]}
            )

        # Send response via WhatsApp
        # Split long messages into chunks (WhatsApp has ~4096 char limit)
        chunks = split_message(response_text, 4000)
        for chunk in chunks:
            await whatsapp_service.send_text_message(phone_number, chunk)

    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {e}")
        try:
            phone_number = message.get("from", "")
            await whatsapp_service.send_text_message(
                phone_number,
                "❌ क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।"
            )
        except Exception:
            pass


async def handle_message_status(status: dict):
    """Handle message status update (sent, delivered, read)"""
    try:
        message_id = status.get("id", "")
        status_type = status.get("status", "")
        recipient_id = status.get("recipient_id", "")

        logger.info(f"Message {message_id} status: {status_type} for {recipient_id}")

    except Exception as e:
        logger.error(f"Error handling message status: {e}")


def split_message(message: str, max_length: int) -> list:
    """Split a long message into chunks"""
    if len(message) <= max_length:
        return [message]

    chunks = []
    while len(message) > max_length:
        # Find a good split point (newline or space)
        split_at = message.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = message.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length

        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()

    if message:
        chunks.append(message)

    return chunks


# ============================================
# REST Chat Endpoint (for testing and direct API access)
# ============================================

@router.post("/")
async def chat_endpoint(request: Request):
    """
    REST chat endpoint for testing and direct API access.
    """
    try:
        body = await request.json()
        user_message = body.get("message", "").strip()
        session_id = body.get("session_id") or f"rest_{uuid.uuid4().hex[:12]}"
        phone_number = body.get("phone_number", "")

        if not user_message:
            return JSONResponse(
                content={"error": "Message cannot be empty"},
                status_code=400
            )

        # Get or create session
        if phone_number:
            sessions = await firestore_service.get_active_sessions(phone_number)
            if sessions:
                session_data = sessions[0]
                session_info = firestore_service.dict_to_session_info(session_data)
            else:
                session_data = await firestore_service.create_session(session_id, phone_number)
                session_info = firestore_service.dict_to_session_info(session_data)
        else:
            # In-memory session for REST API
            session_info = SessionInfo(
                session_id=session_id,
                phone_number=phone_number or "rest_user",
                state=SessionState.NEW,
                message_count=0,
                created_at=time.time(),
                last_activity=time.time()
            )

        # Process through orchestrator
        response_text, session_updates = await orchestrator.process_message(
            user_message, session_info
        )

        # Update session if Firestore is available
        if phone_number and session_updates:
            await firestore_service.update_session(session_info.session_id, session_updates)

        return JSONResponse(content={
            "response": response_text,
            "session_id": session_info.session_id,
            "timestamp": time.time(),
            "talk_time_remaining": session_updates.get("talk_time_remaining"),
            "questions_remaining": session_updates.get("questions_remaining")
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# ============================================
# Payment Routes
# ============================================

@router.post("/payment/create")
async def create_payment(request: Request):
    """Create a Razorpay payment order"""
    try:
        body = await request.json()
        phone_number = body.get("phone_number", "").strip()
        plan_id = body.get("plan_id", "").strip()

        if not phone_number or not plan_id:
            return JSONResponse(
                content={"error": "phone_number and plan_id are required"},
                status_code=400
            )

        result = await razorpay_service.create_payment_order(phone_number, plan_id)

        if result.get("success"):
            # Send payment link via WhatsApp
            payment_url = f"https://razorpay.me/@{settings.RAZORPAY_KEY_ID}"
            await whatsapp_service.send_payment_message(
                phone_number,
                result.get("plan_name", "Plan"),
                result.get("amount", 0),
                payment_url
            )

            return JSONResponse(content={
                "success": True,
                "order_id": result.get("order_id"),
                "amount": result.get("amount"),
                "plan_name": result.get("plan_name"),
                "message": "Payment link sent to your WhatsApp! 📱"
            })
        else:
            return JSONResponse(
                content={"error": result.get("error", "Payment creation failed")},
                status_code=500
            )

    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/payment/verify")
async def verify_payment(request: Request):
    """Verify a Razorpay payment"""
    try:
        body = await request.json()
        order_id = body.get("razorpay_order_id", "")
        payment_id = body.get("razorpay_payment_id", "")
        signature = body.get("razorpay_signature", "")
        phone_number = body.get("phone_number", "")
        plan_id = body.get("plan_id", "")

        if not all([order_id, payment_id, signature, phone_number, plan_id]):
            return JSONResponse(
                content={"error": "All payment details are required"},
                status_code=400
            )

        result = await razorpay_service.handle_payment_success(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            phone_number=phone_number,
            plan_id=plan_id
        )

        if result.get("success"):
            # Send confirmation via WhatsApp
            await whatsapp_service.send_text_message(
                phone_number,
                result.get("message", "✅ Payment successful!")
            )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
