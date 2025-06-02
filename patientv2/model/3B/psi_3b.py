from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from transformers import BitsAndBytesConfig, Trainer, DataCollatorWithPadding
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import torch
import os
import json

# ------------------------------
# 1. 모델 설정
# ------------------------------
base_model = "Qwen/Qwen2.5-3B-Instruct"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=quant_config,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # Padding 처리

# ------------------------------
# 2. LoRA 설정
# ------------------------------
lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)

model = get_peft_model(model, lora_config)

# ------------------------------
# 3. 데이터셋 로드 (ChatML → Prompt 텍스트로 변환)
# ------------------------------
dataset = load_dataset("json", data_files="/data/yoonsuh0615/repos/patientv2/data/patient_psi_chatml.jsonl")

# ------------------------------
# 4. Prompt Formatting & Tokenization
# ------------------------------
def format_and_tokenize(example):
    msgs = example["messages"]
    prompt_parts = []
    assistant_text = None

    for msg in msgs:
        role = msg["role"]
        content = msg["content"].strip()
        if role == "assistant":
            assistant_text = content
            break
        prompt_parts.append(f"<|im_start|>{role}\n{content}<|im_end|>")

    prompt = "\n".join(prompt_parts) + "\n<|im_start|>assistant\n"
    if not assistant_text:
        return None  # 필터링

    prompt_tokens = tokenizer(prompt, truncation=True, padding=False, add_special_tokens=False)
    assistant_tokens = tokenizer(assistant_text, truncation=True, padding=False, add_special_tokens=False)

    input_ids = prompt_tokens["input_ids"] + assistant_tokens["input_ids"]
    labels = [-100] * len(prompt_tokens["input_ids"]) + assistant_tokens["input_ids"]

    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor([1] * len(input_ids), dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }

tokenized_dataset = dataset["train"].map(format_and_tokenize)
tokenized_dataset = tokenized_dataset.filter(lambda x: x is not None)

# ------------------------------
# 5. 학습 설정
# ------------------------------
from torch.nn.utils.rnn import pad_sequence

def custom_collator(batch):
    input_ids = pad_sequence([torch.tensor(item["input_ids"], dtype=torch.long) for item in batch], batch_first=True, padding_value=tokenizer.pad_token_id)
    attention_mask = pad_sequence([torch.tensor(item["attention_mask"], dtype=torch.long) for item in batch], batch_first=True, padding_value=0)
    labels = pad_sequence([torch.tensor(item["labels"], dtype=torch.long) for item in batch], batch_first=True, padding_value=-100)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

data_collator = custom_collator

EPOCHS = [2, 4, 6, 8, 10]
LRS = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]

for epoch in EPOCHS:
    for lr in LRS:
        output_dir = Path(__file__).parent / "model" / f"3B_EP{epoch}_LR{lr:.0e}".replace("e-0", "e-").replace("e+0", "e+")
        if output_dir.exists():
            print(f"⏩ Skipping: {output_dir} already exists")
            continue
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            per_device_train_batch_size=2,
            gradient_accumulation_steps=8,
            learning_rate=lr,
            num_train_epochs=epoch,
            lr_scheduler_type="cosine",
            warmup_steps=50,
            fp16=True,
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=2,
            report_to="none"
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=tokenizer,
            data_collator=data_collator
        )

        print(f"🚀 Start training: epoch={epoch}, lr={lr}")
        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"✅ Finished training: {output_dir}")
