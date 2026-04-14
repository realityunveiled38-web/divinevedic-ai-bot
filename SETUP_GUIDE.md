# 🚀 DivineVedic AI Bot - Setup & Deployment Guide

## ✅ What's Been Updated

Your WhatsApp AI chatbot has been successfully updated to use **Qwen via OpenRouter** instead of OpenAI!

### Key Changes Made:

1. **✅ Config Updated** - Switched from OpenAI to OpenRouter API
   - Model: `qwen/qwen2.5-7b-instruct`
   - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
   
2. **✅ All Agents Updated** - Vedic Astrology, Numerology, and Business Manager now use Qwen
   - New `qwen_service.py` created for centralized API calls
   - All agents use `qwen_service.get_completion_with_retry()`
   
3. **✅ System Prompts Updated** - Matches your exact specification
   - "100+ years experienced Vedic astrologer"
   - Speaks in Hinglish
   - Structures answers in: Past, Present, Future, Remedies
   
4. **✅ Environment Variables Updated** - `.env.example` now uses `OPENROUTER_API_KEY`

5. **✅ WhatsApp Webhook Verified** - Already matches specification perfectly
   - GET endpoint for verification ✅
   - POST endpoint for messages ✅
   - Extracts message and sender ✅
   - Calls Qwen API ✅
   - Sends response back ✅
   - Ignores non-text messages ✅
   - Error handling ✅

---

## 📋 Quick Start Guide

### Step 1: Get Your API Keys

#### 1.1 OpenRouter API Key (for Qwen)
1. Go to https://openrouter.ai/
2. Sign up and get your API key
3. Free tier available with limited credits
4. Copy your key (starts with `sk-or-`)

#### 1.2 WhatsApp Cloud API
1. Go to https://developers.facebook.com/
2. Create a Business App
3. Add WhatsApp product
4. Get:
   - **Phone Number ID**
   - **Access Token** (temporary, get permanent later)
   - **Verify Token** (create your own)

#### 1.3 Firebase (Firestore)
1. Go to https://console.firebase.google.com/
2. Create a new project
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Generate new private key (JSON)
6. Save as `firebase-credentials.json` in project root

#### 1.4 Razorpay (Payments)
1. Go to https://dashboard.razorpay.com/
2. Sign up and get:
   - **Key ID**
   - **Key Secret**

---

### Step 2: Setup Local Environment

#### Option A: Using Existing venv (Recommended)

```bash
# Navigate to project
cd c:\Users\thenu\OneDrive\Desktop\divinevedic-ai-bot

# Activate virtual environment
venv\Scripts\activate

# Copy and edit .env file
copy .env.example .env
```

Now edit `.env` with your actual credentials:

```env
# ---- OpenRouter API (Qwen) ----
OPENROUTER_API_KEY=sk-or-your_actual_key_here
OPENROUTER_MODEL=qwen/qwen2.5-7b-instruct
OPENROUTER_MAX_TOKENS=2000
OPENROUTER_TEMPERATURE=0.7

# ---- WhatsApp Cloud API ----
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_WEBHOOK_URL=https://your-domain.com/chat/webhook/whatsapp

# ---- Firebase / Firestore ----
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# ---- Razorpay ----
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
RAZORPAY_WEBHOOK_URL=https://your-domain.com/webhook/razorpay

# ---- Security ----
API_SECRET_KEY=your_super_secret_key
```

#### Option B: Fresh Install (If venv doesn't work)

If Python 3.14 causes issues, use Python 3.11 or 3.12:

```bash
# Create new venv with Python 3.11/3.12
python -m venv venv_new
venv_new\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Run the Application

```bash
# Activate venv
venv\Scripts\activate

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🙏 Starting DivineVedic AI Bot v2.0.0
Qwen service initialized successfully
WhatsApp service initialized successfully
Firestore initialized: True
Razorpay initialized: True
🙏 All services initialized. DivineVedic AI Bot is ready!
```

---

### Step 4: Test Locally

#### Test 1: Health Check
Open browser: http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 123.45,
  "services": {
    "openrouter_configured": true,
    "whatsapp_configured": true,
    "firestore_configured": true,
    "razorpay_configured": true
  }
}
```

#### Test 2: REST Chat API
```bash
curl -X POST http://localhost:8000/chat/ ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"hello\", \"session_id\": \"test123\"}"
```

Expected: Welcome message with trial info in Hinglish.

#### Test 3: Test Qwen Integration
```bash
curl -X POST http://localhost:8000/chat/ ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What is my future according to astrology?\", \"session_id\": \"test123\"}"
```

Expected: Astrology-based response in Hinglish with Past, Present, Future, Remedies structure.

---

### Step 5: Setup WhatsApp Webhook

#### Option A: Using ngrok (Local Testing)

```bash
# Install ngrok
# Go to https://ngrok.com/ and download

# Run ngrok
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok.io`

#### Option B: Deploy to Railway/Render (Production)

**Railway:**
1. Push code to GitHub
2. Connect repo to Railway
3. Add environment variables
4. Deploy!

**Render:**
1. Push code to GitHub
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy!

---

### Step 6: Configure WhatsApp Webhook URL

1. Go to Meta Developer Console
2. Open your app → WhatsApp → Configuration
3. Set Callback URL:
   - Local: `https://abc123.ngrok.io/chat/webhook/whatsapp`
   - Production: `https://your-domain.railway.app/chat/webhook/whatsapp`
4. Set Verify Token: (same as in your `.env`)
5. Subscribe to: **messages**
6. Click "Verify and Save"

---

### Step 7: Test WhatsApp Integration

1. Send a message to your WhatsApp Business number
2. Check logs for incoming webhook
3. Bot should respond within seconds!

Expected flow:
```
You: Hello
Bot: 🙏 नमस्ते! DivineVedic AI Bot में आपका स्वागत है!
     🎁 आपको 5 मिनट का FREE TRIAL मिला है!
     बताइए, मैं आपकी कैसे सहायता करूँ? 🙏

You: What is my future?
Bot: 🙏 नमस्ते!
     Past: [Detailed prediction]
     Present: [Current situation]
     Future: [Future insights]
     Remedies: [Solutions and mantras]
     🔒 आपकी जानकारी सुरक्षित है। 🙏
```

---

## 🏗️ Architecture Overview

```
User → WhatsApp → Meta Webhook → FastAPI Backend → Qwen API → Response → WhatsApp API
```

### Request Flow:

1. **User sends message on WhatsApp**
2. **Meta forwards to your webhook** (`/chat/webhook/whatsapp`)
3. **FastAPI extracts:**
   - `user_message` = message text
   - `sender` = phone number
4. **Orchestrator routes to appropriate agent:**
   - Vedic Astrology Agent (general queries)
   - Numerology Agent (numerology queries)
   - Business Manager (plans, payments, status)
5. **Agent calls Qwen API** with system prompt + user message
6. **Response sent back** via WhatsApp Cloud API

---

## 📁 Project Structure

```
divinevedic-ai-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Settings (UPDATED: OpenRouter)
│   ├── models.py                  # Pydantic models
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── vedic_astrology_agent.py    # UPDATED: Uses Qwen
│   │   ├── numerology_chaldean_agent.py # UPDATED: Uses Qwen
│   │   ├── business_manager_agent.py    # UPDATED: Uses Qwen
│   │   └── orchestrator.py              # Central coordinator
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                  # WhatsApp webhook
│   │   └── payment.py               # Razorpay webhook
│   └── services/
│       ├── __init__.py
│       ├── qwen_service.py          # ✨ NEW: Qwen API service
│       ├── firestore_service.py     # Google Firestore
│       ├── razorpay_service.py      # Razorpay payments
│       └── whatsapp_service.py      # WhatsApp Cloud API
├── requirements.txt
├── Dockerfile
├── .env.example                     # UPDATED: OpenRouter vars
├── .gitignore
└── README.md                        # UPDATED: Qwen docs
```

---

## 🔧 Qwen API Integration Details

### Endpoint:
```
POST https://openrouter.ai/api/v1/chat/completions
```

### Headers:
```json
{
  "Authorization": "Bearer YOUR_OPENROUTER_API_KEY",
  "Content-Type": "application/json",
  "HTTP-Referer": "https://divinevedic.ai",
  "X-Title": "DivineVedic AI Bot"
}
```

### Request Body:
```json
{
  "model": "qwen/qwen2.5-7b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are a 100+ years experienced Vedic astrologer..."
    },
    {
      "role": "user",
      "content": "What is my future?"
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.7
}
```

### Response Extraction:
```python
response_text = result["choices"][0]["message"]["content"]
```

---

## 🎯 System Prompts (All Updated)

### Vedic Astrology Agent:
```
You are a 100+ years experienced Vedic astrologer. You speak in Hinglish.
You give deep and accurate predictions based on astrology and numerology.
Always structure your answers in: Past, Present, Future, and Remedies.
Be confident and detailed.
```

### Numerology Agent:
```
तुम "संख्या आचार्य" हो - 100+ वर्षों के अनुभव वाले अंकशास्त्र और काल्डियन चार्ट विशेषज्ञ।
[Detailed Hindi prompt with Chaldean number system]
```

### Business Manager:
```
तुम "व्यापार मैनेजर" हो - DivineVedic AI Bot के Business & Conversation Manager।
[Handles subscriptions, payments, talk-time tracking]
```

---

## 🚀 Production Deployment

### Docker Build:
```bash
# Build
docker build -t divinevedic-ai:latest .

# Run
docker run -p 8000:8000 --env-file .env divinevedic-ai
```

### Google Cloud Run:
```bash
# Build and push
docker build -t gcr.io/YOUR_PROJECT/divinevedic-ai:latest .
docker push gcr.io/YOUR_PROJECT/divinevedic-ai:latest

# Deploy
gcloud run deploy divinevedic-ai \
  --image gcr.io/YOUR_PROJECT/divinevedic-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY=your_key,...
```

### Railway (Easiest):
1. Push to GitHub
2. Connect to Railway
3. Add all env variables from `.env.example`
4. Auto-deploys on push!

---

## 🧪 Testing Checklist

- [ ] Health check returns 200 OK
- [ ] Qwen API responds correctly
- [ ] WhatsApp webhook verification succeeds
- [ ] Incoming message triggers webhook
- [ ] Bot responds on WhatsApp within 5 seconds
- [ ] Response is in Hinglish
- [ ] Response includes Past, Present, Future, Remedies
- [ ] Non-text messages are ignored gracefully
- [ ] Error handling works (try with wrong API key)
- [ ] Session tracking works (multiple messages)
- [ ] Trial timer starts correctly
- [ ] Payment flow integrates with Razorpay

---

## 🐛 Troubleshooting

### Qwen API Not Responding
1. Check `OPENROUTER_API_KEY` is correct
2. Verify you have credits at https://openrouter.ai/
3. Check logs: `logger.info(f"Qwen API responded: {len(response_text)} chars")`

### WhatsApp Webhook Not Receiving
1. Verify webhook URL is publicly accessible
2. Check verify token matches
3. Ensure "messages" subscription is enabled
4. Test with ngrok first, then deploy

### Firestore Connection Failed
1. Verify `firebase-credentials.json` exists
2. Check `FIREBASE_PROJECT_ID` matches
3. Enable Firestore API in Google Cloud Console

### Talk Time Not Tracking
1. Check session state is "trial" or "active"
2. Verify `talk_time_used_seconds` updates in Firestore
3. Check orchestrator's `update_talk_time()` function

---

## 📝 Next Steps

1. **Get OpenRouter API Key** → https://openrouter.ai/
2. **Setup WhatsApp Business API** → https://developers.facebook.com/
3. **Deploy to Railway/Render** → Get public URL
4. **Configure Webhook** → Point to your deployment
5. **Test on WhatsApp** → Send your first message!

---

## 🎉 You're All Set!

Your production-ready WhatsApp AI chatbot is now configured with:

✅ **Qwen via OpenRouter** (instead of OpenAI)
✅ **100+ years experienced Vedic astrologer** personality
✅ **Hinglish responses** with Past, Present, Future, Remedies structure
✅ **WhatsApp Cloud API** webhook integration
✅ **Multi-agent system** (Vedic, Numerology, Business)
✅ **Subscription management** (₹199, ₹499, ₹999 plans)
✅ **Talk-time tracking** with expiry
✅ **Payment integration** via Razorpay
✅ **Production-ready** Docker setup

**🙏 ॐ सर्वे भवन्तु सुखिनः**
*May all be happy*

---

Need help? Check the logs or refer to the comprehensive README.md!
