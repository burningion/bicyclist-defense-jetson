from fastapi import FastAPI
import subprocess

import os

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/healthcheck")
def healthchecker():
    return {"status": "success", "message": "Integrated FastAPI Framework with Next.js successfully!"}

@app.post("/api/py/record")
def record():
    print("recoding...")
    print(f"current directory: {os.getcwd()}")
    subprocess.call(f"python3 rrecord_30s.py --num-frames=300".split(" "))
    return True