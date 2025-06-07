from .openpsi_05B_model import OpenPsi05BModel
from .openpsi_3B_model import OpenPsi3BModel
from .gpt4o_model import GPT4OModel

model_registry = {
    "openpsi": OpenPsi05BModel(),
    "gpt4o": GPT4OModel()
}