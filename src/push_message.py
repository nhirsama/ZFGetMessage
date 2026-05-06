import json

import requests


class PushMessage:
    def __init__(self, env, result):
        self.env = env
        self.result = result

    def push(self, title, content):
        url = self.env['push_url'] + self.env['token']
        # 创建一个字典，包含标题和内容
        data = {"title": title, "content": content}
        # 将字典转换为JSON字符串，并编码为UTF-8
        body = json.dumps(data).encode(encoding="utf-8")
        # 定义HTTP请求头，设置内容类型为JSON
        headers = {"Content-Type": "application/json"}
        # 发送POST请求，携带JSON数据和请求头
        response = requests.post(url, data=body, headers=headers, timeout=15)
        response.raise_for_status()
        # 解析响应的JSON数据，转换为字典
        return response.json()

    def check_message(self):
        if self.result['has_error']:
            val = self.push("错误日志", self.result['content'])
            print(val.get('error_message', val))
            return "出现错误，已推送错误日志"
        elif self.result['has_new']:
            val = self.push(self.result['title'], self.result['content'])
            print(val.get('error_message', val))
            return f"{self.result['title']}有更新，已推送"
        else:
            return f"{self.result['title']}无变动"
