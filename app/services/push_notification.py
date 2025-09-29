import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Path to your Firebase service account key
                service_account_path = "firebase_credentials/service-account-key.json"
                
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("✅ Firebase Admin SDK initialized successfully")
                else:
                    logger.error("❌ Firebase service account key not found!")
                    logger.error(f"Please place your service-account-key.json file in: {service_account_path}")
            else:
                logger.info("✅ Firebase Admin SDK already initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {str(e)}")

    async def send_push_notification(self, device_token: str, title: str, body: str) -> bool:
        """
        Send push notification to a specific device
        
        Args:
            device_token (str): The device token of the target device
            title (str): Notification title
            body (str): Notification body
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not device_token:
                logger.warning("⚠️ No device token provided")
                return False

            # Create the notification message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                token=device_token
            )

            # Send the message
            response = messaging.send(message)
            logger.info(f"✅ Push notification sent successfully: {response}")
            print(f"🔔 PUSH NOTIFICATION SENT: {title} - {body}")
            return True

        except messaging.UnregisteredError:
            logger.warning(f"⚠️ Device token is invalid or unregistered: {device_token}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send push notification: {str(e)}")
            return False

    async def send_to_multiple_devices(self, device_tokens: list, title: str, body: str) -> dict:
        """
        Send push notification to multiple devices
        
        Args:
            device_tokens (list): List of device tokens
            title (str): Notification title
            body (str): Notification body
            
        Returns:
            dict: Results with success/failure counts
        """
        try:
            if not device_tokens:
                logger.warning("⚠️ No device tokens provided")
                return {"success": 0, "failed": 0}

            # Create the notification message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                tokens=device_tokens
            )

            # Send the message
            response = messaging.send_multicast(message)
            
            logger.info(f"✅ Multicast notification sent: {response.success_count} successful, {response.failure_count} failed")
            print(f"🔔 MULTICAST NOTIFICATION: {response.success_count} sent, {response.failure_count} failed")
            
            return {
                "success": response.success_count,
                "failed": response.failure_count,
                "responses": response.responses
            }

        except Exception as e:
            logger.error(f"❌ Failed to send multicast notification: {str(e)}")
            return {"success": 0, "failed": len(device_tokens)}

# Create a global instance
push_service = PushNotificationService() 