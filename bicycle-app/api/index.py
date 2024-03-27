from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
import cv2
import asyncio
import subprocess

import os

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)


manager = ConnectionManager()

def get_realsense_data():
    subprocess.call(f"python3 accel_rrecord_30s.py --num-frames=300".split(" "))
    os.remove("recording.lock")
    print("recording finished")
    return 

@app.get("/api/py/healthcheck")
def healthchecker():
    return {"status": "success", "message": "Integrated FastAPI Framework with Next.js successfully!"}

@app.get("/api/py/recording")
def recording():
    if os.path.exists('recording.lock'):
        return {"recording": True}
    else:
        return {"recording": False}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# websocket logic mostly from nano-owl example repo
async def detection_loop(app: FastAPI):
    loop = asyncio.get_event_loop()
    camera = cv2.VideoCapture(4)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 270)

    def _read_and_encode_image():
        re, image = camera.read()

        if not re:
            return re, None
        image_jpeg = bytes(
                cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 50])[1]
            )

        return re, image_jpeg

    while True:
        re, image = await loop.run_in_executor(None, _read_and_encode_image)
        
        if not re:
            break
        await manager.broadcast(image)

    camera.release()
    
@asynccontextmanager
async def run_detection(app: FastAPI):
    try:
        task = asyncio.create_task(detection_loop(app))
        yield
        task.cancel()
    except asyncio.CancelledError:
        task.cancel()
        raise
    finally:
        await task

@app.post("/api/py/record")
def record(background_tasks: BackgroundTasks):
    if os.path.exists('recording.lock'):
        return {"message": "Already recording"}
    else:
        with open('recording.lock', 'w') as f:
            pass
        print("recording started")
        background_tasks.add_task(get_realsense_data)
        return {"message": "Recording started"}