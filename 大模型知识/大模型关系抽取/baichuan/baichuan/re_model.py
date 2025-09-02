import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig
tokenizer = AutoTokenizer.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat", use_fast=False, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat", torch_dtype=torch.float16, trust_remote_code=True)
# model = model.quantize(8).cuda() 
model.generation_config = GenerationConfig.from_pretrained("/data/huggingface/models/baichuan-inc_baichuan2-13b-chat")
with open('data.json', "r") as fh:
    data = json.load(fh)
result=[]
print('read done')
for sample in data:
    text = sample['text']
    prompt= "你是专门进行关系抽取的专家。请从 %s 中抽取关系三元组，请按照{头实体，关系，尾实体}的格式回答，候选关系有[导演，主演，编剧，时间]。" % (sample['text'])
    messages = []
    messages.append({"role": "user", "content": prompt})
    response = model.chat(tokenizer, messages)
    result.append({'text':text,
                   'result':response})
json_data = json.dumps(result,ensure_ascii=False, indent=4)
with open("result.json", "w",encoding = 'utf-8') as file:
    file.write(json_data)