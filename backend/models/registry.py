from .openpsi_model import OpenPsiModel
from .gpt4o_model import GPT4OModel

model_registry = {
    "openpsi": OpenPsiModel(),
    "gpt4o": GPT4OModel()
}