from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel
from drozd_server import DrozdServer, DrozdInfo
import os
from dotenv import load_dotenv
#Model settings

load_dotenv("config.env")
MODEL_PATH = os.environ.get("MODEL_PATH", "")

tokenizer = GPT2Tokenizer.from_pretrained(MODEL_PATH, clean_up_tokenization_spaces=False)
model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)

def on_prompt_GPT(prompt, temperature, length):
    prompt = f"{prompt}"

    outputs = generator(
        prompt,
        max_new_tokens=length,
        do_sample=True,
        temperature=temperature,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2
    )

    return outputs[0]["generated_text"]

info = DrozdInfo(MODEL_PATH)
server = DrozdServer(info, on_prompt_GPT)
server.run("localhost", 5001)