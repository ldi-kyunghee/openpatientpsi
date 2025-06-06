#from .openpsi_model_v2 import OpenPsiModelv2
from .openpsi_model import OpenPsiModel
from .gpt4o_model import GPT4OModel

model_registry = {
    #"openpsiv2": OpenPsiModelv2(),
    "openpsi": OpenPsiModel(),
    "gpt4o": GPT4OModel()
}