from .base import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

class OpenPsiModel(BaseModel):
    def __init__(self, model_path="openpsi_0.5b_v3/checkpoint-186"):
        peft_config = PeftConfig.from_pretrained(model_path, local_files_only=True)
        base_model = AutoModelForCausalLM.from_pretrained(
            peft_config.base_model_name_or_path, torch_dtype=torch.float16
        )
        self.model = PeftModel.from_pretrained(base_model, model_path)
        self.model.eval()
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def generate(self, prompt: str) -> str:
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(input_ids=input_ids, max_new_tokens=512)
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded.split(prompt, 1)[-1].strip()