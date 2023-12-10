import requests
import json
from AESEnCrpT import AESEnCrpTor


class chaoxing:
    def __init__(self,config) -> None:
        self.phone=config.get("phone")
        self.password=config.get("password")
        self.uid=""
        self.courseId="xxx"
        self.classId="xxx"
        self.longitude=config.get("longitude")
        self.latitude=config.get("latitude")
        self.address=config.get("address")
        self.session=requests.Session()
        self.headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.120 Mobile Safari/537.36 com.chaoxing.mobile/ChaoXingStudy_3_4.1.2_android_phone_335_2 (@Kalimdor)_-1533462925",
            "referer":"https://mobilelearn.chaoxing.com/widget/sign/e",
            "X-Requested-With":"com.chaoxing.mobile"
        }
        self.login()
    
    def login(self):
        url="https://passport2.chaoxing.com/fanyalogin"
        key="u2oh6Vu^HWe4_AES"
        aee=AESEnCrpTor(key,key)
        phone=aee.aes_encrypt(self.phone)
        passwd=aee.aes_encrypt(self.password)
        data={
            "fid": -1,
            "uname": phone,
            "password": passwd,
            "refer": "http%3A%2F%2Fi.mooc.chaoxing.com",
            "t": True,
            "forbidotherlogin": 0,
            "validate": "",
            "doubleFactorLogin": 0,
            "independentId": 0,
        }
        self.session.post(url,headers=self.headers,data=data)
        self.uid=self.get_cookie()['UID']


    def get_cookie(self):
        return self.session.cookies.get_dict()


    def token(self):  # 获取上传图片用的token
        url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
        res = self.session.get(url, headers=self.headers)
        tokendict = json.loads(res.text)
        return tokendict['_token']

    def upload_pic(self,picname):
        url = 'https://pan-yz.chaoxing.com/upload'
        files = {
            'file': (picname, open(picname, 'rb'),'image/webp,image/*',) 
        }
        data={
            'puid':self.uid,
            "_token":self.token()
        }
        response=self.session.post(url=url,data=data,files=files,headers=self.headers)
        objectid=json.loads(response.text)['objectId']
        return objectid

    def index(self):
        url="http://i.mooc.chaoxing.com/space/index"
        response=self.session.get(url=url,headers=self.headers)
        print(response.content.decode())
    
    def getactivelist(self):
        url=f"http://mobilelearn.chaoxing.com/v2/apis/active/student/activelist?fid=0&courseId={self.courseId}&classId={self.classId}&showNotStartedActive=0"
        response=self.session.get(url=url,headers=self.headers)
        activelist=json.loads(response.content.decode())['data']['activeList']
        return activelist

    def presignin(self,activeId):
        preurl=f"https://mobilelearn.chaoxing.com/newsign/preSign?courseId={self.courseId}&classId={self.classId}&activePrimaryId={activeId}&general=1&sys=1&ls=1&appType=15&&tid=&uid={self.uid}&ut=s"
        self.session.get(url=preurl,headers=self.headers)

    def get_enc(self,activeId):
        preurl=f"https://mobilelearn.chaoxing.com/v2/apis/sign/refreshQRCode?activeId={activeId}"
        response=self.session.get(url=preurl,headers=self.headers)
        data=json.loads(response.content.decode())['data']
        return data['enc'],data['signCode']

    def signin(self,mode_info,activeid=None):
        if activeid is None:
            activeid=self.getactivelist()[0]['id']
        self.presignin(activeid)
        data={
            "activeId":activeid,
            "uid":self.uid,
        }
        if mode_info['mode']=="pic":
            picpath=mode_info['picpath']
            object_id=self.upload_pic(picpath)
            data['objectId']=object_id
        elif mode_info['mode']=="location":
            data['longitude']=self.longitude
            data['latitude']=self.latitude
            data['address']=self.address
        elif mode_info['mode']=='qrcode':
            data['latitude']=-1
            data['longitude']=-1
            data['enc']=mode_info['enc']

            
        url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
        response=self.session.get(url=url,headers=self.headers,params=data)
        return response.content.decode()


def sign_xxt():
    config={
        "phone":"xxx",
        "password":"xxx",
        "longitude":"xxx",
        "latitude":"xxx",
        "address":"xxx"
    }
    mode2={"mode":"location"}
    student=chaoxing(config=config)
    print(student.signin(mode2))



