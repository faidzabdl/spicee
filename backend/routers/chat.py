from fastapi import APIRouter
from models import ChatRequest, ChatResponse
from langflow_client import call_chat_flow
from db import supabase

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply, success = await call_chat_flow(req.message, req.session_id)

    saved = False
    if success:
        try:
            supabase.table("chats").insert([
                {"session_id": req.session_id, "role": "user", "message": req.message},
                {"session_id": req.session_id, "role": "assistant", "message": reply},
            ]).execute()
            saved = True
        except Exception:
            saved = False

    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        saved=saved,
    )
