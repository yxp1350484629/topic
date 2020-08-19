from django.db import models
import random

# Create your models here.
# 表名　user_profile
# 库名　mywiki
def choice_sign():
    s = ['I am very happy!', 'I am so happy!']
    return random.choice(s)

class UserProfile(models.Model):

    username = models.CharField(max_length=11, verbose_name='用户名', primary_key=True)
    nickname =models.CharField(max_length=30,verbose_name='昵称')
    email = models.EmailField()
    password = models.CharField(max_length=32,verbose_name='密码')
    sign = models.CharField(max_length=50,default=choice_sign, verbose_name='个人签名')
    info = models.CharField(max_length=150, default='', verbose_name='个人描述')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    #image字段
    #upload_to 存储文件夹  settings.py MEDIA_ROOT + upload_to值
    avatar = models.ImageField(upload_to='avatar/', null=True)
    #登录时间
    login_time = models.DateTimeField(null=True)




    class Meta:
        db_table = 'user_profile'
        







    pass



