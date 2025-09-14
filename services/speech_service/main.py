# speech_service.py
from fastapi import FastAPI, File, UploadFile
import tempfile, os
from faster_whisper import WhisperModel

app = FastAPI()

# --- Load Whisper Model (faster-whisper) ---
# "small" is fast and accurate; use "medium" or "large" if needed
model = WhisperModel("small", compute_type="int8")

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Transcribe audio (auto language detection)
        segments, info = model.transcribe(tmp_path, beam_size=5)
        # Combine all segments into a single text
        text = " ".join([segment.text for segment in segments]).strip()

        return {
            "detected_language": info.language if hasattr(info, 'language') else "unknown",
            "text": text
        }

    finally:
        os.remove(tmp_path)

# Run with:
# uvicorn speech_service:app --reload --port 8003
