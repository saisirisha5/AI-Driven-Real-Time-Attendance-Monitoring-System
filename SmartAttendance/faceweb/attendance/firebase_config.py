import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load .env (from parent directory)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))

firebase_cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")

if not firebase_cred_path or not os.path.exists(firebase_cred_path):
    raise FileNotFoundError(f"❌ Firebase credential file not found: {firebase_cred_path}")

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
