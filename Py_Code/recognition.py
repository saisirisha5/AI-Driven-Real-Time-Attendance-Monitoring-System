import numpy as np
import face_recognition
from firebase_utils import db
import cv2

print("🔄 Loading student encodings from Firebase...")

students_ref = db.collection("students").stream()
known_encodings = []
known_names = []
known_regd = []

for s in students_ref:
    data = s.to_dict()
    if "face_encoding" in data:
        try:
            encoding = np.array(data["face_encoding"])
            known_encodings.append(encoding)
            known_names.append(data["name"])
            known_regd.append(data["regd_no"])
        except:
            continue

print(f"✅ Loaded {len(known_encodings)} student encodings.")


def recognize_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None, None, 0.0

    # Resize & convert to RGB
    img_small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(img_rgb)
    face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

    if len(face_encodings) == 0:
        return None, None, 0.0

    face = face_encodings[0]

    matches = face_recognition.compare_faces(known_encodings, face)
    distances = face_recognition.face_distance(known_encodings, face)
    best_match = int(np.argmin(distances))

    if matches[best_match]:
        name = known_names[best_match]
        regd_no = known_regd[best_match]
        confidence = 1 - distances[best_match]
        return name, regd_no, round(float(confidence), 3)

    return None, None, 0.0
