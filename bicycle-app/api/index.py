from fastapi import BackgroundTasks, FastAPI
import subprocess

import os

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

def get_realsense_data():
    subprocess.call(f"python3 record_30s.py --num-frames=300".split(" "))
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