import requests
import json


def download_qrcode(url,name):
    res=requests.get(url)
    print("下载登录二维码中")
    with open(f"qrcode_{name}.jpg","wb")as f:
        f.write(res.content)

async def recv_json(websocket):
    server_response = await websocket.recv()
    # print(f"Received from server: {server_response}")
    info=json.loads(server_response)
    return info
