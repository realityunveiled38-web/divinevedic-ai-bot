"""
Pydantic Models for Request/Response Validation - DivineVedic AI Bot
Complete models for WhatsApp, Payments, Sessions, Subscriptions, and Agents
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# WhatsApp Webhook Models
# ============================================

class WhatsAppWebhookVerification(BaseModel):
    """WhatsApp webhook verification request"""
    hub_mode: Optional[str] = Field(None, alias="hub.mode")
    hub_token: Optional[str] = Field(None, alias="hub.token")
    hub_challenge: Optional[str] = Field(None, alias="hub.challenge")


class WhatsAppTextMessage(BaseModel):
    """WhatsApp text message body"""
    body: str = ""


class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message"""
    from_: str = Field("", alias="from")
    id: str = ""
    timestamp: Optional[str] = None
    text: Optional[WhatsAppTextMessage] = None
    type: str = "text"


class WhatsAppContact(BaseModel):
    """WhatsApp contact info"""
    profile: Dict[str, Any] = {}
    wa_id: str = ""


class WhatsAppStatus(BaseModel):
    """WhatsApp message status"""
    id: str = ""
    status: str = ""
    timestamp: str = ""
    recipient_id: str = ""


class WhatsAppEntry(BaseModel):
    """WhatsApp webhook entry"""
    changes: List[Dict[str, Any]] = []


class WhatsAppWebhookPayload(BaseModel):
    """Full WhatsApp webhook payload"""
    object: str = ""
    entry: List[WhatsAppEntry] = []


# ============================================
# Chat & Session Models
# ============================================

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    phone_number: Optional[str] = Field(None, description="User phone number")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: Optional[str] = None
    timestamp: float
    model_used: Optional[str] = None
    agent_used: Optional[str] = None
    talk_time_remaining: Optional[int] = None
    questions_remaining: Optional[int] = None


class SessionState(str, Enum):
    """Session state enumeration"""
    NEW = "new"
    TRIAL = "trial"
    TRIAL_EXPIRED = "trial_expired"
    ACTIVE = "active"
    SUBSCRIBED = "subscribed"
    EXPIRED = "expired"
    AWAITING_PAYMENT = "awaiting_payment"
    AWAITING_NAME = "awaiting_name"
    AWAITING_NUMEROLOGY = "awaiting_numerology"
    AWAITING_PLAN_SELECTION = "awaiting_plan_selection"
    SATIK_ANALYSIS = "satik_analysis"


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    phone_number: str
    state: str = SessionState.NEW
    message_count: int = 0
    created_at: float = 0.0
    last_activity: float = 0.0
    trial_started_at: Optional[float] = None
    trial_expired: bool = False
    talk_time_used_seconds: int = 0
    talk_time_total_seconds: int = 300  # 5 min trial
    questions_remaining: int = 0
    current_plan: Optional[str] = None
    subscription_end: Optional[float] = None
    conversation_history: List[Dict[str, str]] = []
    user_name: Optional[str] = None
    user_dob: Optional[str] = None
    user_full_name: Optional[str] = None  # For Satik Bhavishyavani
    user_mobile_for_numerology: Optional[str] = None  # For Satik Bhavishyavani
    pending_payment_id: Optional[str] = None
    satik_analysis_complete: bool = False


# ============================================
# User Models
# ============================================

class UserProfile(BaseModel):
    """User profile stored in Firestore"""
    phone_number: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    created_at: float = 0.0
    last_active: float = 0.0
    total_messages: int = 0
    total_sessions: int = 0
    trial_used: bool = False
    trial_end_time: Optional[float] = None


# ============================================
# Subscription Models
# ============================================

class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    TRIAL = "trial"
    BASIC = "basic"
    POPULAR = "popular"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Subscription(BaseModel):
    """Subscription model"""
    user_phone: str
    plan_id: str
    status: str = SubscriptionStatus.PENDING
    start_time: float = 0.0
    end_time: Optional[float] = None
    talk_time_total_seconds: int = 0
    talk_time_used_seconds: int = 0
    questions_total: int = 0
    questions_used: int = 0
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    amount_paid: int = 0
    created_at: float = 0.0


# ============================================
# Payment Models
# ============================================

class PaymentOrderRequest(BaseModel):
    """Request to create a payment order"""
    phone_number: str
    plan_id: str = Field(..., description="Plan ID: basic, popular, pro")


class PaymentOrderResponse(BaseModel):
    """Response after creating payment order"""
    success: bool
    order_id: str
    amount: int
    currency: str
    key_id: str
    plan_name: str
    razorpay_order: Dict[str, Any] = {}


class RazorpayWebhookPayload(BaseModel):
    """Razorpay webhook payload"""
    event: str
    payload: Dict[str, Any] = {}
    account_id: str = ""


class PaymentVerificationRequest(BaseModel):
    """Request to verify payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    phone_number: str
    plan_id: str


class PaymentVerificationResponse(BaseModel):
    """Response after payment verification"""
    success: bool
    message: str
    subscription: Optional[Subscription] = None


# ============================================
# Agent Models
# ============================================

class AgentType(str, Enum):
    """Available agent types"""
    VEDIC_ASTROLOGY = "vedic_astrology"
    NUMEROLOGY_CHALDEAN = "numerology_chaldean"
    BUSINESS_MANAGER = "business_manager"


class AgentRequest(BaseModel):
    """Request to an agent"""
    agent_type: AgentType
    user_message: str
    session_info: SessionInfo
    conversation_history: List[Dict[str, str]] = []


class AgentResponse(BaseModel):
    """Response from an agent"""
    agent_type: AgentType
    response: str
    session_updates: Dict[str, Any] = {}
    requires_action: bool = False
    action_type: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None


# ============================================
# Satik Bhavishyavani Models
# ============================================

class SatikAnalysisRequest(BaseModel):
    """Request for Satik Bhavishyavani analysis"""
    full_name: str = Field(..., min_length=2, description="User's full name")
    mobile_number: str = Field(..., min_length=10, description="User's mobile number")
    phone_number: str = Field(..., description="WhatsApp phone number")


class SatikAnalysisResponse(BaseModel):
    """Response for Satik Bhavishyavani"""
    mulank: int = 0
    bhagyank: int = 0
    chaldean_chart: Dict[str, Any] = {}
    name_analysis: str = ""
    mobile_analysis: str = ""
    predictions: Dict[str, str] = {}
    remedies: List[str] = []
    full_report: str = ""


# ============================================
# Health & Status Models
# ============================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime: float
    openrouter_configured: bool
    whatsapp_configured: bool
    firestore_configured: bool
    razorpay_configured: bool


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    status_code: int
    timestamp: float
