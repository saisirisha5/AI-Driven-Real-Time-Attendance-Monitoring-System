import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="face_recognition_models")

import firebase_admin
from firebase_admin import credentials, firestore
import face_recognition
import base64
import cv2
import numpy as np
from datetime import datetime
import PIL.Image

# -------------------------------------------------------------------
# 🔹 Firebase initialization
# -------------------------------------------------------------------
cred = credentials.Certificate(
    r"C:\Users\prabh\OneDrive\Desktop\Projects\Term Paper Project\esp32-attendance-system-2025-firebase-adminsdk-fbsvc-7d9ed7b2b0.json"
)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------------------------------------------------------
# 🔹 Student details
# -------------------------------------------------------------------
name = "Sai Sirisha Devi"
regd_no = "2200030081"
department = "CSE-H"
image_path = r"C:\Users\prabh\OneDrive\Desktop\Projects\Term Paper Project\Py_Code\test_face.png"  # update path

# -------------------------------------------------------------------
# 🔹 Read image safely
# -------------------------------------------------------------------
img = cv2.imread(image_path)
if img is None:
    print("❌ Image not found or unreadable. Check path:", image_path)
    exit()

print(f"📷 Image loaded successfully: {image_path} | Shape: {img.shape}, Dtype: {img.dtype}")

# -------------------------------------------------------------------
# 🔹 Ensure 8-bit RGB format (handles grayscale, RGBA, etc.)
# -------------------------------------------------------------------
if img.dtype != 'uint8':
    print("⚠️ Image not 8-bit, converting...")
    img = (img * 255).astype('uint8')

if len(img.shape) == 2:
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
elif img.shape[2] == 4:
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

# Convert via Pillow to ensure exact 8-bit RGB layout
pil_image = PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
pil_image = pil_image.convert("RGB")  # guarantees proper RGB
rgb_img = np.array(pil_image).astype('uint8')

# -------------------------------------------------------------------
# 🔹 Make array contiguous in memory (critical fix for dlib on Windows)
# -------------------------------------------------------------------
rgb_img = np.ascontiguousarray(rgb_img, dtype=np.uint8)
print("✅ Image prepared for encoding:", rgb_img.shape, rgb_img.dtype, "| Contiguous:", rgb_img.flags['C_CONTIGUOUS'])

# -------------------------------------------------------------------
# 🔹 Generate face encoding
# -------------------------------------------------------------------
print("🔍 Detecting face and generating encoding...")
try:
    encodings = face_recognition.face_encodings(rgb_img)
except RuntimeError as e:
    print("❌ Dlib error while encoding:", e)
    exit()

if len(encodings) == 0:
    print("❌ No face detected in image. Try another image with clearer face visibility.")
    exit()

face_encoding = encodings[0]
print("✅ Face encoding generated successfully.")

# -------------------------------------------------------------------
# 🔹 Convert image to base64 for Firestore storage
# -------------------------------------------------------------------
with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

# -------------------------------------------------------------------
# 🔹 Prepare Firestore document
# -------------------------------------------------------------------
student_data = {
    'name': name,
    'regd_no': regd_no,
    'department': department,
    'image_base64': img_base64,
    'face_encoding': face_encoding.tolist(),
    'created_at': datetime.now().isoformat()
}

# -------------------------------------------------------------------
# 🔹 Upload to Firestore
# -------------------------------------------------------------------
try:
    doc_ref = db.collection('students').document(regd_no)
    if doc_ref.get().exists:
        print(f"⚠️ Student {regd_no} already exists in Firebase. Skipping upload.")
    else:
        doc_ref.set(student_data)
        print(f"✅ Successfully added {name} ({regd_no}) to Firebase. Document path: {doc_ref.path}")
except Exception as e:
    print("❌ Failed to upload student data:", e)
