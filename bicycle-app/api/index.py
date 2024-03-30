from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import av
from av.packet import Packet
import cv2
import asyncio
import subprocess

import threading
from nanoowl.owl_predictor import OwlPredictor
from nanoowl.owl_drawing import (
    draw_owl_output
)

from PIL import Image

import os
import logging
from datetime import datetime

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

prompt = ["a person", "a car", "a truck", "a van"]
thresholds = [0.2, 0.2, 0.2, 0.2]
predictor_model = "google/owlvit-base-patch32" 
image_encoder_engine = "/opt/nanoowl/data/owl_image_encoder_patch32.engine" # if running in the container!

predictor = OwlPredictor(
        predictor_model,
        image_encoder_engine=image_encoder_engine
)

text_encodings = predictor.encode_text(prompt)

camera = cv2.VideoCapture(4)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 848)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.is_recording = False
        self.output = None
        self.stream = None

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

def cv2_to_pil(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image)

def get_realsense_data():
    subprocess.call(f"python3 accel_rrecord_30s.py --num-frames=300".split(" "))
    os.remove("recording.lock")
    print("recording finished")
    return 

# websocket logic mostly from nano-owl example repo
async def detection_loop(app: FastAPI):
    loop = asyncio.get_event_loop()
    logger.info("Detection Loop Started")
    def _read_and_encode_image():
        re, image = camera.read()
        if not re:
            return re, None
        
        image_pil = cv2_to_pil(image)
        output = predictor.predict(
                    image=image_pil, 
                    text=prompt, 
                    text_encodings=text_encodings,
                    threshold=thresholds,
                    pad_square=False)
        owl_image = draw_owl_output(image, output, text=prompt, draw_text=True)
        # image_copy = image.copy()
        if manager.is_recording: # Add a red bar to indicate recording
            bar_height = 50  # Adjust the thickness of the bar
            color = (0, 0, 255)  # Red color in BGR format
            image_height, image_width = image.shape[:2]
            # The top-left corner of the rectangle (x1, y1)
            x1, y1 = 0, image_height - bar_height
            # The bottom-right corner of the rectangle (x2, y2)
            x2, y2 = image_width, image_height
            cv2.rectangle(owl_image, (x1, y1), (x2, y2), color, thickness=cv2.FILLED)

        image_jpeg = bytes(
                cv2.imencode(".jpg", owl_image, [cv2.IMWRITE_JPEG_QUALITY, 50])[1]
            )

        return re, image_jpeg, Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    while True:
        re, image, raw_image = await loop.run_in_executor(None, _read_and_encode_image)

        if not re:
            logger.info("Camera not connected!")
            break
        if manager.is_recording:
            frame = av.VideoFrame.from_image(raw_image)
            for packet in manager.stream.encode(frame):
                manager.output.mux(packet)
        await manager.broadcast(image)

    camera.release()
    
@asynccontextmanager
async def run_detection(app: FastAPI):
    global bouncingTimer
    try:
        task = asyncio.create_task(detection_loop(app))
        yield
        task.cancel()

    except asyncio.CancelledError:
        logger.info("Run Detection Cancelled")
        task.cancel()
        raise
    finally:
        await task

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json", lifespan=run_detection)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://ubuntu:3000",
    "http://ubuntu",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/py/record-video")
def record_video(background_tasks: BackgroundTasks):
    if manager.is_recording:
        return {"message": "Already recording"}
    else:
        manager.is_recording = True
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        manager.output = av.open(f"{dt_string}.mp4", mode='w')
        manager.stream = manager.output.add_stream('libx264', rate=30)
        manager.stream.width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        manager.stream.height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        manager.stream.pix_fmt = 'yuv420p'

        return {"message": "Recording started"}

@app.post("/api/py/stop-video")
def stop_recording_video():
    if manager.is_recording:
        manager.is_recording = False
        for packet in manager.stream.encode():
            manager.output.mux(packet)
        manager.output.close()
        return {"message": "Recording stopped"}
    else:
        return {"message": "Not recording"}

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