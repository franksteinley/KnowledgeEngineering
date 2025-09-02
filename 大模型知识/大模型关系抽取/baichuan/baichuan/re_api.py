from http import HTTPStatus
import dashscope
import ujson as json
result=[]

def call_with_messages():
    with open('data2.json', "r",encoding="utf-8") as fh:
        data = json.load(fh)
    for sample in data:
        instruction = sample['instruction']
        input = sample['input']
        prompt= instruction + input
        messages = [
            {'role': 'user', 'content': prompt}]
        response = dashscope.Generation.call(
            'qwen1.5-32b-chat',
            messages=messages,
            result_format='message',  # set the result is message format.
        )
        if response.status_code == HTTPStatus.OK:
            result.append({'instruction':instruction,
                           'input':input,
                           'result':response['output']['choices'][0]['message']['content']})
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
    json_data = json.dumps(result,ensure_ascii=False, indent=4)
    with open("result2.json", "w",encoding = 'utf-8') as file:
        file.write(json_data)


if __name__ == '__main__':
    call_with_messages()