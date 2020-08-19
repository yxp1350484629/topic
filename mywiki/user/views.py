import hashlib
import json
import time ,datetime

import jwt
from django.http import HttpResponse, JsonResponse
from .models import *

from btoken.views import make_token
from tools.logging_check import logging_check


# Create your views here.
@logging_check('PUT')
def users(request, username=None):
    #http://127.0.0.1:8000/v1/users GET
    if request.method == 'GET':
        #查询数据
        if username:
            #查询具体用户的数据
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                user = None

            if not user:
                result = {'code':10108, 'error': 'User is not existed !'}
                return JsonResponse(result)
            #判断是否有查询字符串
            if request.GET.keys():
                #有查询字符串
                data = {}
                # /?nickname=1&sign=1&ppp=1
                for k in request.GET.keys():
                    #判断查询字符串的key 是否在表里有该对应的字段
                    if k in ['password']:
                        continue

                    if hasattr(user, k):
                        data[k] = getattr(user, k)

                result = {'code':200, 'username':username, 'data':data}

                return JsonResponse(result)

            else:
                #无查询字符串
                result = {'code':200, 'username':username, 'data':{'nickname':user.nickname, 'email':user.email,'sign':user.sign, 'info': user.info,'avatar':str(user.avatar)}}
                return JsonResponse(result)
        else:
            print('---全量---')
            all_user = UserProfile.objects.all()
            all_data = []
            for u in all_user:
                d = {'nickname':u.nickname, 'email':u.email, 'sign': u.sign }
                all_data.append(d)
            return JsonResponse({'code':200, 'data':all_data})








    elif request.method == 'POST':
        #创建资源/ 注册用户
        # 注册用户成功后　签发 token[一天]
        #用户模块状态码　10100 开始　/ 200为正常返回
        #{'code': 200/101xx, 'data':xxx, 'error':xxx}
        #响应json字符串 return JsonResponse({})
        print(12123123123)
        json_str = request.body
        print(json_str)
        if not json_str:
            result = {'code':10100, 'error':'Please give me data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str.decode())

        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not username:
            result = {'code':10101, 'error':'Please give me username'}
            return JsonResponse(result)
        if not email:
            result = {'code':10102, 'error':'Please give me email'}
            return JsonResponse(result)

        if not password_1 or not password_2:
            result = {'code':10103, 'error':'Please give me password'}
            return JsonResponse(result)

        if password_1 != password_2:
            result = {'code': 10104, 'error':'The password is not same!'}
            return JsonResponse(result)
        #检查当前用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10105, 'error':'The username is already existed!'}
            return JsonResponse(result)
        #密码进行哈希　－　md5
        p_m = hashlib.md5()
        p_m.update(password_1.encode())

        #创建用户
        now = datetime.datetime.now()
        try:
            UserProfile.objects.create(username=username,password=p_m.hexdigest(),nickname=username, email=email, login_time=now)
        except Exception as e:
            print(e)
            result = {'code':10106, 'error':'The username is already used!'}
            return JsonResponse(result)

        #todo 生成token
        token = make_token(username, now)
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)

    elif request.method == 'PUT':
        #更新用户数据
        json_str  = request.body
        if not json_str:
            result = {'code': 10109, 'error': 'Please give me data'}
            return JsonResponse(result)

        json_obj = json.loads(json_str.decode())

        if 'sign' not in json_obj:
            result = {'code': 10110, 'error': 'Please give me sign !'}
            return JsonResponse(result)

        if 'info' not in json_obj:
            result = {'code':10111, 'error':'Please give me info'}
            return JsonResponse(result)

        if 'nickname' not in json_obj:
            result = {'code': 10112, 'error': 'Please give me nickname'}
            return JsonResponse(result)

        nickname = json_obj['nickname']
        sign = json_obj['sign']
        info = json_obj['info']

        #初级版
        # try:
        #     user = UserProfile.objects.get(username=username)
        # except Exception as e:
        #     result = {'code':10113, 'error':'no user'}
        #     return JsonResponse(result)

        #获取用户
        user = request.user

        #判断是否要更新
        to_update = False

        if user.nickname != nickname:
            to_update = True
        if user.sign != sign:
            to_update = True
        if user.info != info:
            to_update = True

        if to_update:
            print('----to updae----')
            user.nickname = nickname
            user.sign = sign
            user.info = info
            user.save()
        result = {'code':200, 'username':username}
        return JsonResponse(result)

    return HttpResponse('test user')

@logging_check('POST')
def users_avatar(request, username):
    #用户上传头像
    if request.method != 'POST':
        result = {'code':10114, 'error':'Please use POST'}
        return JsonResponse

    user = request.user

    #前端 username   后端 request.user.username
    if username != request.user.username:
        result = {'code': 10117, 'error': 'You guofen le!'}
        return JsonResponse(result)

    user_avatar = request.FILES['avatar']
    if not user_avatar:
        result = {'code':10116, 'error': 'No avatar'}
        return JsonResponse(result)
    user.avatar = user_avatar
    user.save()
    result = {'code':200, 'username':username}
    return JsonResponse(result)





@logging_check('PUT')
def users_password(request, username):

    #测试celery
    from .tasks import task_test
    task_test.delay()

    if request.method != 'PUT':
        result = {'code': 10118, 'error': 'Please use put'}
        return JsonResponse(result)

    if request.user.username != username:
        result = {'code': 10119, 'error': 'Username not match'}
        return JsonResponse(result)

    json_str = request.body
    if not json_str:
        result = {'code': 10120, 'error': 'no data'}
        return JsonResponse(result)

    json_obj = json.loads(json_str.decode())
    old_password = json_obj.get('old_password')
    password_1 = json_obj.get('password_1')
    password_2 = json_obj.get('password_2')
    #判断新旧密码的一致性
    if old_password == password_1:
        result = {'code': 10123 , 'error': 'The old password and new password is same'}
        return JsonResponse(result)

    #TDOD 校验三个密码是否都有值
    m = hashlib.md5()
    m.update(old_password.encode())
    if request.user.password != m.hexdigest():
        result = {'code': 10121, 'error': 'Password error!'}
        return JsonResponse(result)

    if password_1 != password_2:
        result = {'code': 10122, 'error': 'Passwords not same !'}
        return JsonResponse(result)

    #重新生成md5对象
    n_m = hashlib.md5()
    n_m.update(password_1.encode())
    request.user.password = n_m.hexdigest()
    request.user.save()
    result = {'code':200}
    return JsonResponse(result)


























































