from .base import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

class OpenPsi3BModel(BaseModel):
    def __init__(self, model_path="openpsi_3b/checkpoint-315"):
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
            output = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,  # ex) 100 정도로 충분
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                stopping_criteria=stopping_criteria
            )
        
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded.split(prompt, 1)[-1].strip()