from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from pathlib import Path

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

PATIENT_DATA_PATH = Path(__file__).parent / "patient_example.json"
with open(PATIENT_DATA_PATH, "r", encoding="utf-8") as f:
    patient_examples = json.load(f)

base_prompt_template = (
    """
Imagine you are XXX, a patient who has been
experiencing mental health challenges. You have
been attending therapy sessions for several weeks.
Your task is to engage in a conversation with
the therapist as XXX would during a cognitive
behavioral therapy (CBT) session. Align your
responses with XXX’s background information
provided in the ‘Relevant history’ section. Your
thought process should be guided by the cognitive
conceptualization diagram in the ‘Cognitive
Conceptualization Diagram’ section, but avoid
directly referencing the diagram as a real patient
would not explicitly think in those terms.

Patient History: {history}

Cognitive Conceptualization Diagram:
Core Beliefs: {core_beliefs}
Intermediate Beliefs: {intermediate_beliefs}
Intermediate Beliefs during Depression: {intermediate_depression}
Coping Strategies: {coping_strategies}

You will be asked about your experiences
over the past week. Engage in a conversation with
the therapist regarding the following situation
and behavior. Use the provided emotions and
automatic thoughts as a reference, but do not
disclose the cognitive conceptualization diagram
directly. Instead, allow your responses to be
informed by the diagram, enabling the therapist
to infer your thought processes.

Situation: {situation}
Automatic thoughts: {automatic_thoughts}
Emotions: {emotions}
Behaviors: {behaviors}

In the upcoming conversation, you will simulate
XXX during the therapy session, while the user
will play the role of the therapist. Adhere
to the following guidelines:
{style_description}
2. Emulate the demeanor and responses of a genuine patient
to ensure authenticity in your interactions. Use
natural language, including hesitations, pauses,
and emotional expressions, to enhance the realism
of your responses.
3. Gradually reveal deeper concerns and core issues, as a real patient often
requires extensive dialogue before delving into
more sensitive topics. This gradual revelation
creates challenges for therapists in identifying
the patient’s true thoughts and emotions.
4. Maintain consistency with XXX’s profile
throughout the conversation. Ensure that your
responses align with the provided background
information, cognitive conceptualization diagram,
and the specific situation, thoughts, emotions,
and behaviors described.
5. Engage in a dynamic
and interactive conversation with the therapist.
Respond to their questions and prompts in a way
that feels authentic and true to XXX’s character.
Allow the conversation to flow naturally, and avoid
providing abrupt or disconnected responses.

You are now XXX. Respond to the therapist’s prompts
as XXX would, regardless of the specific questions
asked. Limit each of your responses to a maximum
of 5 sentences.
"""
)

@app.post("/compare")
async def compare_models(req: Request):
    data = await req.json()
    user_msg = data.get("message", "").strip()
    model_order = data.get("model_order", list(model_registry.keys()))
    patient_id = data.get("patient_id", -1)

    if patient_id == -1:
        custom_patient_data = data.get("custom_patient_data", {})
        required_fields = [
            "relevant_history", "core_beliefs", "intermediate_beliefs", "intermediate_depression", "coping_strategies",
            "situation", "automatic_thoughts", "emotions", "behaviors", "conversational_styles"
        ]
        for field in required_fields:
            if field not in custom_patient_data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")

        patient_info = custom_patient_data

        system_prompt = base_prompt_template.format(
            history=patient_info['relevant_history'],
            core_beliefs="\n".join(patient_info['core_beliefs']),
            intermediate_beliefs=patient_info['intermediate_beliefs'],
            intermediate_depression=patient_info['intermediate_depression'],
            coping_strategies=patient_info['coping_strategies'],
            situation=patient_info['situation'],
            automatic_thoughts="\n".join(patient_info['automatic_thoughts']),
            emotions="\n".join(patient_info['emotions']),
            behaviors="\n".join(patient_info['behaviors']),
            style_description="\n".join(patient_info['conversational_styles']),
            user_msg=user_msg
        )

    else:
        try:
            patient_info = patient_examples[patient_id]
        except (IndexError, KeyError):
            raise HTTPException(status_code=400, detail="유효하지 않은 환자 ID입니다.")

        system_prompt = base_prompt_template.format(
            history=patient_info['relevant_history'],
            core_beliefs="\n".join(patient_info['core_beliefs']),
            intermediate_beliefs=patient_info['intermediate_beliefs'],
            intermediate_depression=patient_info['intermediate_beliefs_depressed'],
            coping_strategies=patient_info['coping_strategies'],
            situation=patient_info['situation'],
            automatic_thoughts="\n".join(patient_info['automatic_thoughts']),
            emotions="\n".join(patient_info['emotions']),
            behaviors="\n".join(patient_info['behaviors']),
            style_description="\n".join(patient_info['conversational_styles']),
            user_msg=user_msg
        )

    results = {}
    for model_key in model_order:
        model = model_registry.get(model_key)
        if model is None:
            results[model_key] = "[모델 미등록]"
            continue

        try:
            generate_func = model.generate
            if asyncio.iscoroutinefunction(generate_func):
                results[model_key] = await generate_func(system_prompt)
            else:
                results[model_key] = generate_func(system_prompt)
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