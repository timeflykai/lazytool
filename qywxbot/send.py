import json
import requests
import os
import time

global ACCESS_TOKEN

AgentId = 'xxx'
Secret = 'xxxxx'
CompanyId = 'xxxxx'



class MsgManager:
    def __init__(self,debug=False,wx=True) -> None:
        self.debug=debug
        self.wx=wx

    def sendMsg(self,msg="this is a test msg",user=None):
        if self.debug:
            print(f"发送给{user}的消息: {msg}")
        if self.wx and user is not None:
            send2wechat(msg,user)

def get_token():
    global ACCESS_TOKEN
    # 通行密钥
    ACCESS_TOKEN = None
    # 如果本地保存的有通行密钥且时间不超过两小时，就用本地的通行密钥
    if os.path.exists('ACCESS_TOKEN.txt'):
        txt_last_edit_time = os.stat('ACCESS_TOKEN.txt').st_mtime
        now_time = time.time()
        if now_time - txt_last_edit_time < 7200:  # 官方说通行密钥2小时刷新
            with open('ACCESS_TOKEN.txt', 'r') as f:
                ACCESS_TOKEN = f.read()
                # print(ACCESS_TOKEN)
    # 如果不存在本地通行密钥，通过企业ID和应用Secret获取
    if not ACCESS_TOKEN:
        r = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CompanyId}&corpsecret={Secret}').json()
        ACCESS_TOKEN = r["access_token"]
        # print(ACCESS_TOKEN)
        # 保存通行密钥到本地ACCESS_TOKEN.txt
        with open('ACCESS_TOKEN.txt', 'w', encoding='utf-8') as f:
            f.write(ACCESS_TOKEN)



def upload_file(filepath):
    TYPE="file"
    files={
        'file':open(filepath,'rb')
    }
    r=requests.post(f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={ACCESS_TOKEN}&type={TYPE}',files=files)
    r.json()
    return r.json()['media_id']

def send_file(id,user):
    data = {
        "touser": user,
        "msgtype": "file",
        "agentid": f"{AgentId}",
        "file":  {'media_id':id}
    }
    # 字典转成json，不然会报错
    data = json.dumps(data)
    # 发送消息
    r = requests.post(
        f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}', data=data)
    
def send2wechat(message,user):
    # 要发送的信息格式
    get_token()
    data = {
        "touser": user,
        "msgtype": "text",
        "agentid": f"{AgentId}",
        "text": {"content": f"{message}"}
    }
    # 字典转成json，不然会报错
    data = json.dumps(data)
    # 发送消息
    r = requests.post(
        f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}', data=data)

def send_image(id,user):
    # 要发送的信息格式
    data = {
        "touser": user,
        "msgtype": "image",
        "agentid": f"{AgentId}",
        "image":  {'media_id':id}
    }
    # 字典转成json，不然会报错
    data = json.dumps(data)
    # 发送消息
    r = requests.post(
        f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}', data=data)
    #print(r.json())




def get_useridlist():
    print(ACCESS_TOKEN)
    url="https://qyapi.weixin.qq.com/cgi-bin/user/list_id?access_token={ACCESS_TOKEN}"
    r=requests.post(url)
    print(r.json())

