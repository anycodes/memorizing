from english.models import *
import xml.sax.handler
import urllib.request
import urllib.error
import json
from memorizing.settings import *
import random
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import xml.sax.handler
import urllib.request
import urllib.error
from lxml import etree
from django.core.paginator import *
from django.http import HttpResponse
import hashlib
from django.utils.encoding import smart_str
import urllib.request
import ssl
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

# Create your views here.

# 定义全局变量
def global_setting(request):
    return {'SITE_NAME': SITE_NAME,
            'SITE_DESC': SITE_DESC,
            'SITE_KEYWORD': SITE_KEYWORD, }


# 分析xml
class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        self.mapping[name] = self.buffer

    def getDict(self):
        return self.mapping


# 获取微信token
def getToken():
    context = ssl._create_unverified_context()
    appid = WECHAT_APPID
    appsecret = WECHAT_APPSECRET
    get_access_token = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    get_access_token_data = urllib.request.urlopen(get_access_token, context=context).read().decode("utf-8")
    print("*" * 30)
    print(get_access_token_data)
    access_token = json.loads(get_access_token_data)["access_token"]
    return access_token

# 获得语音
def get_voice(med_id):
    url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=" + getToken() + "&media_id=" + med_id
    context = ssl._create_unverified_context()
    get_res = urllib.request.urlopen(url, context=context)
    return get_res.read()

# 图文信息发送
def tuwenMsg(fromuser, touser, title, desc, url):
    request_xml = """
    <xml>
    <ToUserName><![CDATA[""" + fromuser + """]]></ToUserName>
    <FromUserName><![CDATA[""" + touser + """]]></FromUserName>
    <CreateTime>12345678</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>1</ArticleCount>
    <Articles>
    <item>
    <Title><![CDATA[""" + title + """]]></Title> 
    <Description><![CDATA[""" + desc + """]]></Description>
    <Url><![CDATA[""" + url + """]]></Url>
    </item>
    </Articles>
    </xml>
            """
    return request_xml


# 文本信息发送
def wenbenMsg(fromuser, touser, text):
    request_xml = """
    <xml>
    <ToUserName><![CDATA[""" + fromuser + """]]></ToUserName>
    <FromUserName><![CDATA[""" + touser + """]]></FromUserName>
    <CreateTime>12345678</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[""" + text + """]]></Content>
    </xml>
    """
    return request_xml

# 地图定位
def get_jieJing(x, y):
    url = 'http://apis.map.qq.com/ws/streetview/v1/getpano?location=' + x + ',' + y + '&radius=100&key=QU3BZ-DLORW-RTNR7-OJGVX-OAHQJ-6DFVR'
    url_open = urllib.request.urlopen(url)
    data = json.loads(url_open.read().decode("utf-8"))
    return data["detail"]["id"]

# 判断用户是否在数据库内绑定了账号
def userin(uname):
    try:
        eve = User.objects.get(userid=uname)
        return True
    except Exception as e:
        return False


# 判断用户是否在数据库内绑定了账号
def wechat_in(uname):
    try:
        eve = User.objects.get(wechat=uname)
        return False
    except Exception as e:
        return True

# 总页面
@csrf_exempt
def getChat(request):
    with open("count") as f:
        count = f.readline()
    count_data = int(count.replace("\n", ""))
    count_data = count_data + 1
    with open("count", "w") as f:
        f.write(str(count_data))
    if request.method == "GET":
        signature = request.GET.get("signature", None)
        timestamp = request.GET.get("timestamp", None)
        nonce = request.GET.get("nonce", None)
        echostr = request.GET.get("echostr", None)
        token = "shuaibi"
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "%s%s%s" % tuple(tmp_list)
        tmp_str = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()
        if tmp_str == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin  index")
    else:
        xml_str = smart_str(request.body)
        request_xml = etree.fromstring(xml_str)
        url_body = request.body.decode("utf-8")
        print(url_body)
        xh = XMLHandler()
        xml.sax.parseString(url_body, xh)
        ret = xh.getDict()
        # 点击事件
        if ret['MsgType'] == "event":
            if ret['Event'] == "CLICK":
                if ret["EventKey"] == "lsjl":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "历史记录"
                        desc = "查看你单词背诵记录"
                        url = "http://beidanci.jlqlkj.cn/history?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "cczx":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "错词中心"
                        desc = "单词错了，就应该多看看"
                        url = "http://beidanci.jlqlkj.cn/wrong?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "smsb":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "扫码识别"
                        desc = "这是您的成绩单"
                        url = "http://ouryust.jlqlkj.cn/grades?userid=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "dcxx":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "单词学习"
                        desc = "先学习单词，好好学习有帮助"
                        url = "http://beidanci.jlqlkj.cn/catlist_one?cattype=all&wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "ksbs":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "开始背诵"
                        desc = "背诵单词，要用心欧！"
                        url = "http://beidanci.jlqlkj.cn/catlist_two?cattype=all&wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "yjfk":
                    title = "信息反馈"
                    desc = "有话想对我们说？"
                    url = "http://beidanci.jlqlkj.cn/fankui?wechat=" + ret["FromUserName"]
                    request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "zhzc":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "您已注册"
                        desc = "无需重复注册！"
                        url = ""
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                elif ret["EventKey"] == "xxxg":
                    wechat = ret['FromUserName']
                    if wechat_in(wechat):
                        title = "注册账号"
                        desc = "只有注册，才能有背心背单词的快感"
                        url = "http://beidanci.jlqlkj.cn/writeinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
                    else:
                        title = "信息修改"
                        desc = "在这里您可以修改您的注册信息"
                        url = "http://beidanci.jlqlkj.cn/userinfo?wechat=" + ret["FromUserName"]
                        request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
            elif ret['Event'] == "subscribe":
                string_info = '''感谢您关注单词易背微信平台，您可以通过本平台使用以下功能：
1）翻译：发送语音（汉语），或者给平台发送文字，可以快速为您翻译，语音目前只支持汉语->英语，文字支持英汉互译，其他语言自动翻译成英文。
2）背单词：通过完善账号，可以快速背诵单词，我们会在后期增加更多背单词模式和词库，同时也希望大家给我们提意见'''
                title = "感谢您的关注"
                desc = string_info
                url = "http://beidanci.jlqlkj.cn"
                request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
        # 文本信息
        elif ret['MsgType'] == "text":
            if ret["Content"]:
                text = translation(ret["Content"])
                request_xml = wenbenMsg(ret['FromUserName'], ret['ToUserName'], text)
        # 语音信息
        elif ret['MsgType'] == "voice":
            if ret["Recognition"]:
                text = translation(ret["Recognition"])
                request_xml = wenbenMsg(ret['FromUserName'], ret['ToUserName'], text)
        # 图像信息
        elif ret['MsgType'] == "image":
            picurl = ret["PicUrl"]
            title = "相似图片"
            desc = "这里我找到的和你发的类似图片【打开速度可能有点慢】"
            url = "http://ouryust.jlqlkj.cn/picpage?picurl=" + picurl
            request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
        # 位置信息
        elif ret['MsgType'] == "location":
            zoubiao_x = ret['Location_X']
            zuobiao_y = ret['Location_Y']
            title = "街景地图"
            desc = "用手机看看你周边的世界"
            url = "https://jiejing.qq.com/#pano=" + get_jieJing(zoubiao_x,
                                                                zuobiao_y) + "&heading=330&pitch=0&poi=detail&addr=1&minimap=0&region=0&search=0&direction=1&ref=wx&isappinstalled=-1"
            request_xml = tuwenMsg(ret['FromUserName'], ret['ToUserName'], title, desc, url)
        # 其他信息
        else:
            request_xml = wenbenMsg(ret['FromUserName'], ret['ToUserName'], "请您给我发语音或者文字信息")
        return HttpResponse(request_xml)
    return render(request, "get_from_wechat.html")

# 图片反馈功能
def picSB(picurl):
    data = {
        'imageURL': picurl
    }
    img_data = urllib.parse.urlencode(data).encode("utf-8")
    imge_source = urllib.request.urlopen('http://api1.wozhitu.com/%20index/apiImageSearch', img_data)
    content = imge_source.read().decode("utf-8")
    xpath_data = etree.HTML(content)
    eveUrl = xpath_data.xpath('////*[@id="imgs-div"]/div/div[1]/img/@src')
    return eveUrl


# 图片反馈页面
def picpage(request):
    picurl = request.GET.get("picurl")
    ans = picSB(picurl)
    return render(request, "picpage.html", locals())



# 自定义菜单
def zidingyicaidan():
    url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + getToken()
    caidan = '''{
        "button": [
            {
                "name": "背单词",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "历史记录",
                        "key": "lsjl"
                    },
                    {
                        "type": "click",
                        "name": "错词中心",
                        "key": "cczx"
                    },
                    {
                        "type": "click",
                        "name": "单词学习",
                        "key": "dcxx"
                    },
                    {
                        "type": "click",
                        "name": "开始背诵",
                        "key": "ksbs"
                    }
                ]
            },
            {
                "name": "微中心",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "关于我们",
                        "url": "http://beidanci.jlqlkj.cn/about"
                    },
                    {
                        "type": "click",
                        "name": "意见反馈",
                        "key": "yjfk"
                    },
                    {
                        "type": "click",
                        "name": "账号注册",
                        "key": "zhzc"
                    },
                    {
                        "type": "click",
                        "name": "信息修改",
                        "key": "xxxg"
                    },
                ]
            }
        ],
    }'''
    context = ssl._create_unverified_context()
    re_data = urllib.request.urlopen(url, caidan.encode('utf-8')).read().decode("utf-8")
    return re_data

# 更新菜单
def gengxincaidan(request):
    redata = zidingyicaidan()
    return render(request, "gengxincaidan.html", locals())


# 用户注册完善信息
def writeinfo(request):
    wechat = request.GET.get("wechat")
    return render(request, "writeinfo.html", locals())


# 用户注册与更改信息完善结果
def writeresult(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        username = request.GET.get("username")
        password = request.GET.get("password")
        sex = request.GET.get("sex")
        school = request.GET.get("school")
        grade = request.GET.get("grade")
        qq = request.GET.get("qq")
        email = request.GET.get("email")
        print(request.GET.get("change"))
        if request.GET.get("change"):
            try:
                user = User.objects.get(wechat=wechat)
                user.username = username
                user.password = password
                user.sex = sex
                user.school = school
                user.grade = grade
                user.qq = qq
                user.email = email
                user.save()
                result = "Succeed"
            except:
                # 11003用户更新信息时，数据库升级错误
                result = "Error Code : 11003"
        else:
            try:
                try:
                    User.objects.get(wechat=wechat)
                    result = "This wechat had already registe!"
                except Exception as e:
                    User.objects.create(wechat=wechat, username=username, password=password, sex=sex, school=school,
                                        grade=grade, qq=qq, email=email)
                    result = "Succeed"
            except:
                # 11001用户注册信息时，数据库新增错误
                result = "Error Code : 11001"
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
    return render(request, "result.html", locals())


# 用户查看和修改信息
def infoview(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        try:
            user = User.objects.get(wechat=wechat)
        except:
            # 11002用户查看信息时，微信不再数据库内
            result = "Error Code : 11002"
            return render(request, "result.html", locals())
    else:
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "userinfo.html", locals())


# 总分类列表
@csrf_exempt
def catlist_one(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        cattype = request.GET.get("cattype")
        try:
            wordcat = Catagory.objects.all()
            fenlei = []
            fenlei1 = []
            for eveFenlei1 in wordcat:
                fenlei.append(eveFenlei1.first)
            for evefenlei in fenlei:
                if evefenlei not in fenlei1:
                    fenlei1.append(evefenlei)
            if cattype == "all":
                wordcatinfor = wordcat
            else:
                wordcatinfor = Catagory.objects.filter(first=cattype)
            paginator = Paginator(wordcatinfor, 12)
            try:
                page = int(request.GET.get('page', 1))
                wordcatinfor = paginator.page(page)
            except Exception as ex:
                pass
        except Exception as e:
            print(e)
            # 12001查询分类总列表出错
            result = "Error Code : 12001"
            return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "catlist.html", locals())

# 总分类列表
@csrf_exempt
def catlist_two(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        cattype = request.GET.get("cattype")
        try:
            wordcat = Catagory.objects.all()
            fenlei = []
            fenlei1 = []
            for eveFenlei1 in wordcat:
                fenlei.append(eveFenlei1.first)
            for evefenlei in fenlei:
                if evefenlei not in fenlei1:
                    fenlei1.append(evefenlei)
            if cattype == "all":
                wordcatinfor = wordcat
            else:
                wordcatinfor = Catagory.objects.filter(first=cattype)
            paginator = Paginator(wordcatinfor, 12)
            try:
                page = int(request.GET.get('page', 1))
                wordcatinfor = paginator.page(page)
            except Exception as ex:
                pass
        except Exception as e:
            print(e)
            # 12001查询分类总列表出错
            result = "Error Code : 12001"
            return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "catlist2.html", locals())


# #递进分类列表
# def djcatlist(request):
#     if request.GET.get("wechat"):
#         wechat = request.GET.get("wechat")
#         if request.GET.get("filter"):
#             filter = request.GET.get("filter")
#             try:
#                 wordcatinfor = Catagory.objects.filter()
#             except:
#                 # 12002查询分类递进列表出错
#                 result = "Error Code : 12002"
#                 return render(request, "result.html", locals())
#         else:
#             result = "Error Code : 12002"
#             return render(request, "result.html", locals())
#     else:
#         # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
#         result = "Error Code : 10000"
#         return render(request, "result.html", locals())
#     return render(request,"djcatlist.html",locals())


# 单词列表
@csrf_exempt
def wordlist(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        if request.GET.get("cat"):
            cat = request.GET.get("cat")
            try:
                catname = Catagory.objects.get(catid=cat)
                try:
                    wordcatinfor = Word.objects.filter(catagory=catname)
                    paginator = Paginator(wordcatinfor, 20)
                    try:
                        page = int(request.GET.get('page', 1))
                        wordcatinfor = paginator.page(page)
                    except Exception as ex:
                        pass
                except:
                    # 13002单词列表查询失败
                    result = "Error Code : 13002"
                    return render(request, "result.html", locals())
            except:
                # 单词列表分类传参错误
                result = "Error Code : 13001"
                return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "looklist.html", locals())


# 背单词模式选择
@csrf_exempt
def memoword_list(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        cat = request.GET.get("cat")
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "beisong.html", locals())

# 背单词跳转
@csrf_exempt
def memoword_tz(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        cat = request.GET.get("cat")
        words = Word.objects.filter(catagory=cat)
        length = len(words)
        func = request.GET.get("func")
        with open('mingyan') as file:
            mingyan_list = file.readlines()
        mingyan = random.choice(mingyan_list).replace("\n", "")
        if func == "mo1":
            tiaozhuan = 'modle_1_question'
        elif func == 'mo2':
            tiaozhuan = 'modle_2_question'
        elif func == 'mo3':
            tiaozhuan = 'modle_3_question'
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "beisongtiaozhhuan.html", locals())


# 背单词模式1-看解释写单词
@csrf_exempt
def memoword_mo_one(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        if request.GET.get("cat"):
            cat = request.GET.get("cat")
            try:
                catname = Catagory.objects.get(catid=cat)
                try:
                    wordslist = Word.objects.filter(catagory=catname)
                    length = len(wordslist)
                    try:
                        counttemp = int(request.GET.get("count"))
                        if counttemp <= length and counttemp>0:
                            count = counttemp
                        else:
                            count = length
                    except:
                        count = length
                    wordcatinfor = random.sample(list(wordslist), count)
                    answer_word = []
                    for eveWord in wordcatinfor:
                        hou_string = eveWord.word[1:]
                        tihuan_string = '_ '
                        for eve in hou_string[1:]:
                            tihuan_string = tihuan_string + '_ '
                        eveWord.word = eveWord.word[0:1] + tihuan_string
                        answer_word.append(eveWord.wordid)
                except Exception as e:
                    # 13002单词列表查询失败
                    print(e)
                    result = "Error Code : 13002"
                    return render(request, "result.html", locals())
            except:
                # 单词列表分类传参错误
                result = "Error Code : 13001"
                return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "wordlist.html", locals())


# 背单词模式1-答题结果
@csrf_exempt
def word_result_one(request):
    if request.POST.get("wechat"):
        cat = request.POST.get("cat")
        wechat = request.POST.get("wechat")
        answer = request.POST.getlist("answer", [])
        wordids = request.POST.get("wordids").replace("[", "").replace("]", "").split(",")
        user = User.objects.get(wechat=wechat)
        catagory = Catagory.objects.get(catid=cat)
        main_ans = []
        answer_word = []
        for eve_answer_wordid in wordids:
            try:
                ans_word = Word.objects.get(wordid=eve_answer_wordid)
                answer_word.append(ans_word)
            except:
                # 14001 用户在查询答案是数据出错
                result = "Error Code : 14001"
                return render(request, "result.html", locals())
        num = 0
        right_num = 0
        wrong_num = 0
        for eve_answer_word in answer_word:
            answer_content = eve_answer_word.word[1:]
            if answer[num] == answer_content:
                ans_result = True
                right_num = right_num + 1
            else:
                ans_result = False
                wrong_num = wrong_num + 1
                try:
                    neirong = Wrong.objects.filter(word=eve_answer_word)
                    time = 1
                    for eve in neirong:
                        if neirong.user == user:
                            time = time + 1
                    Wrong.objects.create(user=user, word=eve_answer_word, times=time)
                except Exception as e:
                    print(e)
            ans_dict = {"wordid": wordids[num], "word_source": eve_answer_word.word,
                        "word_user": eve_answer_word.word[0:1] + answer[num], "mean_en": eve_answer_word.mean_en,
                        "mean_zh": eve_answer_word.mean_zh, "state": ans_result}
            main_ans.append(ans_dict)
            num = num + 1
        grade = [right_num, wrong_num, num]
        try:
            History.objects.create(user=user, catagory=catagory, grade=grade)
        except Exception as e:
            print(e)
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "datiresult.html", locals())


# 背单词模式2-连线
@csrf_exempt
def memoword_mo_two(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        if request.GET.get("cat"):
            cat = request.GET.get("cat")
            try:
                catname = Catagory.objects.get(catid=cat)
                wordslist = Word.objects.filter(catagory=catname)
                length = len(wordslist)
                try:
                    counttemp = int(request.GET.get("count"))
                    if counttemp <= length and counttemp > 0:
                        count = counttemp
                    else:
                        count = length
                except:
                    count = length
                try:
                    wordcatinfor = random.sample(list(Word.objects.filter(catagory=catname)), count)
                    main_word_list = []
                    main_mean = []
                    answer_word = []
                    final_mean = {}
                    num = 0
                    for eveMean in wordcatinfor:
                        temp_eveMean = eveMean.mean_en
                        main_mean.append(temp_eveMean)
                    random.shuffle(main_mean)
                    for eveWord in wordcatinfor:
                        answer_word.append(eveWord.wordid)
                        word_content = eveWord.word
                        mean_content = main_mean[num]
                        wordid_content = eveWord.wordid
                        num = num + 1
                        final_mean[num] = main_mean[num - 1]
                        main_word_list.append(
                            {"wordid": wordid_content, "num": num, "word": word_content, "mean": mean_content})
                except Exception as e:
                    # 13002单词列表查询失败
                    print(e)
                    result = "Error Code : 13002"
                    return render(request, "result.html", locals())
            except:
                # 单词列表分类传参错误
                result = "Error Code : 13001"
                return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "wordlist2.html", locals())


# 背单词模式2-答题结果
@csrf_exempt
def word_result_two(request):
    if request.POST.get("wechat"):
        cat = request.POST.get("cat")
        wechat = request.POST.get("wechat")
        yuanen = request.POST.get("yuanen")
        answer = request.POST.getlist("answer", [])
        wordids = request.POST.get("wordids").replace("[", "").replace("]", "").split(",")
        user = User.objects.get(wechat=wechat)
        catagory = Catagory.objects.get(catid=cat)
        zhuanhua_data = eval(yuanen)
        main_ans = []
        answer_word = []
        for eve_answer_wordid in wordids:
            try:
                ans_word = Word.objects.get(wordid=eve_answer_wordid)
                answer_word.append(ans_word)
            except:
                # 14001 用户在查询答案是数据出错
                result = "Error Code : 14001"
                return render(request, "result.html", locals())
        num = 0
        right_num = 0
        wrong_num = 0
        for eve_answer_word in answer_word:
            answer_content = eve_answer_word.mean_en
            try:
                if zhuanhua_data[int(answer[num])] == answer_content:
                    ans_result = True
                    right_num = right_num + 1
                else:
                    ans_result = False
                    wrong_num = wrong_num + 1
                    try:
                        neirong = Wrong.objects.filter(word=eve_answer_word)
                        time = 1
                        for eve in neirong:
                            if neirong.user == user:
                                time = time + 1
                        Wrong.objects.create(user=user, word=eve_answer_word, times=time)
                    except Exception as e:
                        print(e)
                ans_dict = {"wordid": wordids[num], "word_source": eve_answer_word.word,
                            "word_user": zhuanhua_data[int(answer[num])], "mean_en": eve_answer_word.mean_en,
                            "mean_zh": eve_answer_word.mean_zh, "state": ans_result}
                main_ans.append(ans_dict)
                num = num + 1
            except:
                pass
        grade = [right_num, wrong_num, num]
        try:
            History.objects.create(user=user, catagory=catagory, grade=grade)
        except Exception as e:
            print(e)
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "datiresult2.html", locals())


# 背单词模式3-根据汉语写单词
@csrf_exempt
def memoword_mo_three(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        if request.GET.get("cat"):
            cat = request.GET.get("cat")
            try:
                catname = Catagory.objects.get(catid=cat)
                try:
                    wordslist = Word.objects.filter(catagory=catname)
                    length = len(wordslist)
                    try:
                        counttemp = int(request.GET.get("count"))
                        if counttemp <= length and counttemp>0:
                            count = counttemp
                        else:
                            count = length
                    except:
                        count = length
                    wordcatinfor = random.sample(list(wordslist), count)
                    answer_word = []
                    for eveWord in wordcatinfor:
                        hou_string = eveWord.word[1:]
                        tihuan_string = '_ '
                        for eve in hou_string[1:]:
                            tihuan_string = tihuan_string + '_ '
                        eveWord.word = eveWord.word[0:1] + tihuan_string
                        answer_word.append(eveWord.wordid)
                except Exception as e:
                    # 13002单词列表查询失败
                    print(e)
                    result = "Error Code : 13002"
                    return render(request, "result.html", locals())
            except:
                # 单词列表分类传参错误
                result = "Error Code : 13001"
                return render(request, "result.html", locals())
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "wordlist3.html", locals())


# 背单词模式3-答题结果
@csrf_exempt
def word_result_three(request):
    if request.POST.get("wechat"):
        cat = request.POST.get("cat")
        wechat = request.POST.get("wechat")
        answer = request.POST.getlist("answer", [])
        wordids = request.POST.get("wordids").replace("[", "").replace("]", "").split(",")
        user = User.objects.get(wechat=wechat)
        catagory = Catagory.objects.get(catid=cat)
        main_ans = []
        answer_word = []
        for eve_answer_wordid in wordids:
            try:
                ans_word = Word.objects.get(wordid=eve_answer_wordid)
                answer_word.append(ans_word)
            except:
                # 14001 用户在查询答案是数据出错
                result = "Error Code : 14001"
                return render(request, "result.html", locals())
        num = 0
        right_num = 0
        wrong_num = 0
        for eve_answer_word in answer_word:
            answer_content = eve_answer_word.word[1:]
            if answer[num] == answer_content:
                ans_result = True
                right_num = right_num + 1
            else:
                ans_result = False
                wrong_num = wrong_num + 1
                try:
                    neirong = Wrong.objects.filter(word=eve_answer_word)
                    time = 1
                    for eve in neirong:
                        if neirong.user == user:
                            time = time + 1
                    Wrong.objects.create(user=user, word=eve_answer_word, times=time)
                except Exception as e:
                    print(e)
            ans_dict = {"wordid": wordids[num], "word_source": eve_answer_word.word,
                        "word_user": eve_answer_word.word[0:1] + answer[num], "mean_en": eve_answer_word.mean_en,
                        "mean_zh": eve_answer_word.mean_zh, "state": ans_result}
            main_ans.append(ans_dict)
            num = num + 1
        grade = [right_num, wrong_num, num]
        try:
            History.objects.create(user=user, catagory=catagory, grade=grade)
        except Exception as e:
            print(e)
    else:
        # 10000 用户提交资料如果不再微信中提交注册，提示失败，不写入数据库
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "datiresult3.html", locals())


# 查看历史成绩和记录
def history(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        try:
            user = User.objects.get(wechat=wechat)
            words = History.objects.filter(user=user)
            paginator = Paginator(words, 20)
            try:
                page = int(request.GET.get('page', 1))
                words = paginator.page(page)
            except Exception as ex:
                pass
        except:
            # 11002用户查看信息时，微信不再数据库内
            result = "Error Code : 11002"
            return render(request, "result.html", locals())
    else:
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "history.html", locals())

# 查看错误记录
def wrong(request):
    if request.GET.get("wechat"):
        wechat = request.GET.get("wechat")
        try:
            user = User.objects.get(wechat=wechat)
            words = Wrong.objects.filter(user=user)
            paginator = Paginator(words, 20)
            try:
                page = int(request.GET.get('page', 1))
                words = paginator.page(page)
            except Exception as ex:
                pass
        except:
            # 11002用户查看信息时，微信不再数据库内
            result = "Error Code : 11002"
            return render(request, "result.html", locals())
    else:
        result = "Error Code : 10000"
        return render(request, "result.html", locals())
    return render(request, "wrong.html", locals())

# 关我我们页面
def aboutus(request):
    with open("count") as f:
        count = f.readline()
    count_data = int(count.replace("\n", ""))
    count_data = count_data + 1
    with open("count", "w") as f:
        f.write(str(count_data))
    return render(request, "aboutus.html", locals())

# 首页信息
def index(request):
    with open("count") as f:
        count = f.readline()
    count_data = int(count.replace("\n", ""))
    count_data = count_data + 1
    with open("count", "w") as f:
        f.write(str(count_data))
    return render(request, "index.html", locals())

# 帮助信息
def help(request):
    with open("count") as f:
        count = f.readline()
    count_data = int(count.replace("\n", ""))
    count_data = count_data + 1
    with open("count", "w") as f:
        f.write(str(count_data))
    return render(request, "help.html", locals())

#阿里云翻译
def translation(input_data):
    url = "http://fanyi.baidu.com/v2transapi"
    from_type = yuyan(input_data)
    if from_type == "en":
        to_tyoe = "zh"
    else:
        to_tyoe = "en"
    data = {}
    data['from'] = from_type
    data['query'] = input_data
    data['to'] = to_tyoe
    data['transtype'] = 'realtime'
    post_data = urllib.parse.urlencode(data).encode("gbk")
    post_request = urllib.request.Request(url,post_data)
    post_open = urllib.request.urlopen(post_request)
    post_read = json.loads(post_open.read().decode("utf-8"))["trans_result"]['data'][0]['result'][0][1]
    return post_read

#翻译功能-语言种类识别
def yuyan(input_data):
    host = 'https://dm-12.data.aliyun.com'
    path = '/rest/160601/mt/detect.json'
    method = 'POST'
    appcode = 'fdd704ee687c4ef095e7c4730592b240'
    querys = ''
    bodys = {}
    url = host + path

    bodys['q'] = input_data
    post_data = urllib.parse.urlencode(bodys).encode("utf-8")
    request = urllib.request.Request(url, post_data)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read().decode("utf-8")
    if (content):
        return json.loads(content)["data"]["language"]

# 邮件反馈
def fankui(request):
    wechat = request.GET.get("wechat")
    try:
        user = User.objects.get(wechat=wechat)
    except:
        user = {"username": "", "qq": "", "email": ""}
    return render(request, "fankui.html", locals())


# 邮件反馈结果
def fankui_resu(request):
    sender = 'service@52exe.cn'
    if request.GET.get("username"):
        name = request.GET.get("username")
        email = request.GET.get("email")
        qq = request.GET.get("qq")
        wechat = request.GET.get("wechat")
        message = request.GET.get("message")
        if not email:
            email = ''
        if not qq:
            qq = ''
        if not wechat:
            wechat = ''
        if not message:
            message = ''
        write_data = '姓名:' + name + '  邮箱:' + email + '  QQ:' + qq + '  微信:' + wechat + '  备注:' + message
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = Header("反馈成功", 'utf-8')
        msgRoot['To'] = Header(name, 'utf-8')
        subject = name + '反馈成功'
        msgRoot['Subject'] = Header(subject, 'utf-8')
        msgme = "尊敬的" + name + ": 您的信息已经提交到微信背单词官方！感谢您的支持！"
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgAlternative.attach(MIMEText(msgme, 'html', 'utf-8'))
        try:
            server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465);
            server.login(sender, "LIUYU714515")  # 登录服务器
            server.sendmail(sender, email, msgRoot.as_string())
            server.close()
            statu = "您的信息已经提交到微信背单词官方！"
        except smtplib.SMTPException:
            statu = "很抱歉，系统故障，请稍后重试！"
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = Header("反馈提醒", 'utf-8')
        msgRoot['To'] = Header(name, 'utf-8')
        subject = '有新的反馈信息'
        msgRoot['Subject'] = Header(subject, 'utf-8')
        msgad = write_data
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgAlternative.attach(MIMEText(msgad, 'html', 'utf-8'))
        try:
            server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465);
            server.login(sender, "LIUYU714515")  # 登录服务器
            server.sendmail("service@52exe.cn", "service@52exe.cn", msgRoot.as_string())
            server.close()
            statu = "您的信息已经提交到微信背单词官方！"
        except smtplib.SMTPException:
            statu = "很抱歉，系统故障，请稍后重试！"
    return render(request, "fankui_sult.html", locals())

@csrf_exempt
def piliang(request):
    if request.GET.get("canshu"):
        canshu = request.GET.get("canshu")
        if canshu == "shuaibi":
            try:
                first = request.POST.get("first")
                second = request.POST.get("second")
                third = request.POST.get("third")
                forth = request.POST.get("forth")
                shujv = request.POST.get("shujv")
                print(first)
                if first and shujv:
                    if not forth:
                        forth = ""
                        name = first + '_' + second + '_' + third
                    if not third:
                        third = ""
                        name = first + '_' + second
                    if not second:
                        second = ""
                        name = first
                    print(name)
                    try:
                        catagory = Catagory.objects.get(name=name)
                    except Exception as e:
                        try:
                            Catagory.objects.create(first=first, second=second, third=third, forth=forth, name=name)
                            catagory = Catagory.objects.get(name=name)
                        except Exception as e:
                            print(e)
                    shujv1 = shujv.split("\r\n")
                    for eve in shujv1:
                        shujv2 = eve.split("----")
                        print(shujv2)
                        try:
                            length = len(Word.objects.all())+1
                            # print(shujv2[0])
                            # print(shujv2[1])
                            # print(shujv2[2])
                            # print(catagory)

                            word_save = Word.objects.create(wordid=length,word=shujv2[0],mean_en=shujv2[1],mean_zh=shujv2[2])
                            catagory_list = Catagory.objects.filter(name=name)
                            word_save.catagory.add(*catagory_list)
                            # print(shujv1[0])
                        except Exception as e:
                            print(e)
                else:
                    pass
            except:
                pass
    return render(request,"piliang.html",locals())
