import json
import base64
import copy
import time
import hmac


class Jwt():

    def __init__(self):
        pass

    @staticmethod
    def b64encode(j_s):
        #替换b64生成出来的占位=
        return base64.urlsafe_b64encode(j_s).replace(b'=',b'')

    @staticmethod
    def b64decode(b64_s):
        rem = len(b64_s) % 4
        if rem:
            b64_s += b'=' * (4-rem)
        return base64.urlsafe_b64decode(b64_s)

    @staticmethod
    def encode(payload, key, exp=300):
        #init header
        header = {'typ':'JWT', 'alg':'HS256'}
        # 将header 转成json串
        header_json = json.dumps(header,sort_keys=True, separators=(',',':'))
        #b64 - json穿
        header_bs  = Jwt.b64encode(header_json.encode())

        #init payload {'username':'guoxiaonao'}
        payload = copy.deepcopy(payload)
        payload['exp'] = time.time() + exp
        payload_json = json.dumps(payload,sort_keys=True, separators=(',',':'))
        payload_bs = Jwt.b64encode(payload_json.encode())

        if isinstance(key, str):
            key = key.encode()
        #sign
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        hm_bs = Jwt.b64encode(hm.digest())

        return header_bs + b'.' + payload_bs + b'.' + hm_bs

    @staticmethod
    def decode(token, key):
        #对比两次HMAC结果  - raise
        #payload部分有exp的话，要校验exp - raise
        #最终返回 payload
        header_bs, payload_bs, sign = token.split(b'.')

        if isinstance(key, str):
            key = key.encode()
        #重新计算hmac的值
        hm = hmac.new(key, header_bs + b'.' + payload_bs, digestmod='SHA256')
        #比较两次hmac值
        if sign != Jwt.b64encode(hm.digest()):
            #hmac异常
            print('---sign error---')
            raise
        #获取payload内容
        payload_json = Jwt.b64decode(payload_bs)
        #注意 json.loads(b'')
        payload = json.loads(payload_json)

        #exp校验
        exp = payload['exp']
        now = time.time()
        if now > exp:
            #此token过期
            raise

        return payload


if __name__ == '__main__':

    d = {'username':'guoxiaonao'}
    res = Jwt.encode(d,'123456')
    #print(res)

    # import time
    # #time.sleep(3)
    d_res = Jwt.decode(res, '123456')
    print(d_res)





















