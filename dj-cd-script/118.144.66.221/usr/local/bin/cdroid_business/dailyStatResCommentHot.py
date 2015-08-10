#!/usr/bin/python
#encoding=utf-8
'''
# Created on 2014/12/8/
@author: qiu.zhong@downjoy.com

note1:该脚本每天1:00am执行
note2:resourceInfo集合增加的字段：
        hr:资源热门评论热度边界值，即大于该热度值的算热门评论
        hc:资源热门评论列表应该显示的条数
        mh:资源最大热度值

# crontab 设置定时执行
0 1 * * * /usr/local/bin/pyscript/comment/dailyStatResCommentHot.py >> /home/downjoy/logs/py_dailyStatResCommentHot.log &

每天执行一次
#1.1. 获取编辑设置值（热门评论边界位序，衰减因子等）
#1.2. 取最大热度值(该步骤改为最开始执行一次，因为是取所有评论的最大值，而不是每个资源评论最大值)

#2.1. 获取资源评论数
#2.2. 从resourceInfo集合获取资源热门评论边界值，如无则计算对应值
#2.3. 获取资源的热度值

#2.4. 根据热门评论衰减算法，计算并更新热门评论的热度值
规则：fianlHeat = currentHeat – (curreentHeat/maxHeat)*（0.5*衰减因子*游戏应用热度（当前时间-评论发表时间）²）
    #. 遍历resourceComment表的所有评论（优化，不单独遍历resourceComment，利用该循环，以及上面已经计算好的hotRange, maxHot），根据resourceKey到resourceInfo表查询maxHot，以及 #1中计算得到的hot边界值
    #. 根据上面查得的hot边界值，判断该评论是否热门评论，如果是，继续下面步骤
    #. 根据resourceKey解析得到resid和resType到mysql查询对应游戏的应用热度
    #. 根据上面所查询到的值，结合规则公式，计算热门评论衰减后的值，再根据resourceKey更新该值

#2.5. 统计每个资源的热门评论边界热度值：每天周期统计，去重后倒序排名第13位热度值，如果为0则排名依次降低直到不为0
    #. 取编辑设置的热门评论最低排位边界，衰减因子
    #. 热门评论：根据rank位数查询热门评论的边界热度值
    #. 将上述计算的每个resourceKey对应的hot边界值，最大热度值存入ResourceInfo(资源统计值集合)集合

#2.6. 统计每个资源热门评论显示条数：
规则：当0<=T<10 热门显示：1条；当10<= T< 20 显示：2条；当20<= T < 30 显示：3条；当30<= T< 40 显示：4条；当40<= T < 50 显示：5条；当50<= T < 60 显示：6条；当60<=T显示10条；T:此应用的总评论数
    #. 根据resourceKey从ResourceInfo集合中获取资源评论总数 T
    #. 根据规则计算热门评论列表数量hc，并保存到resourceInfo集合

'''
import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO
from djutil.MailUtil import MailUtil

# connection = pymongo.Connection('192.168.0.72',27017)
# db = connection.comment
connection = pymongo.MongoClient('192.168.9.25',27017)
db = connection.comment
db.authenticate('moster','shzygjrmdwg')

key_hot = "hot"
key_resource = "resourceKey"
key_hotrange = "hr"
key_hotcount = "hc"
key_pubtime= "pubTime"

mysql = MySQLdb.connect(host="192.168.0.4", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"评论系统衰减值计算错误信息（dailyStatResCommentHot.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

def main():
    #1.1
    config = getConfig()
    #1.2
    maxHot=getMaxHot()
    for out in db.resourceComment.distinct(key_resource):
        resourceKey = out
        
        if(resourceKey==None):
            continue

        #2.1
        commentCount = getResourceCommentCount(resourceKey)
        #2.2
        hotRange = getHotRange(config["rank"], resourceKey)

        #优化，不单独遍历resourceComment，利用该循环，以及上面已经计算好的hotRange, maxHot
        #优化，带入上面的hotRange，结合resourceKey，查询热门评论
        #2.3
        resHot = getResourceHotValue(resourceKey)
        decayFactor = config["decayFactor"]
        #2.4
        doHotCommentDecay(resourceKey, hotRange["hotRange"], decayFactor, maxHot, resHot, hotRange["hotCount"])

        #2.5
        hotRange=computeHotRange(config["rank"], resourceKey)
        #2.6
        saveResourceHotRange(resourceKey, hotRange)

        #2.7
        computeAndSaveHotListCount(resourceKey, commentCount)
#         print ""+str(hotRange)+" : "+resourceKey


# 1.1. 取编辑设置的热门评论最低排位边界，衰减因子
def getConfig():
    conf = db.commentParamTO.find_one({"type":"hotConfig"})
    n = conf["hotRank"]
    decayFactor = conf["decayFactor"]
    return {"rank":n, "decayFactor":decayFactor}

# 1.2. 取资源最大热度值
def getMaxHot():
    for out in db.resourceComment.find({},{key_hot:1}).sort(key_hot,pymongo.DESCENDING).limit(1):
        maxHot = out[key_hot];
        if(maxHot!=None and maxHot>0):
            return out[key_hot]
        else:
            break
        #     for out in db.resourceComment.find({key_resource:resourceKey},{key_hot:1}).sort(key_hot,pymongo.DESCENDING).limit(1):
        #         if(hasattr(out, key_hot)):
        #             return out[key_hot]
    return 0

# 2.1. 根据resourceKey从ResourceInfo集合中获取资源评论总数 T
def getResourceCommentCount(resourceKey):
    count = 0
    try:
        commentCount = db.resourceInfo.find_one({"_id":resourceKey}, {"commentCount":1})
        count = commentCount["commentCount"]
    except Exception:
        count = 0
    return int(count)

# 2.2. 为热度衰减值计算获取热门评论边界值
def getHotRange(rank, resourceKey):
    hotRange = None
    hotCount = 0
    for out in db.resourceInfo.find({"_id":resourceKey},{key_hotrange:1, key_hotcount:1}).limit(1):
        try:
            hotRange = out[key_hotrange]
        except Exception:
            hotRange = None
        try:
            hotCount = int(out[key_hotcount])
        except Exception:
            hotCount = 0
        break;
    
    if(hotRange==None or hotRange<0):
        hotRange = computeHotRange(rank, resourceKey)
        
    
    return {"hotRange":hotRange, "hotCount":hotCount};

# 2.3. 根据resourceKey解析得到resid和resType到mysql查询对应游戏的应用热度
def getResourceHotValue(resourceKey):
    keys = resourceKey.split(':')
    resid = keys[0]
    restype = keys[1]
    resHot = None
    sql=None
    # 1    Android游戏
    # 2    Android软件
    # 5    Android网游
    if(restype=="1" or restype=="2"):
        sql="select coalesce(round(least(log(1.1, t1.HOT_CNT), 100)),0)/100 AS HOT_CNT from GAME t1 where t1.ID="+resid+" and t1.RESOURCE_TYPE="+restype
    elif(restype=="5"):
        sql="select t1.HOT_CNT/100  from NETGAME_CHANNEL t1 where t1.ID = " + resid

    if(sql!=None):
        cursor.execute(sql)
        for row in cursor.fetchall():
            for r in row:
                resHot = r
                break
            break

    if(resHot==None or resHot<=0):
        resHot = 1
    return resHot

# 2.4. 根据上面所查询到的值，结合规则公式，计算热门评论衰减后的值，再根据resourceKey更新该值
def doHotCommentDecay(resourceKey, hotRange, decayFactor, maxHot, resHot, hotCount):
    if(hotCount > 0):
        stickCount = 0
        try:
            stickCount = db.resourceComment.find({key_resource:resourceKey,"stick":True}).count()
            stickCount = int(stickCount)
        except:
            stickCount = 0
        hotCount = hotCount - stickCount
        if(hotCount<=0):
            return
        
        for out in db.resourceComment.find({key_resource:resourceKey, key_hot:{"$gt":hotRange}},{"_id":1,key_hot:1,key_pubtime:1}).sort(key_hot,pymongo.DESCENDING).limit(hotCount):
            #fianlHeat = currentHeat – (curreentHeat/maxHeat)*（0.5*衰减因子*游戏应用热度（当前时间-评论发表时间）²）
            hot = out[key_hot]
            #         print out[key_pubtime]
            try:
                timeDiffMicroseconds = (time.time() - time.mktime(time.strptime(out[key_pubtime], '%Y-%m-%d %H:%M:%S'))) / 60 / 60 / 24
            except:
                timeDiffMicroseconds = 1
    #             print "time exception"
            finalHot = hot - (hot/maxHot)*(0.5*decayFactor*resHot*(timeDiffMicroseconds)**2)
            if(finalHot<0):
                #print str(finalHot)+ " : " + str(hot) + " : " + str(maxHot) + " : " + str(resHot) + " : " + str(timeDiffMicroseconds)
                finalHot = 0
            nowMillseconds = int(time.time() * 1000)
            if(resourceKey=="45759:1"):
                print resourceKey + " : " + str(hot) + " : " + str(finalHot) + " : " + str(hotCount)
            db.resourceComment.update({"_id":out["_id"]}, {"$set":{key_hot:finalHot, "time":nowMillseconds}})

# 2.5. 热门评论：根据rank位数查询热门评论的边界热度值
def computeHotRange(rank, resourceKey):
    groupKey = [key_hot]
    condition = {key_resource:resourceKey}
    initial = {"count":0}
    func = '''
            function(obj,prev)
            {
                prev.count++;
            }
        '''
    result = db.resourceComment.group(groupKey,condition,initial,func)
    def f(x):
        return x[key_hot]
    result.sort(key=f,reverse=True)
    l = len(result)
    n = l if rank>l else rank
    hot = 0
    if(n>0):
        h=result[n-1][key_hot]
        if(h == 0):
            for i in range(0, n):
                m=result[i][key_hot]
                if(m==0):
                    break
                h=m
        if(h!=None):
            hot=h
    return hot

# 2.6. 将上述计算的每个resourceKey对应的hot边界值，最大热度值存入ResourceInfo(资源统计值集合)集合
def saveResourceHotRange(resourceKey, hotRange):
    db.resourceInfo.update({"_id":resourceKey}, {"$set":{key_hotrange:hotRange}})

# 2.7. 根据规则计算热门评论列表数量hc，并保存到resourceInfo集合
def computeAndSaveHotListCount(resourceKey, commentCount):
    #当0<=T<10 热门显示：1条；当10<= T< 20 显示：2条；当20<= T < 30 显示：3条；
    #当30<= T< 40 显示：4条；当40<= T < 50 显示：5条；当50<= T < 60 显示：6条；
    #当60<=T显示10条；T:此应用的总评论数
    hotCount = 0
    if(commentCount==None or commentCount<=0):
        hotCount = 0
    elif(commentCount>=60):
        hotCount = 10
    else:
        hotCount = commentCount / 10 + 1
    hotCount = int(hotCount)
    db.resourceInfo.update({"_id":resourceKey}, {"$set":{key_hotcount:hotCount}})


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
        if mysql:
            mysql.close()
        if connection:
            connection.close()
        if ERROR_MSG:
            sendMail()

