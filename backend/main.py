from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수 및 모델 API 설정
VLLM_URL = os.getenv("VLLM_API_URL", "http://localhost:8000/v1/chat/completions")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VLLM_MODEL = "beomi/KoAlpaca-Polyglot-13B"
OPENAI_MODEL = "gpt-3.5-turbo"

# 리더보드 데이터: 간단한 통계 구조
leaderboard = {
    "vllm": 0,
    "chatgpt": 0,
    "Tie": 0,
    "Both Bad": 0
}

@app.post("/compare")
async def compare_models(req: Request):
    data = await req.json()
    user_msg = data.get("message", "")
    
    if not user_msg.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어 있습니다.")
    
    prompt = [{"role": "user", "content": user_msg}]
    
    vllm_output = "(응답 실패)"
    openai_output = "(응답 실패)"
    
    # 모델 순서 추가
    model_order = data.get("model_order", ["vllm", "chatgpt"])

    async with httpx.AsyncClient() as client:
        # vLLM 요청
        try:
            vllm_resp = await client.post(
                VLLM_URL,
                json={"model": VLLM_MODEL, "messages": prompt},
                timeout=30
            )
            vllm_resp.raise_for_status()
            vllm_output = vllm_resp.json()["choices"][0]["message"]["content"]
        except httpx.RequestError:
            vllm_output = "[vLLM 응답 오류]"
        
        # OpenAI 요청
        try:
            openai_resp = await client.post(
                OPENAI_URL,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={"model": OPENAI_MODEL, "messages": prompt},
                timeout=30
            )
            openai_resp.raise_for_status()
            openai_output = openai_resp.json()["choices"][0]["message"]["content"]
        except httpx.RequestError:
            openai_output = "[OpenAI 응답 오류]"

    return {
        model_order[0]: vllm_output.strip(),
        model_order[1]: openai_output.strip()
    }


@app.post("/vote")
async def vote(req: Request):
    data = await req.json()
    model_order = data.get("model_order", ["vllm", "chatgpt"])  # A/B 모델 순서
    vote_option = data.get("vote", "")

    if vote_option not in ["A is better", "B is better", "Tie", "Both are bad"]:
        raise HTTPException(status_code=400, detail="잘못된 투표 옵션입니다.")
    
    # A/B에 해당하는 모델을 정리
    if vote_option == "A is better":
        leaderboard[model_order[0]] += 1
    elif vote_option == "B is better":
        leaderboard[model_order[1]] += 1
    elif vote_option == "Tie":
        leaderboard["Tie"] += 1
    elif vote_option == "Both are bad":
        leaderboard["Both Bad"] += 1

    return {"message": "투표가 성공적으로 반영되었습니다."}

# 리더보드 데이터
leaderboard = {
    "vllm": 0,
    "chatgpt": 0,
    "Tie": 0,
    "Both Bad": 0
}

@app.get("/leaderboard")
async def get_leaderboard():
    return leaderboard
