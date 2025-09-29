# test_firebase_direct_fixed.py
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import ALL models first to resolve relationships
import app.models.user
import app.models.user_profile
import app.models.skin_analysis
import app.models.otp
import app.models.daily_skin_log
import app.models.reminder

from app.services.push_notification import push_service
from app.db.session import SessionLocal
from app.models.user import User


async def test_firebase_connection():
    """Test Firebase connection with dummy token"""
    print("🔍 Testing Firebase Connection...")

    # Test with a dummy token (this will fail but show Firebase connection)
    result = await push_service.send_push_notification(
        device_token="dummy_token_for_testing",
        title="Test Firebase",
        body="Testing Firebase connection"
    )
    print(f"Firebase test result: {result}")


def check_device_token():
    """Check if user has device token in database"""
    print("\n Checking Device Token in Database...")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"✅ User found: {user.email}")
            print(f"📱 Device Token: {user.device_token}")
            print(f"📏 Token Length: {len(user.device_token) if user.device_token else 0}")

            if user.device_token:
                print("✅ Device token is registered!")
            else:
                print("❌ No device token found - user needs to register device")
        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()


async def test_with_real_token():
    """Test with real device token if available"""
    print("\n🔍 Testing with Real Device Token...")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if user and user.device_token:
            print(f"📱 Using device token: {user.device_token[:20]}...")

            result = await push_service.send_push_notification(
                device_token=user.device_token,
                title="🧪 Test Notification",
                body="This is a test from backend"
            )
            print(f" Real token test result: {result}")
        else:
            print("❌ No device token available for testing")
    except Exception as e:
        print(f"❌ Error testing with real token: {e}")
    finally:
        db.close()


async def main():
    print("🚀 Starting Firebase Investigation...")
    print("=" * 50)

    # 1. Check device token in database
    check_device_token()

    # 2. Test Firebase connection
    await test_firebase_connection()

    # 3. Test with real token if available
    await test_with_real_token()

    print("\n" + "=" * 50)
    print("✅ Investigation complete!")


if __name__ == "__main__":
    asyncio.run(main())