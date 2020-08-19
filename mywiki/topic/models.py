from django.db import models
from user.models import UserProfile

# Create your models here.
class Topic(models.Model):

    title = models.CharField(max_length=90, verbose_name='题目')
    category = models.CharField(max_length=20, verbose_name='文章的分类')
    limit = models.CharField(max_length=10, verbose_name='文章权限')
    introduce = models.CharField(max_length=90, verbose_name='文章简介')
    content = models.TextField(verbose_name='文章内容')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    #外键
    author = models.ForeignKey(UserProfile)


    # /obj
    # user = UserProfile.objects.get(username='guoxiaonao')
    # topic.objects.create(author= user)
    #
    # /id
    # topic.objects.create(author_id = 'guoxiaonao' )



    class Meta:
        db_table = 'topic'



























