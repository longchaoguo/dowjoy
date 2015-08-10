#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2014/12/16 $"

################################################
#������������ʱ������Ϸ�����������������
################################################

import StringIO
import datetime
import pymongo
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

#mysql��������
dbUtil_35 = DBUtil('droid_game_10')

# mongodb��������
mongoCon = pymongo.MongoClient("192.168.0.72", 27017)
mdb = mongoCon.comment

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"������Դ������������Ϣ��updateCommentCnt.py��".encode("gbk")
mailTo = ['shan.liang@downjoy.com']
mailContents = u'Hi: \n'

#��ʶ��ͬ��Դ���
RESOURCE_TYPE_GAME = 1      #��Ϸ
RESOURCE_TYPE_SOFTWARE = 2  #���
RESOURCE_TYPE_NEWS = 3      #��Ѷ
RESOURCE_TYPE_NETGAME = 5   #����
RESOURCE_TYPE_SPECIAL_TOPIC = 7 #ר��
RESOURCE_TYPE_ORIGINAL_NEWS = 8 #ԭ��

#����������Ϸ�����������    
def updateGameSoftwareCommentCnt():
    #��ȡ��Ϸ�����
    sql = 'SELECT CHANNEL_ID, RESOURCE_TYPE FROM GAME WHERE STATUS = 1 GROUP BY CHANNEL_ID ORDER BY CHANNEL_ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #��ѯ������
            resChannelId = row[0]
            resType = row[1]
            queryId = str(resChannelId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #����������
            if commentCnt != 0:
                updateCommentCnt(resChannelId, resType, commentCnt)
        #��һҳ��ѯ
        startIdx = startIdx + limitRange

#������������������
def updateNetgameCommentCnt():
    #��ȡ����
    sql = 'select ID from NETGAME_CHANNEL order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #��ѯ������
            resId = row[0]
            resType = RESOURCE_TYPE_NETGAME
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #����������
            if commentCnt != 0:
                updateCommentCnt(resId, resType, commentCnt)
        #��һҳ��ѯ
        startIdx = startIdx + limitRange

#����������Ѷ������
def updateNewsCommentCnt():
    #��ȡ��Ѷ
    sql = 'select ID, ORIGINAL_ID from NEWS order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #��ѯ������
            resId = row[0]
            resType = RESOURCE_TYPE_NEWS
            if row[1] and row[1] > 0:
                resId = row[1]
                resType = RESOURCE_TYPE_ORIGINAL_NEWS
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #����������
            if commentCnt != 0:
                resId = row[0]
                resType = RESOURCE_TYPE_NEWS
                updateCommentCnt(resId, resType, commentCnt)
        #��һҳ��ѯ
        startIdx = startIdx + limitRange

#��������ר��������        
def updateSpecialTopicCommentCnt():
    #��ȡ��Ѷ
    sql = 'select ID, ORIGINAL_ID from SPECIAL_TOPIC order by ID DESC limit %d, %d'
    
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows and len(rows) == 0:
            break
        for row in rows:
            #��ѯ������
            resId = row[0]
            resType = RESOURCE_TYPE_SPECIAL_TOPIC
            if row[1] and row[1] > 0:
                resId = row[1]
                resType = RESOURCE_TYPE_ORIGINAL_NEWS
            queryId = str(resId) + ':' + str(resType)
            commentCnt = queryCommentCnt(queryId)
            #����������
            if commentCnt != 0:
                resId = row[0]
                resType = RESOURCE_TYPE_SPECIAL_TOPIC
                updateCommentCnt(resId, resType, commentCnt)
        #��һҳ��ѯ
        startIdx = startIdx + limitRange
 
#��ѯ������
def queryCommentCnt(id):
    commentCnt = 0
    
    row = mdb.resourceInfo.find_one({"_id":id})
    if row and row.has_key("commentCount"):
        commentCnt = row["commentCount"]
    
    return commentCnt
    
#���µ�����Դ��������
def updateCommentCnt(resId, resType, commentCnt):
    if resType == RESOURCE_TYPE_GAME or resType == RESOURCE_TYPE_SOFTWARE: #��Ϸ�����
        sql = 'update GAME set comments = %d where CHANNEL_ID = %d and RESOURCE_TYPE = %d' % (commentCnt, resId, resType)
    elif resType == RESOURCE_TYPE_NETGAME: #����
        sql = 'update NETGAME_CHANNEL set comments = %d where ID = %d' % (commentCnt, resId)
    elif resType == RESOURCE_TYPE_NEWS: #��Ѷ
        sql = 'update NEWS set COMMENTS = %d where ID = %d' % (commentCnt, resId)
    elif resType == RESOURCE_TYPE_SPECIAL_TOPIC: #ר��
        sql = 'update SPECIAL_TOPIC set COMMENTS = %d where ID = %d' % (commentCnt, resId)
    else: 
        return
    
    dbUtil_35.update(sql)

def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
###############################################################
if __name__ == '__main__':
    try:
        #����������Ϸ�����������    
        updateGameSoftwareCommentCnt()
        
        #������������������
        updateNetgameCommentCnt()
        
        #����������Ѷ������
        updateNewsCommentCnt()
        
        #��������ר��������   
        updateSpecialTopicCommentCnt()
        
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
        
    finally:
        if dbUtil_35: dbUtil_35.close()
        mongoCon.close()
        if ERROR_MSG:
            sendMail()
        
