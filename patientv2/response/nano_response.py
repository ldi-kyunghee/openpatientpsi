import json
import random
from tqdm import tqdm
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 경로 설정
INPUT_FILE = "data/patient_psi_testml.jsonl"  # ChatML 입력 테스트셋
OUTPUT_FILE = "response/gpt4nano_response.jsonl"  # 생성된 응답 저장 경로

# 최대 생성 개수
MAX_EXAMPLES = 200

# 응답 생성 함수
def generate_response(messages, model="gpt-4.1-mini"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
        top_p=0.9,
    )
    return response.choices[0].message.content.strip()

# 입력 데이터 불러오기
with open(INPUT_FILE, "r") as f:
    lines = f.readlines()
    random.shuffle(lines)
lines = lines[:MAX_EXAMPLES]

# 응답 생성 루프
results = []
for line in tqdm(lines, desc="Generating responses with GPT-4.1-nano"):
    item = json.loads(line)
    # Use the system + user messages from the dataset directly
    messages = item["messages"]
    full_response = generate_response(messages)
    # Extract full response as patient's reply
    response = full_response.strip()
    results.append({
        "id": len(results) + 1,
        "response": response
    })

# 저장
with open(OUTPUT_FILE, "w") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"✅ GPT-4.1-nano 응답 생성 완료 (응답만 저장됨): {OUTPUT_FILE}")