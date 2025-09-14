import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/extract_fields/")
async def extract_fields(req: Request):
    body = await req.json()
    text = body.get("text", "")
    lang = body.get("lang", "en")
    form_id = body.get("form_id", "legal_form_1")

    extracted = {}

    # --- Strong Regex Patterns ---
    name_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+[A-Z][a-z]+)\b"

    phone_pattern = r"""
    \b
    (?:\+91[\-\s]?)?       # optional +91
    [6-9]\d{2}             # first 3 digits
    [\s\-]?\d{3}           # next 3 digits
    [\s\-]?\d{4}           # last 4 digits
    \b
    """

    pincode_pattern = r"\b[1-9][0-9]{5}\b"

    dob_pattern = r"\b(?:0[1-9]|[12][0-9]|3[01])[-/\s](?:0[1-9]|1[0-2])[-/\s](?:19|20)\d{2}\b"

    # Address → Extract a line starting with words like "address", "residing at", "living at"
    address_pattern = r"(?:address|residing at|living at)[:\-]?\s*([A-Za-z0-9,\-\s]+)"

    # --- Extract Name ---
    name_match = re.search(name_pattern, text)
    if name_match:
        extracted["applicant_name"] = name_match.group(1).strip()

    # --- Extract Phone ---
    phone_match = re.search(phone_pattern, text, re.VERBOSE)
    if phone_match:
        raw_phone = phone_match.group(0)
        digits_only = re.sub(r"\D", "", raw_phone)
        extracted["phone"] = "+91" + digits_only[-10:]

    # --- Extract Pincode ---
    pincode_match = re.search(pincode_pattern, text)
    if pincode_match:
        extracted["pincode"] = pincode_match.group(0)

    # --- Extract DOB ---
    dob_match = re.search(dob_pattern, text)
    if dob_match:
        extracted["dob"] = dob_match.group(0)

    # --- Extract Address ---
    address_match = re.search(address_pattern, text, re.IGNORECASE)
    if address_match:
        extracted["address"] = address_match.group(1).strip()

    # --- Cleanup Residual Text ---
    residual_text = text
    for value in extracted.values():
        if value and isinstance(value, str):
            residual_text = residual_text.replace(value, "", 1)
    residual_text = re.sub(r"\s+", " ", residual_text).strip()

    # --- Final JSON Response ---
    form_data = {
        "form_id": form_id,
        "applicant_name": extracted.get("applicant_name"),
        "phone": extracted.get("phone"),
        "pincode": extracted.get("pincode"),
        "dob": extracted.get("dob"),
        "address": extracted.get("address"),
        "subject": text,
        "residual_text": residual_text,
        "fields": extracted
    }

    return form_data


# Run with:
# uvicorn nlp_service:app --reload --port 8002
