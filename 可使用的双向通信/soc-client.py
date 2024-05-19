import requests
import json
import threading
import time

# 服务器IP地址和端口号
server_url = 'http://123.57.236.111:802'

def send_message():
    while True:
        # 从控制台获取输入的消息
        direction = input('请输入方向: ')
        hex_code = input('请输入十六进制报文: ')

        # 构造消息
        message = {
            'direction': direction,
            'hex_code': hex_code
        }

        # 发送消息
        try:
            response = requests.post(f'{server_url}/send_message/', json=message)
            print('发送消息的响应:', response.json())
        except requests.exceptions.RequestException as e:
            print(f"发送消息时发生错误: {e}")

        # 如果输入 'stop' 则终止会话
        if direction.lower() == 'stop' or hex_code.lower() == 'stop':
            break

def poll_for_notifications():
    while True:
        # 发送请求以轮询新消息
        try:
            response = requests.get(f'{server_url}/get_notifications/')
            notifications = response.json()
            print('收到来自服务器的新消息:', notifications)
        except requests.exceptions.RequestException as e:
            print(f"轮询消息时发生错误: {e}")

        # 每隔一秒轮询一次
        time.sleep(1)

if __name__ == "__main__":
    # 启动发送消息的线程
    send_thread = threading.Thread(target=send_message)
    send_thread.start()

    # 启动轮询消息的线程
    poll_thread = threading.Thread(target=poll_for_notifications)
    poll_thread.start()

    # 等待两个线程结束
    send_thread.join()
    poll_thread.join()
