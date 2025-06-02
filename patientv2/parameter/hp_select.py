import json
import os
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from sentence_transformers import SentenceTransformer, util
import time

# 설정
EVAL_FILE = "data/patient_psi_validml.jsonl"
OUTPUT_FILE = "parameter/psi0.5b_hparam_selection.jsonl"
BASE_DIR = "/data/yoonsuh0615/repos/patientv2/model/0.5B/model/0.5B_EP{}_LR{}"
BASE_DIR = BASE_DIR.replace("LR{}", "LR{:.0e}")
EPOCHS = [2, 4, 6, 8, 10]
LRS = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]
MAX_NEW_TOKENS = 200

# 평가 데이터 로드
with open(EVAL_FILE, "r") as f:
    eval_lines = [json.loads(l) for l in f.readlines()]

# 결과 저장 리스트
all_results = []

from pathlib import Path
for epoch in EPOCHS:
    for lr in LRS:
        model_path = Path(__file__).resolve().parent.parent / f"model/0.5B/model/0.5B_EP{epoch}_LR{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")
        print(f"\n🚀 Loading model: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_path,
            local_files_only=True,
            device_map="auto",
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True
        )

        results = {"model_dir": model_path, "responses": []}
        start_time = time.time()
        for item in tqdm(eval_lines, desc=f"Evaluating EP{epoch}_LR{lr}"):
            messages = item["messages"]
            input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
            with torch.no_grad():
                output = model.generate(
                    input_ids,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id
                )
            decoded = tokenizer.decode(output[0], skip_special_tokens=True)
            prompt = tokenizer.decode(input_ids[0], skip_special_tokens=True)
            generated = decoded[len(prompt):].strip()
            results["responses"].append(generated)

            current_step = len(results["responses"])
            elapsed = time.time() - start_time
            steps_per_sec = current_step / elapsed if elapsed > 0 else 0
            total_steps = len(eval_lines)
            remaining_steps = total_steps - current_step
            eta_sec = int(remaining_steps / steps_per_sec) if steps_per_sec > 0 else 0
            eta_min, eta_sec = divmod(eta_sec, 60)
            print(f"[{current_step}/{total_steps}] 남은 시간: {eta_min}분 {eta_sec}초")

        # 모델별 결과 임시 저장
        partial_save_path = Path("parameter") / f"result_EP{epoch}_LR{lr:.0e}.json".replace("e-0", "e-").replace("e+0", "e+")
        with open(partial_save_path, "w") as pf:
            json.dump({
                "model_dir": str(model_path),
                "responses": results["responses"]
            }, pf, ensure_ascii=False, indent=2)

        all_results.append(results)


OUTPUT_DIR = "parameter/dev_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
for result in all_results:
    model_name = Path(result["model_dir"]).name
    output_file = Path(OUTPUT_DIR) / f"{model_name}.json"
    with open(output_file, "w") as f:
        json.dump({
            "model_dir": str(result["model_dir"]),
            "responses": result["responses"]
        }, f, ensure_ascii=False, indent=2)
print("✅ 모든 모델에 대한 검증 응답 생성 완료:", OUTPUT_DIR)