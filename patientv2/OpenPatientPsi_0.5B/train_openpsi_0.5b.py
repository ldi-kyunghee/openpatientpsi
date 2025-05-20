import os
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
import torch
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
DATA_PATH = "../data/patient_psi_chatml.jsonl"
BASE_OUTPUT = "output"

EPOCHS = [2, 4, 6, 8, 10]
LEARNING_RATES = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]

# Load once
print("🔄 Loading base tokenizer and model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# QLoRA 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
base_model = prepare_model_for_kbit_training(base_model)

# Load and preprocess dataset
dataset = load_dataset("json", data_files=DATA_PATH, split="train")

def format_prompt(sample):
    for msg in sample["messages"]:
        if msg["role"] == "user":
            return {"text": msg["content"]}
    return {"text": ""}

dataset = dataset.map(format_prompt)
dataset = dataset.remove_columns([col for col in dataset.column_names if col != "text"])

total_start_time = time.time()

# Iterate over grid
for epoch in EPOCHS:
    for lr in LEARNING_RATES:
        exp_name = f"0.5B_EP{epoch}_LR{str(lr).replace('.', 'e-')}"
        output_dir = os.path.join(BASE_OUTPUT, exp_name)
        print(f"\n🚀 Training {exp_name} ...\n")

        # Reset model for each run (deep copy LoRA onto fresh base)
        model = get_peft_model(base_model, LoraConfig(
            r=8,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        ))

        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=2,
            num_train_epochs=epoch,
            learning_rate=lr,
            fp16=True,
            logging_steps=10,
            save_strategy="epoch",
            report_to="none"
        )

        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            args=training_args
        )

        start_time = time.time()
        trainer.train()
        elapsed = time.time() - start_time
        mins = elapsed // 60
        secs = int(elapsed % 60)
        print(f"⏱️ Training time for {exp_name}: {int(mins)}m {secs}s")

        # Save results
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"✅ Saved: {output_dir}")

total_elapsed = time.time() - total_start_time
total_mins = total_elapsed // 60
total_secs = int(total_elapsed % 60)
print(f"\n🧠 Total training time: {int(total_mins)}m {total_secs}s")