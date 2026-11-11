# CHAT AI

A responsive, ChatGPT-style web app with ten selectable assistants, browser speech input, and spoken responses. The FastAPI server sends chat requests to Gemini; the API key stays on the server.

## Run locally

1. Use Python 3.10 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Set `GEMINI_API_KEY` in your shell (never commit it or put it in browser code).
4. Start: `uvicorn app:app --host 0.0.0.0 --port 8000`
5. Open `http://localhost:8000`.

## Deploy on Render

Create a **Web Service** from this folder/repository. Render reads `render.yaml`, or configure the service manually:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Environment variable:** `GEMINI_API_KEY` = your Gemini API key (add it in Render → Environment; do not include it in this project or ZIP).
- Optional: `GEMINI_MODEL` (defaults to `gemini-2.5-flash`).

After setting the key, deploy or restart the service. `/api/health` reports whether the server has a key without exposing it. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

The project includes both Gunicorn and Uvicorn in `requirements.txt`. For local development, run `uvicorn app:app --host 0.0.0.0 --port 8000`; Render uses Gunicorn with Uvicorn workers.

## Voice support

Speech recognition uses the browser's Web Speech API and may require a supported browser and microphone permission; availability differs by browser and device. Speech synthesis uses the browser's built-in voices and may also be unavailable. CHAT AI detects each feature independently, disables unavailable controls, and explains the limitation. Voice input and spoken output are browser features, not Gemini audio generation.

## Assistants

Master AI, Study Buddy, Coding Assistant, Writing Assistant, Maths Helper, Science Helper, Translator, Career Guide, Creative Ideas, and Voice Assistant. Conversations are kept in this browser's local storage; there is no account or server-side chat history.
