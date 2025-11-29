import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from dotenv import load_dotenv

# Load .env from project root (Term Paper Project/.env)
env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(env_path)

# Load Firebase credentials
firebase_cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")

if not firebase_cred_path or not os.path.exists(firebase_cred_path):
    raise FileNotFoundError(f"Firebase credentials not found: {firebase_cred_path}")

# Initialize Firebase
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def mark_attendance(name, regd_no):
    """Mark attendance only once per day per student."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    attendance_ref = db.collection("attendance_records")

    # Check if already marked
    existing = (
        attendance_ref
        .where(filter=FieldFilter("regd_no", "==", regd_no))
        .where(filter=FieldFilter("date", "==", date))
        .stream()
    )

    if list(existing):
        return False  # already marked

    # Mark attendance
    attendance_ref.add({
        "name": name,
        "regd_no": regd_no,
        "date": date,
        "time": time,
        "timestamp": now,
        "status": "Present",
    })

    return True
