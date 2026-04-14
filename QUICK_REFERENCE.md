# 🎯 Quick Reference Card - DivineVedic AI Bot

## 🚀 Start Bot (Local)
```bash
cd c:\Users\thenu\OneDrive\Desktop\divinevedic-ai-bot
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Test Integration
```bash
python test_app.py
```

## 📋 Key Endpoints
- **Health Check**: `GET /health`
- **API Docs**: `http://localhost:8000/docs`
- **WhatsApp Webhook**: `GET/POST /chat/webhook/whatsapp`
- **Chat API**: `POST /chat/`
- **Payment Create**: `POST /chat/payment/create`
- **Razorpay Webhook**: `POST /webhook/razorpay`

## 🔑 Required Environment Variables
```env
OPENROUTER_API_KEY=sk-or-your_key_here
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=your_project_id
RAZORPAY_KEY_ID=rzp_test_your_key
RAZORPAY_KEY_SECRET=your_secret
```

## 🤖 Agent Routing
- **Astrology queries** → Vedic Astrology Agent
- **Numerology queries** → Numerology Chaldean Agent
- **Plans/Payments/Status** → Business Manager Agent
- **All orchestrated by** → Central Orchestrator

## 💬 WhatsApp Flow
```
User Message → Meta Webhook → FastAPI → Orchestrator → Agent → Qwen API → Response → WhatsApp
```

## 📦 Deploy Options
- **Railway**: Easiest, auto-deploy from GitHub
- **Render**: Simple web service deployment
- **Google Cloud Run**: Production-ready with Docker

## 🐛 Common Issues
- **Qwen not responding**: Check `OPENROUTER_API_KEY` in `.env`
- **Webhook not receiving**: Use ngrok for local testing
- **Firestore error**: Ensure `firebase-credentials.json` exists
- **Port in use**: Change PORT in `.env` or use different port

## 📞 Support
- Full docs: `README.md`
- Setup guide: `SETUP_GUIDE.md`
- Test script: `test_app.py`

---

**🙏 Bot is production-ready! Just add your API keys and deploy!**
