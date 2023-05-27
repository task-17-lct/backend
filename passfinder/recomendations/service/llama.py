from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "IlyaGusev/llama_7b_ru_turbo_alpaca_lora"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
config = PeftConfig.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path, load_in_8bit=True, device_map="auto"
)
model = PeftModel.from_pretrained(model, MODEL_NAME)
model.eval()
