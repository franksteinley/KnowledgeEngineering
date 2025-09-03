from http import HTTPStatus
import dashscope
import ujson as json


def call_with_messages():
    while(True):
        inputs=input("请输入：")
        messages = [
            {'role': 'user', 'content': inputs}]
        response = dashscope.Generation.call(
                'qwen1.5-32b-chat',
                messages=messages,
                result_format='message',  # set the result is message format.
        )
        if response.status_code == HTTPStatus.OK:
            print(response['output']['choices'][0]['message']['content'])
        else:
                print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))


if __name__ == '__main__':
    call_with_messages()