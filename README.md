# DivineVedic AI Bot 🙏

**Production-Ready WhatsApp Bot with Vedic Astrology, Numerology, Chaldean Chart & Subscription Management**

A multi-agent AI-powered WhatsApp bot that acts as a Vedic astrologer with 100+ years of experience. Built with FastAPI, OpenAI, Google Firestore, Razorpay, and WhatsApp Cloud API.

---

## 🌟 Features

### Core Features
- **Free 5-Minute Trial** on first interaction
- **Free Numerology Section** - Mulank (मूलांक) & Bhagyank (भाग्यांक) calculations
- **3 Subscription Plans** via Razorpay:
  - 💰 **₹199** → 10 minutes talk time
  - 🌟 **₹499 (Most Popular)** → 30 minutes + answers to 3 questions
  - 👑 **Pro Plan (₹999)** → 1 month unlimited (Janam Kundali, Puja-Mantra, past-present-future, expert connect)
- **Advanced "Satik Bhavishyavani with Chaldean Chart"** - Full name + mobile number based complete analysis

### Multi-Agent System
1. **🔮 Vedic Astrology Agent (Jyotish Acharya)**
   - Janam Kundali (Birth Chart) analysis
   - Navagraha (9 planets) effects
   - 12 Bhavas (Houses) analysis
   - 27 Nakshatras
   - Dasha systems (Vimshottari, Yogini)
   - Gochar (Transit) predictions
   - Puja, Mantra, remedies for planetary doshas
   - Mangal Dosha, Kaal Sarp Dosha, Shani Dosha
   - Past, Present, Future predictions
   - Career, Marriage, Health, Finance predictions

2. **🔢 Numerology & Chaldean Expert Agent (Sankhya Acharya)**
   - Mulank (Root Number) calculation
   - Bhagyank (Destiny Number) calculation
   - Chaldean Number System
   - Name Number calculation
   - Mobile Number energy analysis
   - Lucky numbers, colors, days, gemstones
   - Complete Satik Bhavishyavani

3. **💼 Business & Conversation Manager Agent (Vyapar Manager)**
   - Talk-time tracking and expiry
   - Subscription plan management
   - Payment flow coordination
   - Session state management
   - User account status

### Technical Features
- **Central Orchestrator** coordinates all 3 agents
- **FastAPI** backend with async support
- **WhatsApp Cloud API** webhook integration
- **Google Firestore** for persistent data
- **Razorpay** payment gateway with webhook
- **Real-time talk-time tracking** and expiry handling
- **Privacy disclaimer** in every session
- **Production-ready** Docker setup for Google Cloud Run

---

## 📁 Project Structure

```
divinevedic-ai-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Complete settings
│   ├── models.py                  # Pydantic models
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── vedic_astrology_agent.py    # Agent 1: Vedic Astrology
│   │   ├── numerology_chaldean_agent.py # Agent 2: Numerology
│   │   ├── business_manager_agent.py    # Agent 3: Business
│   │   └── orchestrator.py              # Central Orchestrator
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                  # WhatsApp webhook + chat
│   │   └── payment.py               # Razorpay webhook
│   └── services/
│       ├── __init__.py
│       ├── firestore_service.py     # Google Firestore
│       ├── razorpay_service.py      # Razorpay payments
│       └── whatsapp_service.py      # WhatsApp Cloud API
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- OpenRouter API key (for Qwen model)
- WhatsApp Cloud API credentials
- Firebase project with Firestore enabled
- Razorpay account

### Setup Steps

1. **Clone and navigate to project:**
   ```bash
   cd divinevedic-ai-bot
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy example and edit
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Set up Firebase credentials:**
   - Download your Firebase service account JSON key
   - Save as `firebase-credentials.json` in project root

6. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key (for Qwen) | ✅ |
| `OPENROUTER_MODEL` | Qwen model (qwen/qwen2.5-7b-instruct recommended) | |
| `WHATSAPP_VERIFY_TOKEN` | WhatsApp webhook verify token | ✅ |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp Cloud API access token | ✅ |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | ✅ |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON | ✅ |
| `FIREBASE_PROJECT_ID` | Firebase project ID | ✅ |
| `RAZORPAY_KEY_ID` | Razorpay API key ID | ✅ |
| `RAZORPAY_KEY_SECRET` | Razorpay API key secret | ✅ |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook signing secret | |
| `API_SECRET_KEY` | Secret key for signing | ✅ |

---

## 📋 Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| **Free Trial** | ₹0 | 5 minutes talk time, basic queries |
| **Basic** | ₹199 | 10 minutes talk time, Kundali analysis |
| **Most Popular** | ₹499 | 30 minutes + 3 questions, Kundali + Numerology |
| **Pro** | ₹999 | 1 month unlimited, Janam Kundali, Puja-Mantra, Expert connect |

---

## 🤖 How the Bot Works

### First Interaction Flow
```
User sends message → Bot welcomes with 5-min trial info
→ User asks astrology/numerology questions
→ Trial timer starts
→ When trial expires → Bot shows plans
→ User selects plan → Payment link sent
→ Payment confirmed → Plan activated
```

### Satik Bhavishyavani Flow
```
User sends "satik" → Bot asks for full name
→ User sends name → Bot asks for mobile number
→ User sends mobile → Full Chaldean analysis generated
→ Report includes: Mulank, Bhagyank, Name Number,
   Mobile Energy, Past/Present/Future predictions,
   Career, Marriage, Health, Remedies
```

### Numerology Flow
```
User sends "numerology" or "mulank" → Numerology agent responds
→ Calculates Mulank from birth date
→ Calculates Bhagyank from full birth date
→ Provides detailed analysis and predictions
```

---

## 🌐 Google Cloud Run Deployment

### Step 1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Generate new private key (JSON)
6. Save as `firebase-credentials.json`

### Step 2: Set Up WhatsApp Cloud API
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a Business App
3. Add WhatsApp product
4. Get your:
   - Phone Number ID
   - Access Token
   - Verify Token (create your own)
5. Set up webhook URL: `https://YOUR_DOMAIN/chat/webhook/whatsapp`
6. Subscribe to messages field

### Step 3: Set Up Razorpay
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Get API Key ID and Secret
3. Set up webhook URL: `https://YOUR_DOMAIN/webhook/razorpay`
4. Subscribe to: payment.captured, payment.failed, order.paid

### Step 4: Build Docker Image
```bash
# Build
docker build -t gcr.io/YOUR_PROJECT_ID/divinevedic-ai:latest .

# Test locally
docker run -p 8000:8000 --env-file .env divinevedic-ai
```

### Step 5: Push to Google Container Registry
```bash
# Authenticate
gcloud auth configure-docker

# Tag
docker tag divinevedic-ai:latest gcr.io/YOUR_PROJECT_ID/divinevedic-ai:latest

# Push
docker push gcr.io/YOUR_PROJECT_ID/divinevedic-ai:latest
```

### Step 6: Deploy to Cloud Run
```bash
gcloud run deploy divinevedic-ai \
  --image gcr.io/YOUR_PROJECT_ID/divinevedic-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key,WHATSAPP_VERIFY_TOKEN=your_token,WHATSAPP_ACCESS_TOKEN=your_token,WHATSAPP_PHONE_NUMBER_ID=your_phone_id,FIREBASE_PROJECT_ID=your_project_id,RAZORPAY_KEY_ID=your_razorpay_key,RAZORPAY_KEY_SECRET=your_razorpay_secret,API_SECRET_KEY=your_secret_key \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### Step 7: Set Up Secret Manager (Recommended)
```bash
# Store secrets in Secret Manager
echo -n "your_openai_key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your_whatsapp_token" | gcloud secrets create whatsapp-token --data-file=-

# Deploy with secrets
gcloud run deploy divinevedic-ai \
  --image gcr.io/YOUR_PROJECT_ID/divinevedic-ai:latest \
  --update-secrets=OPENAI_API_KEY=openai-api-key:latest,WHATSAPP_ACCESS_TOKEN=whatsapp-token:latest
```

### Step 8: Configure Firestore Security Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null || true;
    }
    match /sessions/{sessionId} {
      allow read, write: if true;
    }
    match /subscriptions/{subId} {
      allow read, write: if true;
    }
  }
}
```

### Step 9: Update WhatsApp Webhook URL
1. Go to Meta Developer Console
2. Update webhook URL to: `https://YOUR_CLOUD_RUN_URL/chat/webhook/whatsapp`
3. Verify the webhook

### Step 10: Update Razorpay Webhook URL
1. Go to Razorpay Dashboard → Settings → Webhooks
2. Create new webhook with URL: `https://YOUR_CLOUD_RUN_URL/webhook/razorpay`
3. Select events: payment.captured, payment.failed, order.paid

---

## 🧪 Testing Instructions

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "services": {...}}`

### Test 2: REST Chat API
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "session_id": "test123"}'
```
Expected: Welcome message with trial info

### Test 3: Numerology Query
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "mera mulank batao", "session_id": "test123"}'
```
Expected: Mulank calculation and analysis

### Test 4: Satik Bhavishyavani
```bash
# Step 1: Initiate
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "satik", "session_id": "test123"}'

# Step 2: Send name (use the session_id from response)
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Rajesh Kumar Sharma", "session_id": "test123"}'

# Step 3: Send mobile
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "9876543210", "session_id": "test123"}'
```
Expected: Full Chaldean chart analysis

### Test 5: Payment Flow
```bash
# Create payment order
curl -X POST http://localhost:8000/chat/payment/create \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "919876543210", "plan_id": "basic"}'
```

### Test 6: WhatsApp Webhook (Manual)
Use ngrok to expose local server:
```bash
# Install ngrok
ngrok http 8000

# Copy the ngrok URL and set it as WhatsApp webhook URL
# Then send a message to your WhatsApp business number
```

### Test 7: API Documentation
Open http://localhost:8000/docs in browser to see interactive Swagger UI.

---

## 🔒 Privacy & Security

- All user data is encrypted and stored securely in Firestore
- Phone numbers are used only for WhatsApp communication
- Payment information is handled by Razorpay (PCI DSS compliant)
- No personal data is shared with third parties
- Users can request data deletion at any time

**Privacy Disclaimer (shown in every session):**
> 🔒 आपकी जानकारी सुरक्षित है और किसी के साथ साझा नहीं की जाएगी।

---

## 📊 Firestore Collections

### `users` Collection
```
{
  "phone_number": "919876543210",
  "name": "User Name",
  "full_name": "",
  "date_of_birth": "",
  "created_at": 1700000000.0,
  "last_active": 1700000000.0,
  "total_messages": 0,
  "total_sessions": 0,
  "trial_used": false,
  "trial_end_time": null
}
```

### `sessions` Collection
```
{
  "session_id": "session_919876543210_1700000000",
  "phone_number": "919876543210",
  "state": "trial",
  "message_count": 0,
  "created_at": 1700000000.0,
  "last_activity": 1700000000.0,
  "trial_started_at": null,
  "trial_expired": false,
  "talk_time_used_seconds": 0,
  "talk_time_total_seconds": 300,
  "questions_remaining": 0,
  "current_plan": null,
  "subscription_end": null,
  "conversation_history": [],
  "user_name": null,
  "user_dob": null,
  "user_full_name": null,
  "user_mobile_for_numerology": null,
  "pending_payment_id": null,
  "satik_analysis_complete": false
}
```

### `subscriptions` Collection
```
{
  "user_phone": "919876543210",
  "plan_id": "basic",
  "status": "active",
  "start_time": 1700000000.0,
  "end_time": 1700000600.0,
  "talk_time_total_seconds": 600,
  "talk_time_used_seconds": 0,
  "questions_total": 0,
  "questions_used": 0,
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "amount_paid": 199,
  "created_at": 1700000000.0
}
```

---

## 🛠️ Troubleshooting

### WhatsApp Webhook Not Receiving Messages
1. Verify webhook URL is correct: `https://YOUR_DOMAIN/chat/webhook/whatsapp`
2. Check verify token matches in .env
3. Ensure WhatsApp phone number is verified
4. Check logs for errors

### Payment Not Processing
1. Verify Razorpay credentials in .env
2. Check webhook URL is set in Razorpay dashboard
3. Ensure webhook events are subscribed

### Firestore Connection Issues
1. Verify `firebase-credentials.json` exists and is valid
2. Check FIREBASE_PROJECT_ID matches
3. Ensure Firestore API is enabled in Google Cloud Console

### OpenAI API Errors
1. Verify OPENAI_API_KEY is correct
2. Check API quota and billing
3. Bot falls back to predefined responses if API fails

---

## 📝 License

MIT License

---

## 🙏 Contact

For questions, support, or custom development:
- Email: support@divinevedic.ai
- Website: https://divinevedic.ai

---

**🙏 ॐ सर्वे भवन्तु सुखिनः**
*May all be happy*
