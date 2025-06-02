import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import random
MAX_EXAMPLES = 200  # 원하는 개수로 조절 가능
BASE_MODEL_DIR = "model/0.5B/model/0.5B_EP3_LR2e-4"
MODEL_DIR = BASE_MODEL_DIR
INPUT_FILE = "data/patient_psi_testml.jsonl"  # ChatML 입력 테스트셋
OUTPUT_FILE = "response/openpsi0.5B_response.jsonl"  # 생성된 응답 저장 경로

# 모델/토크나이저 불러오기
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

# 텍스트 생성 함수
def generate_response(chatml_messages, max_new_tokens=200):
    input_ids = tokenizer.apply_chat_template(chatml_messages, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    full_text = decoded[len(tokenizer.decode(input_ids[0], skip_special_tokens=True)):]
    return full_text.strip()


# 응답 생성 루프
with open(INPUT_FILE, "r") as f:
    lines = f.readlines()
    random.shuffle(lines)  # 랜덤 샘플링
lines = lines[:MAX_EXAMPLES]

results = []
for line in tqdm(lines, desc="Generating responses"):
    item = json.loads(line)
    messages = item["messages"][:-1]  # system + user (no assistant)
    response = generate_response(messages)
    results.append(response)

# 저장
with open(OUTPUT_FILE, "w") as f:
    for idx, r in enumerate(results):
        json.dump({"id": idx + 1, "response": r}, f, ensure_ascii=False)
        f.write("\n")

print(f"✅ 응답 생성 완료: {OUTPUT_FILE}")