from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os, uuid, whisper, shutil
from typing import Optional
from webvtt import WebVTT
import difflib
import glob
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper_models = {
    "medium": whisper.load_model("small"),  # 고품질 (느림)
    "low": None,  # 저품질은 yt-dlp 자막 사용
    "default": whisper.load_model("tiny")   # 중간 품질
}

class URLRequest(BaseModel):
    url: str
    lang: str
    quality: str = "low"

def remove_duplicates(lines, similarity_threshold=0.95):
    unique_lines = []
    for i, line in enumerate(lines):
        line = line.strip().replace("\n", " ")
        if not line:
            continue
        is_duplicate = False
        for prev_line in unique_lines:
            similarity = difflib.SequenceMatcher(None, line, prev_line).ratio()
            if similarity > similarity_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_lines.append(line)
    return unique_lines

@app.post("/transcribe_youtube")
def transcribe_youtube(data: URLRequest):
    url = data.url
    lang = data.lang or "ko"
    quality = data.quality or "low"
    uid = str(uuid.uuid4())[:8]
    base = f"yt_{uid}"

    try:
        if quality == "low":
            # 저품질: 자동자막 긁기
            subprocess.run([
                "yt-dlp", "--write-auto-sub", "--skip-download",
                "--sub-lang", lang, "--sub-format", "vtt",
                "-o", f"{base}.%(ext)s", url
            ], check=True)

            vtt_files = glob.glob(f"{base}.*.vtt")
            if not vtt_files:
                return {"error": "❌ 자막 추출 실패: VTT 파일 없음"}

            vtt_path = vtt_files[0]
            vtt = WebVTT().read(vtt_path)

            raw_lines = []
            for caption in vtt:
                raw_lines.extend([l.strip() for l in caption.text.split("\n") if l.strip()])

            lines = remove_duplicates(raw_lines)
            transcription = "\n".join(lines)

        else:
            # 중/고품질: 오디오 다운로드 후 Whisper 모델 추출
            subprocess.run([
                "yt-dlp", "-x", "--audio-format", "mp3", "-o", f"{base}.%(ext)s", url
            ], check=True)

            mp3_files = glob.glob(f"{base}.mp3")
            if not mp3_files:
                return {"error": "❌ 오디오 추출 실패"}

            audio_path = mp3_files[0]

            model_key = "medium" if quality == "high" else "default"
            model = whisper_models[model_key]

            result = model.transcribe(audio_path, language=lang, fp16=False)
            segments = result.get("segments", [])

            lines = []
            seen = set()
            for seg in segments:
                line = seg["text"].strip()
                if line and line not in seen:
                    lines.append(line)
                    seen.add(line)

            lines = remove_duplicates(lines)
            transcription = "\n".join(lines)

        return {"transcription": transcription}

    except Exception as e:
        return {"error": f"❌ 처리 중 오류: {str(e)}"}

    finally:
        # 끝나고 파일 삭제
        for f in glob.glob(f"{base}.*"):
            os.remove(f)
@app.post("/transcribe_file")
async def transcribe_file(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())[:8]
    filename = f"upload_{uid}.mp3"
    try:
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        model = whisper_models["default"]
        result = model.transcribe(filename, language="ko", fp16=False)
        segments = result.get("segments", [])

        lines = []
        seen = set()
        for seg in segments:
            line = seg["text"].strip()
            if line and line not in seen:
                lines.append(line)
                seen.add(line)

        lines = remove_duplicates(lines)
        transcription = "\n".join(lines)

        return {"transcription": transcription}

    except Exception as e:
        return {"error": f"파일 처리 오류: {str(e)}"}

    finally:
        if os.path.exists(filename):
            os.remove(filename)