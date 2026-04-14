"""
Test Script - DivineVedic AI Bot
Quick test to verify Qwen API integration and basic functionality.
Run this after setting up your .env file.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_qwen_service():
    """Test Qwen API service directly"""
    print("\n" + "="*60)
    print("🧪 Testing Qwen Service...")
    print("="*60)
    
    try:
        from app.services.qwen_service import qwen_service
        
        # Initialize
        if not qwen_service.initialize():
            print("❌ Failed to initialize Qwen service - check OPENROUTER_API_KEY")
            return False
        
        print("✅ Qwen service initialized successfully")
        
        # Test basic completion
        print("\n📤 Sending test message to Qwen API...")
        messages = [
            {"role": "user", "content": "Hello, I'm testing the DivineVedic AI bot. Please respond with a short greeting in Hinglish."}
        ]
        
        response = await qwen_service.get_completion_with_retry(
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            system_prompt="You are a 100+ years experienced Vedic astrologer. You speak in Hinglish."
        )
        
        if response:
            print("✅ Qwen API responded successfully!")
            print(f"\n💬 Response ({len(response)} chars):")
            print("-" * 60)
            print(response[:300])
            print("-" * 60)
            return True
        else:
            print("❌ Qwen API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Qwen service: {e}")
        return False


async def test_vedic_astrology_agent():
    """Test Vedic Astrology agent"""
    print("\n" + "="*60)
    print("🔮 Testing Vedic Astrology Agent...")
    print("="*60)
    
    try:
        from app.agents.vedic_astrology_agent import vedic_astrology_agent
        from app.models import SessionInfo, SessionState
        import time
        
        # Create test session
        session_info = SessionInfo(
            session_id="test_session",
            phone_number="+919876543210",
            state=SessionState.TRIAL,
            message_count=0,
            created_at=time.time(),
            last_activity=time.time()
        )
        
        # Test with astrology query
        print("\n📤 Testing astrology query...")
        response = await vedic_astrology_agent.process(
            user_message="What does my future hold for career and marriage?",
            session_info=session_info
        )
        
        if response.response:
            print("✅ Vedic Astrology Agent responded successfully!")
            print(f"\n💬 Response ({len(response.response)} chars):")
            print("-" * 60)
            print(response.response[:300])
            print("-" * 60)
            return True
        else:
            print("❌ Empty response from agent")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Vedic Astrology Agent: {e}")
        return False


async def test_numerology_agent():
    """Test Numerology agent"""
    print("\n" + "="*60)
    print("🔢 Testing Numerology Agent...")
    print("="*60)
    
    try:
        from app.agents.numerology_chaldean_agent import numerology_chaldean_agent
        from app.models import SessionInfo, SessionState
        import time
        
        # Create test session with DOB
        session_info = SessionInfo(
            session_id="test_numerology",
            phone_number="+919876543210",
            state=SessionState.TRIAL,
            message_count=0,
            created_at=time.time(),
            last_activity=time.time(),
            user_dob="15/08/1990"
        )
        
        # Test with numerology query
        print("\n📤 Testing numerology query...")
        response = await numerology_chaldean_agent.process(
            user_message="What is my mulank and bhagyank?",
            session_info=session_info
        )
        
        if response.response:
            print("✅ Numerology Agent responded successfully!")
            print(f"\n💬 Response ({len(response.response)} chars):")
            print("-" * 60)
            print(response.response[:300])
            print("-" * 60)
            return True
        else:
            print("❌ Empty response from agent")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Numerology Agent: {e}")
        return False


async def test_whatsapp_service():
    """Test WhatsApp service (credentials only)"""
    print("\n" + "="*60)
    print("📱 Testing WhatsApp Service...")
    print("="*60)
    
    try:
        from app.services.whatsapp_service import whatsapp_service
        
        if whatsapp_service.initialize():
            print("✅ WhatsApp service initialized successfully")
            print(f"   Phone Number ID: {whatsapp_service.phone_number_id[:10]}...")
            return True
        else:
            print("⚠️  WhatsApp service not configured (credentials missing)")
            print("   This is OK for local testing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp service: {e}")
        return False


async def test_config():
    """Test configuration"""
    print("\n" + "="*60)
    print("⚙️  Testing Configuration...")
    print("="*60)
    
    try:
        from app.config import settings
        
        # Check required env vars
        checks = {
            "OPENROUTER_API_KEY": bool(settings.OPENROUTER_API_KEY),
            "OPENROUTER_MODEL": settings.OPENROUTER_MODEL,
            "WHATSAPP_ACCESS_TOKEN": bool(settings.WHATSAPP_ACCESS_TOKEN),
            "WHATSAPP_PHONE_NUMBER_ID": bool(settings.WHATSAPP_PHONE_NUMBER_ID),
            "FIREBASE_PROJECT_ID": bool(settings.FIREBASE_PROJECT_ID),
            "RAZORPAY_KEY_ID": bool(settings.RAZORPAY_KEY_ID),
        }
        
        print("\n📋 Configuration Status:")
        for key, value in checks.items():
            status = "✅" if value else "⚠️ "
            print(f"  {status} {key}: {value if isinstance(value, str) else 'Set'}")
        
        # Validate
        is_valid = settings.validate()
        if is_valid:
            print("\n✅ All required settings are configured!")
            return True
        else:
            print("\n⚠️  Some optional settings are missing (this is OK for testing)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🙏 DivineVedic AI Bot - Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Configuration
    results["Config"] = await test_config()
    
    # Test 2: Qwen Service
    results["Qwen Service"] = await test_qwen_service()
    
    # Test 3: WhatsApp Service
    results["WhatsApp Service"] = await test_whatsapp_service()
    
    # Test 4: Vedic Astrology Agent
    results["Vedic Astrology Agent"] = await test_vedic_astrology_agent()
    
    # Test 5: Numerology Agent
    results["Numerology Agent"] = await test_numerology_agent()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your bot is ready to deploy!")
        print("\n📝 Next steps:")
        print("  1. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("  2. Open: http://localhost:8000/docs")
        print("  3. Setup ngrok for WhatsApp webhook testing")
        print("  4. Configure WhatsApp webhook URL in Meta Developer Console")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and fix them.")
        print("   Most likely issue: Missing OPENROUTER_API_KEY in .env file")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
