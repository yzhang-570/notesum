# NoteSum
Summarizes a text note into a short summary plus action items.

## Behavior
- The model is read from the `MODEL_NAME` environment variable, default `claude-haiku-5-5`.
- Every model reply is validated against a schema. Invalid output returns HTTP 502.
- Notes are never logged or stored.
- Model calls time out after 10 seconds.
- Requests are limited to 10 per minute per IP.

## Run
pip install -r requirements.txt  
ANTHROPIC_API_KEY=... uvicorn app:app --port 8080  

## Deploy
docker build -t notesum . && docker run -p 8080:8080 -e ANTHROPIC_API_KEY=... notesum
