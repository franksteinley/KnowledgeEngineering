import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig
tokenizer = AutoTokenizer.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat", use_fast=False, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat", torch_dtype=torch.float16, trust_remote_code=True)
model = model.quantize(8).cuda() 
model.generation_config = GenerationConfig.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat")
while(True):
    inputs=input("请输入：")
    messages = []
    messages.append({"role": "user", "content": inputs})
    response = model.chat(tokenizer, messages)
    print(response)