#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月11日

@author: qiu.zhong@downjoy.com

# crontab 设置定时执行
30 1 * * * /usr/local/bin/pyscript/comment/dailyStatCommentRank.py >> /home/downjoy/logs/py_dailyStatCommentRank.log &

每日集赞榜
  1.每天24时更新；
  2.显示当天50条集赞最多的评论内容，玩家信息，对应游戏

每日互动榜
  1.每天24时更新；
  2.显示当天50条被回复最多的评论内容，玩家信息，对应游戏
  
每周上榜达人
1.每天周更新：
2.上榜次最多，以及每周评论集赞数和被回复数
3.上榜次权重>集赞权重>互动榜权重
注：上过集赞和集贴两个榜单

#     for out in db.resourceComment.find({"subComments":{"$exists":True}}):
#         subComments = out["subComments"]
#         if(subComments!=None):
#             l = len(subComments)
#             if(l>0):
#                 db.resourceComment.update({"_id":out["_id"]}, {"$set":{"replyId":subComments[l-1]["_id"]}})

# "goodRat":1, "subCnt":1, "resourceKey":1, "content":1, "subComments":1, "name":1, "avatarUrl":1, "user":1

SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
System.out.println(Integer.parseInt(sdf.format(new Date())));

'''
import pymongo
import httplib,urllib
import datetime
import time
from bson.code import Code
from bson import ObjectId
import json
import traceback
import StringIO
from djutil.MailUtil import MailUtil
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# connection = pymongo.Connection('192.168.0.72',27017)
# db = connection.comment

connection = pymongo.MongoClient('192.168.9.25',27017)
db = connection.comment
db.authenticate('moster','shzygjrmdwg')

# connRes = httplib.HTTPConnection("data.android.d.cn", 80)
resHost = "data.android.d.cn"
resPort = 80
# connInfo = httplib.HTTPConnection("api.news.d.cn", 80)
infoHost = "api.news.d.cn"
infoPort = 80
# connUser = httplib.HTTPConnection("my.d.cn", 80)
# connUser = httplib.HTTPConnection("211.147.5.170", 7031)
# userHost = "211.147.5.170"
# userPort = 7031
userHost = "my.d.cn"
userPort = 80

#http://swf.service.d.cn/Rival?extract-words=false&just-check=true
#comment.d.cn/comment/_i/userActionStat?user=927
keywordHost = "comment.d.cn"
keywordPort = 80

# keywordHost = "localhost"
# keywordPort = 8080

#api
api_resource = "http://data.android.d.cn/orig/resource"
api_information = "http://api.news.d.cn/GetNewsBasicInfoByID.ashx?ids="
# api_user = "http://115.182.49.237:7001/api/member/"
api_user = "http://my.d.cn/api/member/pub-info.json?mids="
# api_keyword = "http://swf.service.d.cn/Rival?extract-words=false&just-check=true"
api_keyword = "http://comment.d.cn/comment/_i/checkHotKeyword"
# api_keyword = "http://localhost:8080/dj-cd-comment/comment/_i/checkHotKeyword"

maxStatLimit=300
top=50
daySeconds=60 * 60 * 24

dayOfMonth = int(datetime.date.today().strftime("%d"))
dayOfWeek = int(datetime.date.today().strftime("%w"))

# dayOfWeek = 1

today = datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
monthStr = str(datetime.date.today().month)
if(len(monthStr)==1):
    monthStr = "0"+monthStr
dayStr = str(datetime.date.today().day)
if(len(dayStr)==1):
    dayStr = "0"+dayStr
intToday = int(str(datetime.date.today().year) + monthStr + dayStr)
intOneWeekAgo = int(str(today + datetime.timedelta(days=-7)).replace("-",""))
yestoday = today + datetime.timedelta(days=-1)
todayMilliSeconds = int(time.mktime(time.strptime(str(today), "%Y-%m-%d"))) * 1000
yestodayMilliSeconds =  int(time.mktime(time.strptime(str(yestoday), "%Y-%m-%d"))) * 1000


#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"评论系统衰减值计算错误信息（dailyStatResCommentHot.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

def main():
    #每日集赞
    try:
        statGoodRatRankingDaily()
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
     
    #每日交互  
    try:    
        statCommunityRankingDaily()
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
     
    #每周达人
    statTopRankExpert()


# 每日集赞榜
#  1.每天24时更新；
#  2.显示当天50条集赞最多的评论内容，玩家信息, 对应游戏(接口)
def statGoodRatRankingDaily():
    doStat = False
    loop = 0
    for out in db.resourceComment.find({"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}, "goodRat":{"$gt":0}}).sort("goodRat",pymongo.DESCENDING):
        try:
            
            try:
                out["user"] = int(out["user"])
            except Exception:
                continue
            out["id_"] = out["_id"]
            out["_id"] = ObjectId()
            out["statTime"] = intToday
            out["tt"] = time.time()
            out["rankType"] = 1
            requestResourceInfo(out)
            if(filterKeyWord(out["content"])!=True and out["rname"] != None and out["rname"] != ""):
                db.statCommentRankDaily.insert(out)
                loop = loop+1
                doStat = True
            if(loop>=top):
                break
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG
    if(doStat):        
        db.statCommentRankDaily.remove({"rankType":1, "statTime":{"$lt":intOneWeekAgo}})

# 每日互动榜
#   1.每天24时更新；
#   2.显示当天50条被回复最多的评论内容，玩家信息，对应游戏 subCnt
def statCommunityRankingDaily():
#     db.tmp_mr_stat_communitiyTopRank.remove({})
    doStat = False
    condition = {"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}, "replyId":{"$gt":0}}

    mapfun = Code("function () {emit(this.replyId, 1)}")
    reducefun = Code("function (key, values) {"
                     "  var total = 0;"
                     "  for (var i = 0; i < values.length; i++) {"
                     "    total += values[i];"
                     "  }"
                     "  return total;"
                     "}")

    result = db.resourceComment.map_reduce(mapfun, reducefun, "tmp_mr_stat_communitiyTopRank", query=condition)
    loop = 0
    for doc in result.find().sort("value",pymongo.DESCENDING):
        try:
            for out in db.resourceComment.find({"_id":doc["_id"]}).limit(1):
                try:
                    out["user"] = int(out["user"])
                except Exception:
                    break
                if(out["opTime"] < yestodayMilliSeconds):
                    break
                out["id_"] = out["_id"]
                out["_id"] = ObjectId()
                out["statTime"] = intToday
                out["tt"] = time.time()
                out["rankType"] = 2
                out["replyCount"] = int(doc["value"])
                requestResourceInfo(out)
                if(filterKeyWord(out["content"])!=True and out["rname"] != None and out["rname"] != ""):
                    loop = loop + 1
                    db.statCommentRankDaily.insert(out)
                    doStat = True
            if(loop>=top):
                break
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG
    if(doStat):        
        db.statCommentRankDaily.remove({"rankType":2, "statTime":{"$lt":intOneWeekAgo}})

# 调用基础服务进行关键字屏蔽
# {"check-result":false} //true包含     
def filterKeyWord(content):
    connKeyword = httplib.HTTPConnection(keywordHost, keywordPort)
    form = urllib.urlencode({"content":content})
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    connKeyword.request(method="POST",url=api_keyword, body=form,headers=headers)
    response = connKeyword.getresponse()
    res= response.read()
    tmp = json.loads(res)
    contains = tmp["check-result"]
    if(contains!=None):
        return contains
    return False

# 每周上榜达人：每周一更新
#    1.每天周更新：
#    2.上榜次最多，以及每周评论集赞数和被回复数
#    3.上榜次权重>集赞权重>互动榜权重
#    注：上过集赞或集贴两个榜单 , "name", "avatarUrl"
def statTopRankExpert():
    if(dayOfWeek==1):
        groupKey = ["user"]
        condition = {}
        initial = {"count":0, "goodRat":0, "replyCount":0, "statDay":dayOfMonth}
        func = Code("function(obj, prev) {"
                    "    prev.count++;"
                    "    prev.goodRat+=obj.goodRat;"
                    "    if(!isNaN(obj.replyCount)){"
                    "        prev.replyCount+=obj.replyCount;"
                    "    }"
                    "}")
        result = db.statCommentRankDaily.group(groupKey,condition,initial,func)
        def f(x):
            return x["count"]
        def mycmp(a, b):
            if(a["count"] > b["count"]):
                return -1
            if(a["count"] < b["count"]):
                return 1
            if(a["count"] == b["count"]):
                if(b["goodRat"]==None):
                    return -1
                if(a["goodRat"]==None):
                    return 1
                if(a["goodRat"] > b["goodRat"]):
                    return -1
                if(a["goodRat"] < b["goodRat"]):
                    return 1
                if(a["goodRat"] == b["goodRat"]):
                    if(b["replyCount"]==None):
                        return -1
                    if(a["replyCount"]==None):
                        return 1
                    if(a["replyCount"] > b["replyCount"]):
                        return -1

            return 1

        result.sort(cmp=mycmp,reverse=False)
        #TODO-------------------------------------------------------------------------
        for user in result:
            requestUserInfo(user)

        db.statCommentExpertRankWeekly.insert(result)
        db.statCommentExpertRankWeekly.remove({"statDay":{"$ne":dayOfMonth}})

def requestResourceInfo(out):
    resourceKey = out["resourceKey"]
    out["rname"] = None
    if(resourceKey!=None):
        keys = resourceKey.split(":")
        resid = int(keys[0])
        restype = int(keys[1])
        out["rid"] = resid
        out["rtype"] = restype
        if(restype==1 or restype==2 or restype==5):
            api = api_resource + "?ids=" + str(resid) + "&type=" + str(restype)
            connRes = httplib.HTTPConnection(resHost, resPort)
            connRes.request(method="GET",url=api)
            response = connRes.getresponse()
            res= response.read()
            for tmp in json.loads(res):
                out["rname"] = tmp["name"]
                out["icon"] = tmp["icon"]
        elif(restype==8):
            api = api_information + str(resid)
            connInfo = httplib.HTTPConnection(infoHost, infoPort)
            connInfo.request(method="GET",url=api)
            response = connInfo.getresponse()
            res= response.read()
            for tmp in json.loads(res):
                out["rname"] = tmp["Title"]
                out["icon"] = tmp["IconUrl"]
                


def requestUserInfo(out):
    try:
        out["user"] = int(out["user"])
    except Exception:
        out["user"] = 0
    out["avatarUrl"] = "http://tools.service.d.cn/userhead/get?mid=" + str(out["user"]) + "&size=large"
    out["count"] = int(out["count"])
    out["goodRat"] = int(out["goodRat"])
    out["replyCount"] = int(out["replyCount"])
    user = str(out["user"])
    if(user!=None and user!=""):
        try:
            api = api_user + user
            connUser = httplib.HTTPConnection(userHost, userPort)
            connUser.request(method="GET",url=api)
            response = connUser.getresponse()
            res= response.read()
            tmp = json.loads(res)
            userObj = tmp["members"]
            if(len(userObj)>0):
                userObj = userObj[0]
                out["userQuote"] = userObj["quote"]
                out["name"] = userObj["nickName"]
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

###############################################################
if __name__ == '__main__':
    try:
        main()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if connection:
            connection.close()
        if ERROR_MSG:
            sendMail()

