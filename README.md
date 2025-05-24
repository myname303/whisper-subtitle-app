# 🎙 Whisper Subtitle App

Generate subtitles from YouTube videos or audio files using OpenAI's Whisper model.

This project allows users to upload `.mp3` files **or enter a YouTube video URL**, and receive **automatically generated subtitles** as text output — both on-screen and downloadable as a `.txt` or `.srt` file.

---

## 🚀 Features

- Upload `.mp3` audio or paste a YouTube URL
- Automatic transcription using OpenAI Whisper (local or API-based)
- Web interface built with FastAPI + JavaScript
- Subtitles appear on screen instantly
- Download subtitles as `.txt` or `.srt` file
- Docker-ready for consistent deployment
- Planned EC2 + Terraform deployment workflow

---

## 🛠 Tech Stack

| Area | Tools |
|------|-------|
| Backend | FastAPI, Whisper, Python 3.11 |
| Frontend | HTML, JavaScript, Tailwind CSS (CDN) |
| Audio extraction | yt-dlp |
| Subtitles | Whisper `.transcribe()` output |
| Containerization | Docker |
| Deployment (planned) | AWS EC2 → Terraform IaC |

---

## 🧪 Getting Started (Local)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/whisper-subtitle-app.git
cd whisper-subtitle-app
