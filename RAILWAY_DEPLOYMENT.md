# 🚂 Railway Deployment Checklist

## ✅ Pre-Deployment Verification

### Files Ready:
- ✅ `app/main.py` - FastAPI entry point with `app = FastAPI()`
- ✅ `requirements.txt` - All dependencies listed
- ✅ `Procfile` - Railway start command
- ✅ `railway.json` - Railway configuration
- ✅ `.gitignore` - Properly excludes sensitive files
- ✅ `Dockerfile` - Alternative deployment option

### Code Verified:
- ✅ FastAPI instance named `app` exists in `app/main.py`
- ✅ Server binds to `0.0.0.0` and uses `$PORT` environment variable
- ✅ Health check endpoint at `/health`
- ✅ All imports are correct
- ✅ No syntax errors

---

## 📋 Railway Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app/
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `divinevedic-ai-bot`

### Step 3: Configure Environment Variables
Add these in Railway → Settings → Variables:

#### Required:
```
OPENROUTER_API_KEY=sk-or-your_key_here
WHATSAPP_VERIFY_TOKEN=your_custom_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
FIREBASE_PROJECT_ID=your_firebase_project_id
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
API_SECRET_KEY=your_random_secret_key
```

#### Optional:
```
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_id
WHATSAPP_WEBHOOK_URL=https://your-project.railway.app/chat/webhook/whatsapp
RAZORPAY_WEBHOOK_URL=https://your-project.railway.app/webhook/razorpay
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
DEBUG=False
LOG_LEVEL=INFO
```

### Step 4: Deploy
1. Railway will auto-detect the build
2. Click "Deploy"
3. Wait for build to complete (~2-3 minutes)
4. Copy your public URL (e.g., `https://your-project.up.railway.app`)

### Step 5: Configure WhatsApp Webhook
1. Go to Meta Developer Console
2. Set webhook URL: `https://your-project.up.railway.app/chat/webhook/whatsapp`
3. Set verify token: (same as `WHATSAPP_VERIFY_TOKEN` in Railway)
4. Subscribe to: `messages`
5. Click "Verify and Save"

### Step 6: Configure Razorpay Webhook
1. Go to Razorpay Dashboard → Settings → Webhooks
2. Create webhook with URL: `https://your-project.up.railway.app/webhook/razorpay`
3. Select events: `payment.captured`, `payment.failed`, `order.paid`
4. Copy webhook secret and add to Railway as `RAZORPAY_WEBHOOK_SECRET`

### Step 7: Test
1. Open: `https://your-project.up.railway.app/health`
2. Expected: `{"status": "healthy", ...}`
3. Send a WhatsApp message to your business number
4. Bot should respond within seconds!

---

## 🔧 Deployment Configuration

### Build Command:
```bash
pip install -r requirements.txt
```

### Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Health Check:
```
GET /health
```

---

## 📊 Project Structure (Railway-Ready)

```
divinevedic-ai-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              ← FastAPI entry point (app = FastAPI())
│   ├── config.py
│   ├── models.py
│   ├── agents/
│   ├── routes/
│   └── services/
├── requirements.txt         ← All dependencies
├── Procfile                 ← web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
├── railway.json             ← Railway configuration
├── Dockerfile               ← Alternative deployment
├── .gitignore               ← Excludes .env, venv, etc.
└── README.md                ← Documentation
```

---

## ⚠️ Important Notes

### Firebase Credentials:
For production, you have two options:

**Option 1: Use Google Cloud Service Account (Recommended)**
- Railway runs on Google Cloud
- It will use default credentials automatically
- Just set `FIREBASE_PROJECT_ID` correctly

**Option 2: Upload credentials as Railway variable**
1. Base64 encode your `firebase-credentials.json`
2. Add as `FIREBASE_CREDENTIALS_JSON` in Railway
3. Update code to read from environment variable

### Security:
- ✅ `.env` is in `.gitignore` (never commit!)
- ✅ `firebase-credentials.json` is in `.gitignore`
- ✅ All secrets stored in Railway Variables
- ✅ Railway encrypts all environment variables

### Scaling:
- Railway auto-scales based on traffic
- Set max instances in Railway Settings → Scaling
- Recommended: 1-3 instances for this bot

---

## 🧪 Post-Deployment Testing

### Test 1: Health Check
```bash
curl https://your-project.up.railway.app/health
```

### Test 2: REST Chat API
```bash
curl -X POST https://your-project.up.railway.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

### Test 3: WhatsApp Webhook
Send a message to your WhatsApp business number and verify response.

---

## 🎉 You're Ready!

All files are prepared and verified. Follow the steps above to deploy to Railway.

**Expected deployment time: 3-5 minutes**

---

**🙏 ॐ सर्वे भवन्तु सुखिनः**
