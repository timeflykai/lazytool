from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64

class AESEnCrpTor:
    # base64.b64encode("密钥".encode("utf-8")).decode()
    """https: // tool.chacuo.net / cryptaes"""

    def __init__(self,AES_IV,AES_KEY,):
        self.IV = AES_IV.encode("utf-8")
        self.KEY = AES_KEY.encode("utf-8")

    # def pkcs7_padding(self, data, block_size=128):
    #     """
    #     密码必须满足8的倍数所以需要补位，PKCS7Padding用'\n'补位
    #     :param data:
    #     :param block_size:
    #     :return:
    #     """
    #     if not isinstance(data, bytes):
    #         data = data.encode('utf-8')
    #     padder = padding.PKCS7(block_size).padder()
    #     return padder.update(data) + padder.finalize()
    
    def aes_encrypt(self, text: str):
        """
        aes加密
        :param password:
        :return:
        """
        #key = self.generateKey()
        padded_data = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
        cipher = AES.new(self.KEY, AES.MODE_CBC, self.IV)
        return base64.b64encode(cipher.encrypt(padded_data)).decode()

    def aes_decrypt(self, content: str):
        """
        aes解密
        :param content:
        :return:
        """
        #key = self.generateKey()
        cipher = AES.new(self.KEY, AES.MODE_CBC, self.IV)
        content = base64.b64decode(content)
        return (cipher.decrypt(content).decode('utf-8')).replace('\n', '')

