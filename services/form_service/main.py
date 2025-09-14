from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os, json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBMIT_DIR = os.path.join(BASE_DIR, "submissions")
os.makedirs(SUBMIT_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Form Service is running"}

@app.get("/forms")
def list_forms():
    forms = [f.replace(".json", "") for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    return {"cases": forms}

@app.get("/forms/{form_id}")
def get_form(form_id: str):
    form_file = os.path.join(DATA_DIR, f"{form_id}.json")
    if not os.path.exists(form_file):
        raise HTTPException(404, f"Unknown form: {form_id}")
    with open(form_file, "r", encoding="utf-8") as f:
        return {"case": form_id, "form": json.load(f)}

@app.post("/submit/{form_id}")
async def submit_form(form_id: str, request: Request):
    """Save submitted form data into a file"""
    try:
        data = await request.json()
        file_path = os.path.join(SUBMIT_DIR, f"{form_id}_submissions.json")

        # Append to existing file
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                submissions = json.load(f)
        else:
            submissions = []

        submissions.append(data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(submissions, f, indent=2)

        return {"status": "success", "saved_entries": len(submissions)}
    except Exception as e:
        raise HTTPException(500, f"Error saving submission: {str(e)}")

@app.get("/submissions/{form_id}")
def get_submissions(form_id: str):
    file_path = os.path.join(BASE_DIR, "data", f"{form_id}_submissions.json")
    if not os.path.exists(file_path):
        return {"submissions": []}
    with open(file_path, "r", encoding="utf-8") as f:
        submissions = json.load(f)
    return {"submissions": submissions}
