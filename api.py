from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gemini_client import ask_gemini_with_function_calling


app = FastAPI(title="Vestel Yorum Asistanı")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Vestel Yorum Asistanı API çalışıyor."
    }


@app.post("/chat")
def chat(request: ChatRequest):

    answer = ask_gemini_with_function_calling(
        request.message
    )

    return {
    "reply": answer,
    "queries": [],
    "thread_id": None
    }
