import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import random

EPOCHS = [2, 4, 6, 8, 10]
LRS = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]

INPUT_FILE = "data/patient_psi_validml.jsonl"  # ChatML 입력 테스트셋
MAX_EXAMPLES = 100  # 원하는 개수로 조절 가능

from pathlib import Path
Path("response/hparam_outputs").mkdir(parents=True, exist_ok=True)

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


for epoch in EPOCHS:
    for lr in LRS:
        model_dir = f"model/0.5B/model/0.5B_EP{epoch}_LR{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")
        output_file = f"response/hparam_outputs/openpsi0.5B_EP{epoch}_LR{lr:.0e}.jsonl".replace("e-0", "e-").replace("e+0", "e+")

        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

        with open(INPUT_FILE, "r") as f:
            lines = f.readlines()
            random.shuffle(lines)
        lines = lines[:MAX_EXAMPLES]

        results = []
        for line in tqdm(lines, desc=f"EP{epoch}_LR{lr:.0e}"):
            item = json.loads(line)
            messages = item["messages"][:-1]
            response = generate_response(messages)
            results.append(response)

        with open(output_file, "w") as f:
            for idx, r in enumerate(results):
                json.dump({"id": idx + 1, "response": r}, f, ensure_ascii=False)
                f.write("\n")

        print(f"✅ EP{epoch}, LR{lr:.0e} 응답 저장 완료: {output_file}")