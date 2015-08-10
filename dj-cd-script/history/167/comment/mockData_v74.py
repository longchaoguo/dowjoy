#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月11日

@author: qiu.zhong@downjoy.com

# crontab 设置定时执行
30 1 * * * /usr/local/bin/pyscript/comment/dailyStatCommentRank.py >> /home/downjoy/logs/py_dailyStatCommentRank.log &

·每日精彩评论
    ·每天点赞量倒序，30条？
    ·提供删除接口

·评论达人榜
    ·每天发表评论最多倒序，10条？

·游戏评论排行
    ·每天新增评论最多应用倒序，10条？

以上接口都要按日期查？保留30天记录？

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
from sre_constants import RANGE

reload(sys)
sys.setdefaultencoding('utf-8')

# connection = pymongo.Connection('192.168.0.72',27017)
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

daySeconds=60 * 60 * 24

dayOfMonth = int(datetime.date.today().strftime("%d"))
dayOfWeek = int(datetime.date.today().strftime("%w"))

# dayOfWeek = 1

today = datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)

today = today + datetime.timedelta(days=-11)

monthStr = str(today.month)
if(len(monthStr)==1):
    monthStr = "0"+monthStr
    
# dayStr = str(datetime.date.today().day)
dayStr = str(today.day)


if(len(dayStr)==1):
    dayStr = "0"+dayStr
intToday = int(str(today.year) + monthStr + dayStr)
intOneWeekAgo = int(str(today + datetime.timedelta(days=-7)).replace("-",""))
int50daysAgo = int(str(today + datetime.timedelta(days=-50)).replace("-",""))
yestoday = today + datetime.timedelta(days=-1)

todayMilliSeconds = int(time.mktime(time.strptime(str(today), "%Y-%m-%d"))) * 1000
yestodayMilliSeconds =  int(time.mktime(time.strptime(str(yestoday), "%Y-%m-%d"))) * 1000

intToday = 20150616;


#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"评论系统7.4排行榜每日统计脚本（dailyStatCommentRank_v74.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

# TODO 加一索引：db.resourceComment.ensureIndex({replyId:1},{background:1})

# ·每日精彩评论
#     ·每天点赞量倒序，30条？
#     ·提供删除接口
# 
# ·评论达人榜
#     ·每天发表评论最多倒序，10条？
# 
# ·游戏评论排行
#     ·每天新增评论最多应用倒序，10条？
# 
# 以上接口都要按日期查？保留30天记录？
def main():
    #每日精彩评论
    try:
        statGoodCommentRankingDaily(intToday)
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
       
    #评论达人榜  
    try:    
        statCommentExpertRankingDaily(intToday)
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
      
    #游戏评论排行
    statResourceCommentRankingDaily(intToday)

# ·每日精彩评论
#     ·每天点赞量倒序，30条？
#     ·提供删除接口
def statGoodCommentRankingDaily(intToday):
    maxStatLimit=100 #最大量
    statCount = 30 #要求量
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
            if(loop>=statCount):
                out["validateStatus"] = 0 #无效
            else:
                out["validateStatus"] = 1 #有效
            requestResourceInfo(out)
            if(filterKeyWord(out["content"])!=True and out["rname"] != None and out["rname"] != ""):
                db.v74_statCommentRankDaily.insert(out)
                loop = loop+1
                doStat = True
            if(loop>=maxStatLimit):
                break
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG
    if(doStat):        
        db.v74_statCommentRankDaily.remove({"statTime":{"$lt":int50daysAgo}})

# ·评论达人榜
#     ·每天发表评论最多倒序，10条？
def statCommentExpertRankingDaily(intToday):
    statCount = 30 #要求量
    doStat = False
    condition = {"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}, "isRobot":0}

    mapfun = Code("function () {emit(this.user, 1)}")
    reducefun = Code("function (key, values) {"
                     "  var total = 0;"
                     "  for (var i = 0; i < values.length; i++) {"
                     "    total += values[i];"
                     "  }"
                     "  return total;"
                     "}")

    result = db.resourceComment.map_reduce(mapfun, reducefun, "v74_tmp_mr_stat_statCommentExpertRankingDaily", query=condition)
    loop = 0
    
    for doc in result.find().sort("value",pymongo.DESCENDING).limit(statCount):
        try:
            userId = doc["_id"]
            userObj = {}
            userObj["commentCount"] = int(doc["value"])
            goodRat = 0
            replyCount = 0
            for out in db.resourceComment.find({"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds},"user":userId}, {"goodRat":1}):
                tmp = 0
                commentId = out["_id"]
                try:
                    tmp = int(out["goodRat"])
                    goodRat = goodRat + tmp
                except Exception:
                    print commentId
                
                try: 
                    replyCount = replyCount + db.resourceComment.find({"replyId", commentId}).count()
                except Exception:
                    print commentId
            userObj["user"] = userId
            userObj["goodRat"] = goodRat
            userObj["replyCount"] = replyCount
            userObj["statTime"] = intToday
#             out["tt"] = time.time()
            requestUserInfo(userObj)        
            db.v74_statCommentExpertRankingDaily.insert(userObj)
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG
            
    db.v74_statCommentExpertRankingDaily.remove({"statTime":{"$lt":int50daysAgo}})

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

# ·游戏评论排行
#     ·每天新增评论最多应用倒序，10条？
def statResourceCommentRankingDaily(intToday):
    statCount = 30 #要求量
    resourceRankMap = {}
    for out in db.resourceComment.find({"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}, "isRobot":0},{"resourceKey":1}):
        resourceKey = out["resourceKey"]
        keys = resourceKey.split(":")
        rid = int(keys[0])
        rtype = int(keys[1])
        if(rtype==1 or rtype==5):
            commentCount = 0
            if resourceRankMap.has_key(resourceKey):
                commentCount = resourceRankMap.get(resourceKey)
            commentCount = commentCount + 1
            resourceRankMap[resourceKey] = commentCount
    
    
    for key in resourceRankMap.keys():
        dbObj = {}
        dbObj["_id"] = ObjectId()
        commentCount = resourceRankMap.get(key)
        dbObj["resourceKey"] = key
        dbObj["commentCount"] = commentCount
        dbObj["statTime"] = intToday
        dbObj["totalCommentCount"] = getResourceCommentCount(key)
        requestResourceInfo(dbObj)
        db.v74_statResourceCommentRankingDaily.insert(dbObj)        
    
    db.v74_statResourceCommentRankingDaily.remove({"statTime":{"$lt":int50daysAgo}})
    
    
def getResourceCommentCount(resourceKey):
    count = 0
    try:
        commentCount = db.resourceInfo.find_one({"_id":resourceKey}, {"commentCount":1})
        count = commentCount["commentCount"]
    except Exception:
        count = 0
    count = int(count)
    return count


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
                out["size"] = tmp["size"]
                out["star"] = tmp["star"]
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
#     out["count"] = int(out["count"])
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

