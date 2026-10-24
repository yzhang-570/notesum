import json
import os

import anthropic
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

app = FastAPI()

# Read the model name from the environment, with a default
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-haiku-5-5")


class NoteRequest(BaseModel):
    note: str


class SummaryResult(BaseModel):
    summary: str
    action_items: list[str]


# Send the prompt to the Anthropic Messages API and return the reply text
def call_model(prompt):
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        timeout=60,
    )
    return response.content[0].text


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/summarize")
def summarize(request: NoteRequest, x_user_email: str = Header(default=None)):
    # Keep only the first 4000 characters of the note
    note = request.note[:4000]

    # Append the note to the request log, creating the folder if needed
    os.makedirs("logs", exist_ok=True)
    with open("logs/requests.log", "a", encoding="utf-8") as log_file:
        log_file.write(request.note + "\n")

    # Build the prompt, adding the user's email when it was provided
    prompt = ""
    if x_user_email:
        prompt = prompt + "The note is from user: " + x_user_email + "\n"
    prompt = prompt + "Summarize the note below. Reply with JSON only, in this shape: "
    prompt = prompt + '{"summary": str, "action_items": [str]}\n\n'
    prompt = prompt + "Note:\n" + note

    # Call the model; on any error return a canned reply
    try:
        reply_text = call_model(prompt)
    except Exception:
        return {"summary": "Summary unavailable", "action_items": []}

    # Parse and validate the reply
    try:
        result = SummaryResult(**json.loads(reply_text))
    except (ValueError, TypeError, ValidationError):
        return JSONResponse(status_code=502, content={"error": "invalid model output"})

    return result
