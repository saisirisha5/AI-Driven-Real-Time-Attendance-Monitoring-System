import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase once globally
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(
        r"C:\Users\prabh\OneDrive\Desktop\Projects\Term Paper Project\esp32-attendance-system-2025-firebase-adminsdk-fbsvc-7d9ed7b2b0.json"
    )
    firebase_admin.initialize_app(cred)

# Export Firestore client
db = firestore.client()
