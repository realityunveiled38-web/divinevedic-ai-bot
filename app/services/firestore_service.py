"""
Firestore Service - DivineVedic AI Bot
Handles all Firestore database operations for users, sessions, and subscriptions.
"""

import os
import time
from typing import Optional, Dict, Any, List
from loguru import logger
import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings
from app.models import SessionInfo, UserProfile, Subscription


class FirestoreService:
    """Service for Firestore database operations"""

    def __init__(self):
        self.db: Optional[firestore.Client] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Firebase Admin SDK"""
        try:
            if self._initialized:
                return True

            # Check if running in Cloud Run with default credentials
            if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for Cloud Run with service account)
                try:
                    firebase_admin.initialize_app()
                except ValueError:
                    logger.warning("Firebase already initialized")

            self.db = firestore.client()
            self._initialized = True
            logger.info("Firestore service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            return False

    # ============================================
    # User Operations
    # ============================================

    async def get_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user profile by phone number"""
        try:
            if not self.db:
                return None
            doc_ref = self.db.collection("users").document(phone_number)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user {phone_number}: {e}")
            return None

    async def create_user(self, phone_number: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user profile"""
        try:
            if not self.db:
                return {}
            user_data = {
                "phone_number": phone_number,
                "name": name or "",
                "full_name": "",
                "date_of_birth": "",
                "created_at": time.time(),
                "last_active": time.time(),
                "total_messages": 0,
                "total_sessions": 0,
                "trial_used": False,
                "trial_end_time": None
            }
            self.db.collection("users").document(phone_number).set(user_data)
            logger.info(f"Created user: {phone_number}")
            return user_data
        except Exception as e:
            logger.error(f"Error creating user {phone_number}: {e}")
            return {}

    async def update_user(self, phone_number: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            if not self.db:
                return False
            updates["last_active"] = time.time()
            self.db.collection("users").document(phone_number).update(updates)
            return True
        except Exception as e:
            logger.error(f"Error updating user {phone_number}: {e}")
            return False

    async def increment_user_messages(self, phone_number: str) -> bool:
        """Increment user's total message count"""
        try:
            if not self.db:
                return False
            doc_ref = self.db.collection("users").document(phone_number)
            doc_ref.update({
                "total_messages": firestore.Increment(1),
                "last_active": time.time()
            })
            return True
        except Exception as e:
            logger.error(f"Error incrementing messages for {phone_number}: {e}")
            return False

    # ============================================
    # Session Operations
    # ============================================

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by session ID"""
        try:
            if not self.db:
                return None
            doc_ref = self.db.collection("sessions").document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None

    async def create_session(self, session_id: str, phone_number: str) -> Dict[str, Any]:
        """Create a new session"""
        try:
            if not self.db:
                return {}
            now = time.time()
            session_data = {
                "session_id": session_id,
                "phone_number": phone_number,
                "state": "new",
                "message_count": 0,
                "created_at": now,
                "last_activity": now,
                "trial_started_at": None,
                "trial_expired": False,
                "talk_time_used_seconds": 0,
                "talk_time_total_seconds": 300,  # 5 min trial
                "questions_remaining": 0,
                "current_plan": None,
                "subscription_end": None,
                "conversation_history": [],
                "user_name": None,
                "user_dob": None,
                "user_full_name": None,
                "user_mobile_for_numerology": None,
                "pending_payment_id": None,
                "satik_analysis_complete": False
            }
            self.db.collection("sessions").document(session_id).set(session_data)
            logger.info(f"Created session: {session_id}")
            return session_data
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            return {}

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            if not self.db:
                return False
            updates["last_activity"] = time.time()
            self.db.collection("sessions").document(session_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False

    async def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to session conversation history"""
        try:
            if not self.db:
                return False
            doc_ref = self.db.collection("sessions").document(session_id)
            doc_ref.update({
                "conversation_history": firestore.ArrayUnion([
                    {"role": role, "content": content, "timestamp": time.time()}
                ]),
                "message_count": firestore.Increment(1),
                "last_activity": time.time()
            })
            return True
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False

    async def get_active_sessions(self, phone_number: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            if not self.db:
                return []
            query = (
                self.db.collection("sessions")
                .where("phone_number", "==", phone_number)
                .where("state", "in", ["trial", "active", "subscribed", "satik_analysis"])
                .order_by("last_activity", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error getting active sessions for {phone_number}: {e}")
            return []

    # ============================================
    # Subscription Operations
    # ============================================

    async def get_active_subscription(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get active subscription for a user"""
        try:
            if not self.db:
                return None
            now = time.time()
            query = (
                self.db.collection("subscriptions")
                .where("user_phone", "==", phone_number)
                .where("status", "==", "active")
                .limit(1)
            )
            docs = query.stream()
            for doc in docs:
                data = doc.to_dict()
                # Check if subscription is still valid
                if data.get("end_time") and now > data["end_time"]:
                    # Expire the subscription
                    self.db.collection("subscriptions").document(doc.id).update({
                        "status": "expired"
                    })
                    return None
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting subscription for {phone_number}: {e}")
            return None

    async def create_subscription(self, phone_number: str, plan_id: str, amount: int) -> Optional[str]:
        """Create a new subscription record, returns subscription ID"""
        try:
            if not self.db:
                return None
            now = time.time()
            sub_data = {
                "user_phone": phone_number,
                "plan_id": plan_id,
                "status": "pending",
                "start_time": now,
                "end_time": None,
                "talk_time_total_seconds": 0,
                "talk_time_used_seconds": 0,
                "questions_total": 0,
                "questions_used": 0,
                "razorpay_order_id": None,
                "razorpay_payment_id": None,
                "razorpay_signature": None,
                "amount_paid": amount,
                "created_at": now
            }
            doc_ref = self.db.collection("subscriptions").document()
            doc_ref.set(sub_data)
            logger.info(f"Created subscription: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating subscription for {phone_number}: {e}")
            return None

    async def update_subscription(self, sub_id: str, updates: Dict[str, Any]) -> bool:
        """Update subscription record"""
        try:
            if not self.db:
                return False
            self.db.collection("subscriptions").document(sub_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Error updating subscription {sub_id}: {e}")
            return False

    async def activate_subscription(self, sub_id: str, payment_id: str, plan_id: str) -> bool:
        """Activate a subscription after successful payment"""
        try:
            if not self.db:
                return False
            now = time.time()
            plan = settings.get_plan(plan_id)
            if not plan:
                return False

            updates = {
                "status": "active",
                "razorpay_payment_id": payment_id,
                "start_time": now
            }

            # Set end time based on plan
            if plan_id == "basic":
                updates["end_time"] = now + (settings.PLAN_199_DURATION_MINUTES * 60)
                updates["talk_time_total_seconds"] = settings.PLAN_199_DURATION_MINUTES * 60
            elif plan_id == "popular":
                updates["end_time"] = now + (settings.PLAN_499_DURATION_MINUTES * 60)
                updates["talk_time_total_seconds"] = settings.PLAN_499_DURATION_MINUTES * 60
                updates["questions_total"] = settings.PLAN_499_QUESTIONS
                updates["questions_used"] = 0
            elif plan_id == "pro":
                updates["end_time"] = now + (settings.PLAN_PRO_DURATION_DAYS * 86400)
                updates["talk_time_total_seconds"] = 0  # Unlimited
                updates["questions_total"] = 0  # Unlimited

            self.db.collection("subscriptions").document(sub_id).update(updates)
            logger.info(f"Activated subscription: {sub_id}")
            return True
        except Exception as e:
            logger.error(f"Error activating subscription {sub_id}: {e}")
            return False

    async def get_subscription_by_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription by Razorpay order ID"""
        try:
            if not self.db:
                return None
            query = (
                self.db.collection("subscriptions")
                .where("razorpay_order_id", "==", order_id)
                .limit(1)
            )
            docs = query.stream()
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting subscription by order {order_id}: {e}")
            return None

    # ============================================
    # SessionInfo Conversion
    # ============================================

    def dict_to_session_info(self, data: Dict[str, Any]) -> SessionInfo:
        """Convert Firestore dict to SessionInfo model"""
        return SessionInfo(
            session_id=data.get("session_id", ""),
            phone_number=data.get("phone_number", ""),
            state=data.get("state", "new"),
            message_count=data.get("message_count", 0),
            created_at=data.get("created_at", time.time()),
            last_activity=data.get("last_activity", time.time()),
            trial_started_at=data.get("trial_started_at"),
            trial_expired=data.get("trial_expired", False),
            talk_time_used_seconds=data.get("talk_time_used_seconds", 0),
            talk_time_total_seconds=data.get("talk_time_total_seconds", 300),
            questions_remaining=data.get("questions_remaining", 0),
            current_plan=data.get("current_plan"),
            subscription_end=data.get("subscription_end"),
            conversation_history=data.get("conversation_history", []),
            user_name=data.get("user_name"),
            user_dob=data.get("user_dob"),
            user_full_name=data.get("user_full_name"),
            user_mobile_for_numerology=data.get("user_mobile_for_numerology"),
            pending_payment_id=data.get("pending_payment_id"),
            satik_analysis_complete=data.get("satik_analysis_complete", False)
        )

    def session_info_to_dict(self, session_info: SessionInfo) -> Dict[str, Any]:
        """Convert SessionInfo to dict for Firestore storage"""
        return {
            "session_id": session_info.session_id,
            "phone_number": session_info.phone_number,
            "state": session_info.state,
            "message_count": session_info.message_count,
            "created_at": session_info.created_at,
            "last_activity": session_info.last_activity,
            "trial_started_at": session_info.trial_started_at,
            "trial_expired": session_info.trial_expired,
            "talk_time_used_seconds": session_info.talk_time_used_seconds,
            "talk_time_total_seconds": session_info.talk_time_total_seconds,
            "questions_remaining": session_info.questions_remaining,
            "current_plan": session_info.current_plan,
            "subscription_end": session_info.subscription_end,
            "conversation_history": session_info.conversation_history,
            "user_name": session_info.user_name,
            "user_dob": session_info.user_dob,
            "user_full_name": session_info.user_full_name,
            "user_mobile_for_numerology": session_info.user_mobile_for_numerology,
            "pending_payment_id": session_info.pending_payment_id,
            "satik_analysis_complete": session_info.satik_analysis_complete
        }


# Singleton instance
firestore_service = FirestoreService()
