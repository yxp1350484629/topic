import json

from django.http import JsonResponse
from django.shortcuts import render
from tools.logging_check import logging_check,get_user_by_request
from .models import *
from message.models import Message

# Create your views here.
@logging_check('POST', 'DELETE')
def topics(request, author_id):

    if request.method == 'POST':
        #TODO 校验request.user.username == author_id
        json_str = request.body
        if not json_str:
            result = {'code': 10300, 'error':'Please give me data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str.decode())
        title = json_obj.get('title', '')

        import html
        #防范xss注入
        title = html.escape(title)

        if not title:
            result = {'code': 10301, 'error':'Please give me title'}
            return JsonResponse(result)
        #带有html标签样式的博客内容
        content = json_obj.get('content')
        #纯文本的博客内容
        content_text = json_obj.get('content_text')
        if not content or not content_text:
            result = {'code': 10302, 'error':'Please give me content !'}
            return JsonResponse(result)
        #生成简介部分
        introduce = content_text[:30]
        limit = json_obj.get('limit')
        #校验limit
        if limit not in ('public', 'private'):
            result = {'code':10303, 'error': 'Your limit is not ok!'}
            return JsonResponse(result)
        category = json_obj.get('category')
        #校验category
        if category not in ('tec', 'no-tec'):
            result = {'code': 10304, 'error':'Your category is not ok!'}
            return JsonResponse(result)

        Topic.objects.create(title=title,category=category,limit=limit,introduce=introduce,content=content, author=request.user)

        result = {'code':200, 'username':request.user.username}
        return JsonResponse(result)


    elif request.method == 'GET':
        #取数据
        # v1/topcis/guoxiaonao GET  拿用户所有数据
        #1, 当前博客的主人【博主】 author
        #2, 当前访问博客的访客  visitor
        authors = UserProfile.objects.filter(username=author_id)
        #authors有返回，author必然是authors第一个元素，因为username在表中为主键【唯一】
        if not authors:
            result = {'code':10304, 'error':'no author'}
            return JsonResponse(result)
        #当前被访问博客的博主
        author = authors[0]

        #获取当前访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        #具体文章的id
        t_id = request.GET.get('t_id')
        if t_id:
            # v1/topics/guoxiaonao?t_id=1
            #查询用户具体博客内容
            t_id = int(t_id)
            #当前是否为 博主访问自己的博客， True->博主在访问自己， False -> 游客在访问当前博客
            is_self = False
            #检查文章id，确保其权限合理
            if visitor_username == author_id:
                is_self = True
                #博主访问自己的博客
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code': 10308, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                #非博主访问当前博客
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    print('topic error')
                    print(e)
                    result = {'code': 10309, 'error': 'No topic'}
                    return JsonResponse(result)

            res = make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            #查询用户 博客列表 [category|无category]
            # v1/topics/guoxiaonao
            #判断是否有category
            category = request.GET.get('category')

            if category in ('tec', 'no-tec'):
                #category 查询
                if visitor_username == author_id:
                    author_topics = Topic.objects.filter(author_id=author_id,category=category)

                else:
                    author_topics = Topic.objects.filter(author_id=author_id, category=category, limit='public')

            else:
                #直接返回全量的
                #比对 visitor 跟 author
                if visitor_username == author_id:
                    #博主访问自己的博客
                    author_topics = Topic.objects.filter(author_id=author_id)

                else:
                    #访客 不是当前被访问博客的博主
                    author_topics = Topic.objects.filter(author_id=author_id,limit='public')

            res = make_topics_res(author, author_topics)
            return JsonResponse(res)


    elif request.method == 'DELETE':
        #删除博客
        #?topic_id=1
        #删除一定要校验 token中的username和视图函数传进来的author_id
        # TOKEN guoxiaonao  -> DELETE v1/topics/guoxiaonao?topic_id=1
        if author_id != request.user.username:
            result = {'code': 10305 ,'error':'The author id is error'}
            return JsonResponse(result)

        topic_id = request.GET.get('topic_id')
        if not topic_id:
            result = {'code': 10306, 'error':'No topic id'}
            return JsonResponse(result)

        #查询指定文章
        topic_id = int(topic_id)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            result = {'code': 10307, 'error':'No topic'}
            return JsonResponse(result)

        topic.delete()

        return JsonResponse({'code':200})



def make_topics_res(author, author_topics):

    res = {'code':200, 'data':{}}
    topics_res = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['introduce'] = topic.introduce
        d['author'] = author.nickname
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        #TODO content?
        topics_res.append(d)

    res['data']['nickname'] = author.nickname
    res['data']['topics'] = topics_res
    #{'code':200, 'data':{'nickname':xxx,'topics':[{xxx},{xx}]}}
    return res


def make_topic_res(author, author_topic, is_self):
    if is_self:
        #博主访问自己
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        #游客访问当前博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author,limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author,limit='public').last()

    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None


    #拼message返回
    all_messages = Message.objects.filter(topic=author_topic)
    #存储所有的留言
    msg_list = []
    #存储 {'parent_message':[回复..回复..]}
    reply_dict = {}
    for msg in all_messages:
        if msg.parent_message:
            #回复
            #reply_dict.setdefault(msg.parent_message, [])
            if msg.parent_message not in reply_dict:
                reply_dict[msg.parent_message] = []
                reply_dict[msg.parent_message].append({'msg_id':msg.id, 'content':msg.content,'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatr),'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                reply_dict[msg.parent_message].append(
                    {'msg_id': msg.id, 'content': msg.content, 'publisher': msg.publisher.nickname,
                     'publisher_avatar': str(msg.publisher.avatr),
                     'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})

        else:
            #留言
            msg_list.append({'id':msg.id,'content':msg.content, 'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatar),'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),'reply':[]})

    #合并 msg_list[{'id':xxx},{}] 和 reply_dict{'parent_message':[孩子们]}
    for m in msg_list:
        if m['id'] in reply_dict:
            m['replay'] = reply_dict[m['id']]

    result = {'code':200, 'data':{}}
    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['introduce'] = author_topic.introduce
    result['data']['content'] = author_topic.content
    result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title
    result['data']['last_id'] = last_id
    result['data']['last_title'] = last_title
    result['data']['author'] = author.nickname

    result['data']['messages'] = msg_list
    #TODO message count
    result['data']['messages_count'] = 0
    return result


def gettopic(entityName, fileName):
    try:
        #create paths and txt files
        print(u'topic名称: ', fileName)
        info = codecs.open(fileName, 'w', 'utf-8')

         #locate input  notice: 1.visit url by unicode 2.write files
         #Error: Message: Element not found in the cache -
         #       Perhaps the page has changed since it was looked up
         #解决方法: 使用Selenium和Phantomjs
        print(u'实体名称: ', entityName.rstrip('\n'))
        driver.get("http://baike.baidu.com/")
        elem_inp = driver.find_element_by_xpath("//form[@id='searchForm']/input")
        elem_inp.send_keys(entityName)
        elem_inp.send_keys(Keys.RETURN)
        info.write(entityName.rstrip('\n')+'\r\n')  #codecs不支持'\n'换行

        #load content 摘要
        elem_value = driver.find_elements_by_xpath("//div[@class='lemma-summary']/div")
        for value in elem_value:
             print(value.text)
             info.writelines(value.text + '\r\n')

         #爬取文本信息
        #爬取所有段落<div class='para'>的内容 class='para-title'为标题 [省略]
        time.sleep(2)

    except Exception as e:
        #'utf8' codec can't decode byte
        print("Error: ",e)
    finally:
        print('\n')
        info.close()




























