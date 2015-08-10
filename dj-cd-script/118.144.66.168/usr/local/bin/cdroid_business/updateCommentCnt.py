#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2014/12/16 $"

################################################
#功能描述：定时更新游戏、软件、网游评论数
################################################

import StringIO
import datetime
import pymongo
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

#mysql链接设置
dbUtil_35 = DBUtil('droid_game_10')

# mongodb链接设置
mongoCon = pymongo.MongoClient("192.168.0.72", 27017)
mdb = mongoCon.comment

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"更新资源评论数错误信息（updateCommentCnt.py）".encode("gbk")
mailTo = ['shan.liang@downjoy.com']
mailContents = u'Hi: \n'

#标识不同资源类别
RESOURCE_TYPE_GAME = 1      #游戏
RESOURCE_TYPE_SOFTWARE = 2  #软件
RESOURCE_TYPE_NEWS = 3      #资讯
RESOURCE_TYPE_NETGAME = 5   #网游
RESOURCE_TYPE_SPECIAL_TOPIC = 7 #专题
RESOURCE_TYPE_ORIGINAL_NEWS = 8 #原创

#更新所有游戏、软件评论数    
def updateGameSoftwareCommentCnt():
    #获取游戏、软件
    sql = 'SELECT CHANNEL_ID, RESOURCE_TYPE FROM GAME WHERE STATUS = 1 GROUP BY CHANNEL_ID ORDER BY CHANNEL_ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #查询评论数
            resChannelId = row[0]
            resType = row[1]
            queryId = str(resChannelId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #更新评论数
            if commentCnt != 0:
                updateCommentCnt(resChannelId, resType, commentCnt)
        #下一页查询
        startIdx = startIdx + limitRange

#更新所有网游评论数
def updateNetgameCommentCnt():
    #获取网游
    sql = 'select ID from NETGAME_CHANNEL order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #查询评论数
            resId = row[0]
            resType = RESOURCE_TYPE_NETGAME
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #更新评论数
            if commentCnt != 0:
                updateCommentCnt(resId, resType, commentCnt)
        #下一页查询
        startIdx = startIdx + limitRange

#更新所有资讯评论数
def updateNewsCommentCnt():
    #获取资讯
    sql = 'select ID, ORIGINAL_ID from NEWS order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #查询评论数
            resId = row[0]
            resType = RESOURCE_TYPE_NEWS
            if row[1] and row[1] > 0:
                resId = row[1]
                resType = RESOURCE_TYPE_ORIGINAL_NEWS
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #更新评论数
            if commentCnt != 0:
                resId = row[0]
                resType = RESOURCE_TYPE_NEWS
                updateCommentCnt(resId, resType, commentCnt)
        #下一页查询
        startIdx = startIdx + limitRange

#更新所有专题评论数        
def updateSpecialTopicCommentCnt():
    #获取资讯
    sql = 'select ID, ORIGINAL_ID from SPECIAL_TOPIC order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #查询评论数
            resId = row[0]
            resType = RESOURCE_TYPE_SPECIAL_TOPIC
            if row[1] and row[1] > 0:
                resId = row[1]
                resType = RESOURCE_TYPE_ORIGINAL_NEWS
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #更新评论数
            if commentCnt != 0:
                resId = row[0]
                resType = RESOURCE_TYPE_SPECIAL_TOPIC
                updateCommentCnt(resId, resType, commentCnt)
        #下一页查询
        startIdx = startIdx + limitRange
 
#查询评论数
def queryCommentCnt(id):
    commentCnt = 0
    
    row = mdb.resourceInfo.find_one({"_id":id})
    if row and row.has_key("commentCount"):
        commentCnt = row["commentCount"]
    
    return commentCnt
    
#更新单个资源的评论数
def updateCommentCnt(resId, resType, commentCnt):
    if resType == RESOURCE_TYPE_GAME or resType == RESOURCE_TYPE_SOFTWARE: #游戏、软件
        sql = 'update GAME set comments = %d where CHANNEL_ID = %d and RESOURCE_TYPE = %d' % (commentCnt, resId, resType)
    elif resType == RESOURCE_TYPE_NETGAME: #网游
        sql = 'update NETGAME_CHANNEL set comments = %d where ID = %d' % (commentCnt, resId)
    elif resType == RESOURCE_TYPE_NEWS: #资讯
        sql = 'update NEWS set COMMENTS = %d where ID = %d' % (commentCnt, resId)
    elif resType == RESOURCE_TYPE_SPECIAL_TOPIC: #专题
        sql = 'update SPECIAL_TOPIC set COMMENTS = %d where ID = %d' % (commentCnt, resId)
    else: 
        return
    
    dbUtil_35.update(sql)

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
###############################################################
if __name__ == '__main__':
    try:
        #更新所有游戏、软件评论数    
        updateGameSoftwareCommentCnt()
        
        #更新所有网游评论数
        updateNetgameCommentCnt()
        
        #更新所有资讯评论数
        updateNewsCommentCnt()
        
        #更新所有专题评论数   
        updateSpecialTopicCommentCnt()
        
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
        
    finally:
        if dbUtil_35: dbUtil_35.close()
        mongoCon.close()
        if ERROR_MSG:
            sendMail()
        
