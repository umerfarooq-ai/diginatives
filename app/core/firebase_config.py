import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def create_firebase_credentials_json() -> Optional[dict]:
    """
    Create Firebase credentials JSON from environment variables
    Returns the same JSON structure as the original service-account-key.json
    """
    try:
        # Check if all required environment variables are set
        required_vars = [
            'FIREBASE_TYPE', 'FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY_ID',
            'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL', 'FIREBASE_CLIENT_ID',
            'FIREBASE_AUTH_URI', 'FIREBASE_TOKEN_URI', 'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
            'FIREBASE_CLIENT_X509_CERT_URL', 'FIREBASE_UNIVERSE_DOMAIN'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return None

        # Build Firebase credentials JSON (same structure as original file)
        firebase_credentials = {
            "type": os.getenv('FIREBASE_TYPE'),
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
        }

        logger.info("Firebase credentials JSON created from environment variables")
        return firebase_credentials

    except Exception as e:
        logger.error(f"Error creating Firebase credentials from environment: {str(e)}")
        return None

def get_firebase_credentials_file_path() -> str:
    """
    Get the path to the Firebase credentials file
    This maintains the same file path structure as before
    """
    return "firebase_credentials/service-account-key.json"

def ensure_firebase_credentials_file() -> bool:
    """
    Ensure Firebase credentials file exists by creating it from environment variables
    Returns True if successful, False otherwise
    """
    try:
        # Create firebase_credentials directory if it doesn't exist
        os.makedirs("firebase_credentials", exist_ok=True)

        # Get credentials from environment variables
        credentials = create_firebase_credentials_json()
        if not credentials:
            return False

        # Write to the same file path as before
        file_path = get_firebase_credentials_file_path()
        with open(file_path, 'w') as f:
            json.dump(credentials, f, indent=2)

        logger.info(f"Firebase credentials file created at: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating Firebase credentials file: {str(e)}")
        return False