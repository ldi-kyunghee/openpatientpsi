from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from models.registry import model_registry



app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 리더보드 초기화
leaderboard = {
    key: 0 for key in model_registry.keys()
}
leaderboard.update({"Tie": 0, "Both Bad": 0})

@app.post("/compare")
async def compare_models(req: Request):
    data = await req.json()
    user_msg = data.get("message", "").strip()
    model_order = data.get("model_order", list(model_registry.keys()))

    results = {}
    for model_key in model_order:
        model = model_registry.get(model_key)
        if model is None:
            results[model_key] = "[모델 미등록]"
            continue

        try:
            generate_func = model.generate
            if asyncio.iscoroutinefunction(generate_func):
                results[model_key] = await generate_func(user_msg)
            else:
                results[model_key] = generate_func(user_msg)
        except Exception as e:
            results[model_key] = f"[{model_key} 응답 오류: {e}]"

    return results

@app.post("/vote")
async def vote(req: Request):
    data = await req.json()
    model_order = data.get("model_order", list(model_registry.keys()))
    vote_option = data.get("vote", "")

    if vote_option not in ["A is better", "B is better", "Tie", "Both are bad"]:
        raise HTTPException(status_code=400, detail="잘못된 투표 옵션입니다.")

    if vote_option == "A is better":
        leaderboard[model_order[0]] += 1
    elif vote_option == "B is better":
        leaderboard[model_order[1]] += 1
    elif vote_option == "Tie":
        leaderboard["Tie"] += 1
    elif vote_option == "Both are bad":
        leaderboard["Both Bad"] += 1

    return {"message": "투표가 성공적으로 반영되었습니다."}

@app.get("/leaderboard")
async def get_leaderboard():
    return leaderboard
