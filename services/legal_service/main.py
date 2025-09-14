from fastapi import FastAPI, HTTPException
import os, json

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)
DATA = os.path.join(BASE_DIR, "data", "articles.json")

@app.get("/")
def root():
    return {"message": "Legal Service is running "}

@app.get("/articles/{field_id}")
def get_article(field_id: str):
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            articles = json.load(f)

        if field_id not in articles:
            raise HTTPException(404, detail=f"Field '{field_id}' not found")

        return articles[field_id]

    except Exception as e:
        raise HTTPException(500, detail=f"Server error: {str(e)}")
