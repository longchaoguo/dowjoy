#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月10日

@author: qiu.zhong@downjoy.com
# 0.只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）

'''
import pymongo
import time
import MySQLdb
import StringIO

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment
key_hot = "hot"
key_resource = "resourceKey"
key_hotrange = "hr"
key_maxhot = "mh"
key_hotcount = "hc"
key_pubtime= "pubTime"

mysql = MySQLdb.connect(host="192.168.0.4", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

# 0. 只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）
def main():
    loop = 0;
    #1.1
    config = getConfig()
    #初始化资源热度值
    for out in db.resourceComment.find({}, {"resourceKey":1, "goodRat":1, "subCnt":1, "content":1}):
        lenContent = len(out["content"])
        scoreContent = 0
        isHot = False
        if(lenContent>=config["n"] and count5Chinese(out["content"])):
            scoreContent = config["m"]*config["e"]
            isHot = True
        hot = scoreContent + out["goodRat"] + out["subCnt"]
        if(hot<0):
            hot=0
        db.resourceComment.update({"_id":out["_id"]}, {"$set":{"hot":hot, "isHot":isHot}})
        loop = loop + 1

    #1.3
    maxHot=getMaxHot()

    for out in db.resourceComment.distinct(key_resource):
        resourceKey = out
        #2.1
        commentCount = getResourceCommentCount(resourceKey)
        #2.2
        hotRange = computeHotRange(config["rank"], resourceKey)
        
        #2.5
        saveResourceHotRange(resourceKey, hotRange)
        #2.6
        computeAndSaveHotListCount(resourceKey, commentCount)

def count5Chinese(content):
#     us = unicode(content, "utf-8")
    count = 0
    for ch in content:
        b = isChinese(ord(ch))
        if(b):
            count = count + 1
            if(count >= 5):
                return True
    return False

def isChinese(ch):
    return (ch >= 0x4E00 and ch < 0xA000) or (ch >= 0x3400 and ch < 0x4DBF) or (ch >= 0xF900 and ch < 0xFAFF)

# 1.1 取编辑设置的N(字数), M, E（字数占权重）
def getConfig():
    conf = db.commentParamTO.find_one({"type":"hotConfig"})
    n = conf["hotRank"]
    l = conf["wordNum"]
    decayFactor = conf["decayFactor"]
    m = conf["constantM"]
    e = conf["constantE"]

    return {"rank":n, "decayFactor":decayFactor, "n":l, "m":m, "e":e}

# 1.3. 取资源最大热度值
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
    count = int(count)
    return count

# 2.2. 热门评论：根据rank位数查询热门评论的边界热度值
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
        sql="select coalesce(round(least(log(1.1, t1.HOT_CNT), 100)),0) AS HOT_CNT from GAME t1 where t1.ID="+resid+" and t1.RESOURCE_TYPE="+restype
    elif(restype=="5"):
        sql="select t1.HOT_CNT  from NETGAME_CHANNEL t1 where t1.ID = " + resid

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

# 2.5. 将上述计算的每个resourceKey对应的hot边界值，最大热度值存入ResourceInfo(资源统计值集合)集合
def saveResourceHotRange(resourceKey, hotRange):
    db.resourceInfo.update({"_id":resourceKey}, {"$set":{key_hotrange:hotRange}})



# 2.6. 根据规则计算热门评论列表数量hc，并保存到resourceInfo集合
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



main()   