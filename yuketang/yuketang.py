import asyncio
import websockets
import json
import requests
import os
import time
import traceback
from util import *
from random import*
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qywxbot.send import *


class yuketang:
    def __init__(self,name) -> None:
        self.name=name
        self.cookie_filename=f"cookie_{name}"
        self.cookie=""
        self.lessonId=""
        self.Auth=""
        self.Authorization=""
        self.userid=""
        self.presentation=""
        self.problemid=""
        self.problems={}

        self.debug=True
        self.wx=False
        self.msgmgr=MsgManager(debug=self.debug,wx=self.wx)
        self.getcookie()
        self.start_time=time.time()
        self.slides=""

    def getcookie(self):
        if not os.path.exists(self.cookie_filename):
            self.msgmgr.sendMsg(f"正在第一次获取登录{self.name} cookie，请注意扫码",self.name)
            self.ws_controller(self.ws_login)
        with open(self.cookie_filename,"r")as f:
            self.cookie=f.read()
        if not self.check_cookie():
            self.msgmgr.sendMsg("cookie已失效，请重新扫码",self.name)
            self.ws_controller(self.ws_login)
        else:
            self.msgmgr.sendMsg(f"{self.name} cookie有效",self.name)

    def weblogin(self,UserID,Auth):
        url="https://www.yuketang.cn/pc/web_login"
        data={
            "UserID":UserID,
            "Auth":Auth
        }
        headers={
            "referer":"https://www.yuketang.cn/web?next=/v2/web/index&type=3",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Content-Type":"application/json"
        }
        res=requests.post(url=url,headers=headers,json=data)
        cookies = res.cookies
        self.cookie=""
        for k,v in cookies.items():
            self.cookie += f'{k}={v};'
        with open(self.cookie_filename,"w")as f:
            f.write(self.cookie)

    def check_cookie(self):
        info=self.get_basicinfo()
        if info.get("code")==0:
            return True
        return False
    
    def setAuthorization(self,res):
        if res.headers.get("Set-Auth") is not None:
            self.Authorization="Bearer "+res.headers.get("Set-Auth")

    def get_basicinfo(self):
        url="https://www.yuketang.cn/api/v3/user/basic-info"
        headers={
            "referer":"https://www.yuketang.cn/web?next=/v2/web/index&type=3",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "cookie":self.cookie
        }
        res=requests.get(url=url,headers=headers).json()
        return res
    
    def getlesson(self):
        url="https://www.yuketang.cn/api/v3/classroom/on-lesson-upcoming-exam"
        headers={
            "referer":"https://www.yuketang.cn/web?next=/v2/web/index&type=3",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "cookie":self.cookie
        }
        res=requests.get(url=url,headers=headers).json()
        try:
            self.lessonId=res['data']['onLessonClassrooms'][0]['lessonId']
            return True
        except Exception as e:
            return False
    
    def lesson_checkin(self):
        url="https://www.yuketang.cn/api/v3/lesson/checkin"
        headers={
            "referer":f"https://www.yuketang.cn/lesson/fullscreen/v3/{self.lessonId}?source=5",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Content-Type":"application/json; charset=utf-8",
            "cookie":self.cookie
        }
        data={
            "source":5,
            "lessonId":self.lessonId
        }
        res=requests.post(url=url,headers=headers,json=data)
        self.setAuthorization(res)
        self.Auth=res.json()['data']['lessonToken']
        self.userid=res.json()['data']['identityId']

    
    def fetch_presentation(self):
        url=f"https://www.yuketang.cn/api/v3/lesson/presentation/fetch?presentation_id={self.presentation}"
        headers={
            "referer":f"https://www.yuketang.cn/lesson/fullscreen/v3/{self.lessonId}?source=5",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "cookie":self.cookie,
            "Authorization":self.Authorization
        }
        res=requests.get(url=url,headers=headers)
        self.setAuthorization(res)
        info=res.json()
        slides=info['data']['slides']    #获得幻灯片列表
        for slide in slides:
            if slide.get("problem") is not None:
                self.problems[slide['id']]=slide['problem']
        if slides!=self.slides:
            self.slides=slides
            self.msgmgr.sendMsg("成功获取幻灯片",user=self.name)
        # print(self.problems)
        

    def answer(self):
        url="https://www.yuketang.cn/api/v3/lesson/problem/answer"
        headers={
            "referer":f"https://www.yuketang.cn/lesson/fullscreen/v3/{self.lessonId}?source=5",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "cookie":self.cookie,
            "Content-Type":"application/json",
            "Authorization":self.Authorization
        }
        data={
            "dt":int(time.time()*1000),
            "problemId":self.problemid,
            "problemType":self.problems[self.problemid]['problemType'],
            "result":self.problems[self.problemid]['answers']
        }
        res=requests.post(url=url,headers=headers,json=data)
        self.setAuthorization(res)
        self.msgmgr.sendMsg(json.dumps(data),self.name)




    def ws_controller(self,func,loop=None):
        if loop is None:
            loop=asyncio.get_event_loop()
        while True and time.time()-self.start_time<6000:
            try:
                loop.run_until_complete(func())
                break
            except:
                print(traceback.format_exc())
                print("出现异常，重试中")
                pass


    async def ws_login(self):
        uri = "wss://www.yuketang.cn/wsapp/"
        async with websockets.connect(uri) as websocket:
            # 发送 "hello" 消息以建立连接
            hello_message = {
                "op":"requestlogin",
                "role":"web",
                "version":1.4,
                "type":"qrcode",
                "from":"web"
            }
            await websocket.send(json.dumps(hello_message))

            server_response = await recv_json(websocket)
            qrcode_url=server_response['ticket']

            download_qrcode(qrcode_url,self.name)
            get_token()
            send_image(upload_file(f"qrcode_{self.name}.jpg"),self.name)

            server_response = await asyncio.wait_for(recv_json(websocket),timeout=120)
            self.weblogin(server_response['UserID'],server_response['Auth'])



    
    async def ws_lesson(self):
        uri = "wss://www.yuketang.cn/wsapp/"
        async with websockets.connect(uri) as websocket:
            # 发送 "hello" 消息以建立连接
            hello_message = {
                "op": "hello",
                "userid": self.userid,
                "role": "student",
                "auth": self.Auth,
                "lessonid": self.lessonId
            }
            flag=1
            await websocket.send(json.dumps(hello_message))

            while True and time.time()-self.start_time<6000:
                server_response = await recv_json(websocket)
                op=server_response['op']
                if op=="showpresentation" or op=="presentationupdated" or op=="presentationcreated":
                    self.presentation=server_response['presentation']
                    self.fetch_presentation()
                    flag=0
                elif op=="slidenav" and flag==1:
                    self.presentation=server_response['slide']['pres']
                    self.fetch_presentation()
                    flag=0
                elif op=="unlockproblem":
                    self.problemid=server_response['problem']['prob']
                    time.sleep(randint(10,20))
                    self.answer()
                elif op=="lessonfinished":
                    self.msgmgr.sendMsg("课程结束了",user=self.name)
                    break

                
            


def ykt_user(name):
    count=0
    ykt=yuketang(name)
    while not ykt.getlesson():
        time.sleep(30)
        count+=1
        if count>200:
            return
    ykt.lesson_checkin()
    ykt.ws_controller(ykt.ws_lesson)
    



