"""CHAT AI: small FastAPI app with a server-side Gemini integration."""
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

app = FastAPI(title="CHAT AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

ASSISTANTS = {
    "master": ("Master AI", "A versatile, thoughtful general assistant."),
    "study": ("Study Buddy", "Teach clearly, break topics into steps, and encourage learning."),
    "coding": ("Coding Assistant", "Help with programming, debugging, and technical concepts."),
    "writing": ("Writing Assistant", "Help plan, draft, revise, and polish writing."),
    "maths": ("Maths Helper", "Explain math step by step and show the reasoning."),
    "science": ("Science Helper", "Explain science accurately in an accessible way."),
    "translator": ("Translator", "Translate faithfully and preserve tone. Ask if the target language is unclear."),
    "career": ("Career Guide", "Offer practical, supportive career exploration and job-search guidance."),
    "creative": ("Creative Ideas", "Brainstorm imaginative, useful, age-appropriate ideas."),
    "voice": ("Voice Assistant", "Be concise and conversational, with answers that sound natural when spoken."),
}

class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=12000)

class ChatRequest(BaseModel):
    assistant: str = "master"
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/api/health")
async def health():
    return {"ok": True, "configured": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="The server owner needs to set GEMINI_API_KEY in Render.")
    if request.assistant not in ASSISTANTS:
        raise HTTPException(status_code=400, detail="Choose one of the available assistants.")
    if any(message.role not in {"user", "model"} for message in request.messages):
        raise HTTPException(status_code=400, detail="Invalid conversation role.")

    name, description = ASSISTANTS[request.assistant]
    payload = {
        "system_instruction": {"parts": [{"text": (
            f"You are {name}, one of the assistants in CHAT AI. {description} "
            "Be helpful, honest, and clear. Use safe, age-appropriate language. "
            "Do not facilitate harm, exploitation, illegal activity, or dangerous instructions. "
            "For medical, legal, or financial topics, give general information and encourage consulting a qualified professional. "
            "If uncertain, say so. Master AI can handle varied topics and briefly identify when a specialist perspective is useful."
        )}]},
        "contents": [{"role": m.role, "parts": [{"text": m.content}]} for m in request.messages],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048},
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(API_URL, headers={"x-goog-api-key": api_key}, json=payload)
        if response.status_code >= 400:
            if response.status_code in (401, 403):
                raise HTTPException(status_code=502, detail="Gemini rejected the API key. Check GEMINI_API_KEY in Render.")
            if response.status_code == 429:
                raise HTTPException(status_code=503, detail="Gemini is busy or the API quota was reached. Please try again shortly.")
            raise HTTPException(status_code=502, detail="Gemini could not complete that request. Please try again.")
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise HTTPException(status_code=502, detail="Gemini could not provide a response to that message. Try rephrasing it.")
        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "\n".join(part.get("text", "") for part in parts if part.get("text"))
        if not answer:
            raise HTTPException(status_code=502, detail="Gemini returned an empty response. Please try again.")
        return {"reply": answer}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gemini took too long to respond. Please try again.")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach Gemini. Check the server connection and try again.")
