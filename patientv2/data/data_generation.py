import os
import json
import random
import openai
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 고정 카테고리
CORE_BELIEF_CATEGORIES = {
    "helpless": [
        "I am incompetent", "I am helpless", "I am powerless, weak, vulnerable",
        "I am a victim", "I am needy", "I am trapped", "I am out of control",
        "I am a failure, loser", "I am defective"
    ],
    "unlovable": [
        "I am unlovable", "I am unattractive", "I am undesirable, unwanted",
        "I am bound to be rejected", "I am bound to be abandoned", "I am bound to be alone"
    ],
    "worthless": [
        "I am worthless, waste", "I am immoral", "I am bad - dangerous, toxic, evil"
    ]
}

EMOTIONS = [
    "anxious", "sad", "angry", "hurt", "ashamed", "guilty",
    "jealous", "disappointed", "suspicious"
]

SITUATIONS = [
    "family dynamics", "workplace pressure", "relationship dynamics",
    "social interactions", "personal growth issues", "financial concerns", "daily life stressors"
]

CONVERSATIONAL_STYLES = ["plain", "upset", "verbose", "reserved", "tangent", "pleasing"]

# JSON 파싱
def safe_extract_json(text: str) -> Dict:
    import re
    match = re.search(r"\{[\s\S]+\}", text)
    return json.loads(match.group(0)) if match else {}

# GPT 호출: CCD 생성
def generate_ccd_fields(core_belief: str, situation: str, forced_styles: List[str]) -> Dict:
    system_prompt = (
        "You are a CBT expert. Based on the given core belief and situation, generate a cognitive conceptualization diagram (CCD) as JSON with the following fields:\n"
        "- intermediate_beliefs: string\n"
        "- coping_strategies: string\n"
        "- automatic_thoughts: 3 specific, varied, non-generic thoughts\n"
        "- emotions: choose 3 from [anxious, sad, angry, hurt, ashamed, guilty, jealous, disappointed, suspicious]\n"
        "- behaviors: 3 diverse behavioral reactions (e.g., withdrawal, overcompensation, avoidance)\n"
        f"- conversational_styles: exactly these two: {forced_styles}\n"
        "Return valid JSON only."
    )

    user_prompt = f'Core belief: "{core_belief}"\nSituation: "{situation}"'

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return safe_extract_json(response.choices[0].message.content)

# GPT 호출: relevant_history 생성
def generate_relevant_history(core_belief: str) -> str:
    system_prompt = (
        "Generate a realistic 2-3 sentence relevant history for a patient who developed the following core belief. "
        "Include family background or early environment. Keep it causal and natural."
    )
    user_prompt = f'Core belief: "{core_belief}"'

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 환자 모델 생성
def generate_patient_model(patient_id: int) -> Dict:
    belief_group = random.choice(list(CORE_BELIEF_CATEGORIES.keys()))
    core_belief = random.choice(CORE_BELIEF_CATEGORIES[belief_group])
    situation_type = random.choice(SITUATIONS)
    situation = f"The patient encountered a stressful event related to {situation_type}."

    # 균형 잡힌 스타일 샘플링
    forced_styles = random.sample(CONVERSATIONAL_STYLES, 2)
    relevant_history = generate_relevant_history(core_belief)
    ccd = generate_ccd_fields(core_belief, situation, forced_styles)

    return {
        "id": patient_id,
        "relevant_history": relevant_history,
        "situation": situation,
        "core_beliefs": [core_belief],
        "intermediate_beliefs": ccd.get("intermediate_beliefs", ""),
        "coping_strategies": ccd.get("coping_strategies", ""),
        "automatic_thoughts": ccd.get("automatic_thoughts", []),
        "emotions": ccd.get("emotions", []),
        "behaviors": ccd.get("behaviors", []),
        "conversational_styles": ccd.get("conversational_styles", forced_styles)
    }

# 전체 생성
def generate_dataset(n: int) -> List[Dict]:
    dataset = []
    for i in range(n):
        print(f"🧠 Generating patient {i+1}...")
        try:
            patient = generate_patient_model(i + 1)
            dataset.append(patient)
        except Exception as e:
            print(f"❌ Error for patient {i+1}: {e}")
    return dataset

# 저장
def save_to_json(data: List[Dict], filename="patient_psi_dataset.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 실행
if __name__ == "__main__":
    dataset = generate_dataset(2)
    save_to_json(dataset)
    print(f"✅ {len(dataset)}개 샘플 생성 완료 (저장됨)")
