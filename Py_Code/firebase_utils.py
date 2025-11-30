import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(env_path)

firebase_cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")

if not firebase_cred_path or not os.path.exists(firebase_cred_path):
    raise FileNotFoundError(f"Firebase credentials not found: {firebase_cred_path}")

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def mark_attendance(name, regd_no):
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

    existing_list = list(existing)
    if existing_list:
        # Already exists → don't crash
        return False

    # Safe add (Firestore auto-ID, no create conflict)
    attendance_ref.add({
        "name": name,
        "regd_no": regd_no,
        "date": date,
        "time": time,
        "timestamp": now,
        "status": "Present",
    })

    return True

