from fastapi import FastAPI
from google.cloud import pubsub_v1
from google.cloud import storage
import aiofiles
import os
from datetime import datetime
import requests
from pydantic import BaseModel

app = FastAPI()

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./videos")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
SUBSCRIPTION_NAME = os.getenv("PUBSUB_SUBSCRIPTION")

# Ensure storage directory exists
os.makedirs(STORAGE_PATH, exist_ok=True)

class DoorbellEvent(BaseModel):
    event_id: str
    device_id: str
    video_url: str

async def download_video(video_url: str, filename: str):
    response = requests.get(video_url, stream=True)
    filepath = os.path.join(STORAGE_PATH, filename)
    
    async with aiofiles.open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            await f.write(chunk)
    
    return filepath

@app.post("/doorbell-event")
async def handle_doorbell_event(event: DoorbellEvent):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"doorbell_{event.device_id}_{timestamp}.mp4"
    
    try:
        filepath = await download_video(event.video_url, filename)
        return {"status": "success", "saved_to": filepath}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 