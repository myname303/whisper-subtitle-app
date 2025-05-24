from fastapi import FastAPI, File, UploadFile
import whisper
import shutil

app = FastAPI()
model = whisper.load_model("base")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with open("temp.mp3", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = model.transcribe("temp.mp3")
    return {"transcription": result["text"]}