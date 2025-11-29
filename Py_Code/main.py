from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from recognition import recognize_face
from firebase_utils import mark_attendance
import uuid
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "FastAPI recognition server running"}


@app.post("/recognize")
async def recognize(image: UploadFile = File(...)):
    # Save temporary image
    temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_filename, "wb") as f:
        f.write(await image.read())

    # Recognize
    name, regd_no, confidence = recognize_face(temp_filename)

    # Delete temp image
    os.remove(temp_filename)

    if not name:
        return JSONResponse({"recognized": False, "message": "No face found"})

    marked = mark_attendance(name, regd_no)

    return {
        "recognized": True,
        "name": name,
        "regd_no": regd_no,
        "confidence": confidence,
        "attendance_marked": marked
    }
