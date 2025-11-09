import os
import cv2
import urllib.request
import numpy as np
from datetime import datetime
import face_recognition
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from dotenv import load_dotenv

# -------------------------------------------------------------------
# 🔹 Load environment variables
# -------------------------------------------------------------------
# Load .env from the project root (one level up from Py_Code)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

firebase_cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
if not firebase_cred_path or not os.path.exists(firebase_cred_path):
    raise FileNotFoundError(f"Firebase credential file not found: {firebase_cred_path}")

# -------------------------------------------------------------------
# 🔹 Firebase Initialization
# -------------------------------------------------------------------
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------------------------------------------------------
# 🔹 Mode Selection
# -------------------------------------------------------------------
# Choose between: "static" or "esp32"
MODE = os.getenv("RUN_MODE", "static")  # default to static if not set

# -------------------------------------------------------------------
# 🔹 Fetch Known Encodings from Firebase
# -------------------------------------------------------------------
print("Fetching student data from Firebase...")

students = db.collection('students').stream()
known_encodings, known_names, known_regd = [], [], []

for doc in students:
    data = doc.to_dict()
    if 'face_encoding' in data:
        try:
            encoding = np.array(data['face_encoding'])
            known_encodings.append(encoding)
            known_names.append(data['name'])
            known_regd.append(data['regd_no'])
        except Exception as e:
            print(f"Skipping {data.get('name', 'Unknown')} - encoding issue: {e}")

print(f"Loaded {len(known_names)} encodings from Firebase")

if len(known_encodings) == 0:
    print("No encodings found! Please add students first.")
    exit()

# -------------------------------------------------------------------
# 🔹 Attendance Marking Function
# -------------------------------------------------------------------
def markAttendance(name, regd_no):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    attendance_ref = db.collection("attendance_records")

    query = (
        attendance_ref
        .where(filter=FieldFilter("regd_no", "==", regd_no))
        .where(filter=FieldFilter("date", "==", date))
        .stream()
    )

    existing = list(query)
    if existing:
        print(f"Attendance already marked for {name} ({regd_no}) today.")
        return

    attendance_ref.add({
        "name": name,
        "regd_no": regd_no,
        "date": date,
        "time": time,
        "timestamp": now
    })

    print(f"Attendance uploaded for {name} ({regd_no}) at {time}")

# -------------------------------------------------------------------
# 🔹 Image Source Setup
# -------------------------------------------------------------------
if MODE == "esp32":
    url = os.getenv("ESP32_URL", "http://192.168.1.43/cam-hi.jpg")
    print("📷 Running in ESP32-CAM Mode (Press 'q' to quit)")
else:
    test_img_path = os.getenv(
        "TEST_IMAGE_PATH",
        r"C:\Users\prabh\OneDrive\Desktop\Projects\Term Paper Project\Py_Code\test_face.jpg"
    )
    print(f"Running in Static Image Mode: {test_img_path}")

# -------------------------------------------------------------------
# 🔹 Recognition Logic
# -------------------------------------------------------------------
if MODE == "static":
    img = cv2.imread(test_img_path)
    if img is None:
        print("Could not read test image. Check path.")
        exit()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    if len(facesCurFrame) == 0:
        print("No faces detected.")
    else:
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(known_encodings, encodeFace)
            faceDis = face_recognition.face_distance(known_encodings, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = known_names[matchIndex]
                regd_no = known_regd[matchIndex]
                markAttendance(name, regd_no)
                print(f"Recognized {name} ({regd_no})")
            else:
                print("Face not recognized.")

    print("Static Image Test Completed.")

else:
    # ESP32 Live Stream
    while True:
        try:
            img_resp = urllib.request.urlopen(url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgnp, -1)

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(known_encodings, encodeFace)
                faceDis = face_recognition.face_distance(known_encodings, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = known_names[matchIndex]
                    regd_no = known_regd[matchIndex]
                    markAttendance(name, regd_no)

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('ESP32 Attendance', img)
            if cv2.waitKey(5) == ord('q'):
                break

        except Exception as e:
            print(f"Error: {e}")
            continue

    cv2.destroyAllWindows()
    print("ESP32 Mode Ended.")
