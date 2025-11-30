import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from recognition import recognize_face
from firebase_utils import mark_attendance

app = FastAPI()

LATEST_FRAME_PATH = "latest.jpg"


@app.post("/recognize")
async def recognize(request: Request):
    # Read raw bytes directly from ESP32
    raw_bytes = await request.body()

    # Save for preview
    with open(LATEST_FRAME_PATH, "wb") as f:
        f.write(raw_bytes)

    # Save temp for recognition
    temp_file = f"temp_{uuid.uuid4().hex}.jpg"
    with open(temp_file, "wb") as f:
        f.write(raw_bytes)

    name, regd_no, confidence = recognize_face(temp_file)
    os.remove(temp_file)

    if name is None:
        return {"recognized": False, "message": "Face not recognized"}

    marked = mark_attendance(name, regd_no)

    return {
        "recognized": True,
        "name": name,
        "regd_no": regd_no,
        "confidence": confidence,
        "attendance_marked": marked,
    }


# =======================
# LIVE STREAM / PREVIEW
# =======================

def mjpeg_streamer():
    import time
    while True:
        if os.path.exists(LATEST_FRAME_PATH):
            with open(LATEST_FRAME_PATH, "rb") as f:
                frame = f.read()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.1)


@app.get("/live")
def live_feed():
    return StreamingResponse(
        mjpeg_streamer(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
