import face_recognition
import base64
import cv2
import numpy as np
from datetime import datetime
import PIL.Image
from .firebase_config import db 

def add_student_to_firebase(name, regd_no, department, image_file):
    """
    Takes uploaded image from Django form,
    generates encoding, and uploads to Firebase.
    """
    try:
        # Read image from uploaded file
        file_bytes = image_file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return False, "Could not read uploaded image."

        # Ensure RGB image
        if img.dtype != 'uint8':
            img = (img * 255).astype('uint8')
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Convert via Pillow for stable 8-bit RGB
        pil_image = PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.convert("RGB")
        rgb_img = np.ascontiguousarray(np.array(pil_image), dtype=np.uint8)

        # Generate face encoding
        encodings = face_recognition.face_encodings(rgb_img)
        if len(encodings) == 0:
            return False, "No face detected. Please upload a clearer image."

        face_encoding = encodings[0].tolist()

        # Convert image to base64
        img_base64 = base64.b64encode(file_bytes).decode('utf-8')

        # Prepare Firestore data
        student_data = {
            'name': name,
            'regd_no': regd_no,
            'department': department,
            'image_base64': img_base64,
            'face_encoding': face_encoding,
            'created_at': datetime.now().isoformat()
        }

        # Upload to Firestore
        doc_ref = db.collection('students').document(regd_no)
        if doc_ref.get().exists:
            return False, f"Student {regd_no} already exists in Firebase."

        doc_ref.set(student_data)
        return True, f"Successfully added {name} ({regd_no}) to Firebase."

    except Exception as e:
        return False, f"Error: {e}"
