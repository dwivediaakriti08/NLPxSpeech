import sounddevice as sd
import numpy as np
import tempfile
import requests
import sys
import soundfile as sf

# --- Config: URLs of services ---
SPEECH_SERVICE_URL = "http://127.0.0.1:8003/transcribe/"
NLP_SERVICE_URL = "http://127.0.0.1:8002/extract_fields/"

def record_audio():
    print(" Recording started. Press ENTER to stop...")
    fs = 16000  # sample rate
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        recording.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input()  # wait for ENTER
    print(" Recording stopped!")

    audio = np.concatenate(recording, axis=0)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, fs)
    print(f" Saved as {temp_file.name}")
    return temp_file.name

def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/wav")}
        response = requests.post(SPEECH_SERVICE_URL, files=files)
    response.raise_for_status()
    return response.json()

def parse_text(text, lang="en", form_id="legal_form_1"):
    payload = {"text": text, "lang": lang, "form_id": form_id}
    response = requests.post(NLP_SERVICE_URL, json=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Step 1: Record audio
    audio_file = record_audio()

    try:
        # Step 2: Send audio to speech service
        transcribe_result = transcribe_audio(audio_file)
        text = transcribe_result.get("text", "").strip()
        detected_lang = transcribe_result.get("detected_language", "en")

        print("\n Transcription Result:")
        print("language:", detected_lang)
        print(" Text:", text)

        # Step 3: Send text to NLP service
        nlp_result = parse_text(text, lang=detected_lang, form_id="legal_form_1")

        print("\n Extracted Fields:", nlp_result.get("fields", {}))
        print("\nResidual Text:", nlp_result.get("residual_text", ""))
        print("\nAuto-generated Form JSON:", nlp_result)

    except requests.HTTPError as e:
        print("Request failed:", e)
    except Exception as e:
        print("Error:", e)
