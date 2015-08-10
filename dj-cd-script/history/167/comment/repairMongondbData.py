#!/usr/bin/python
# -*- coding: cp936 -*-
__author__ = 'sgq'

import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO

from djutil.MailUtil import MailUtil

connection = pymongo.MongoClient('192.168.0.72',27017)
db = connection.communication

mysql = MySQLdb.connect(host="192.168.0.4", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"交互系统comm_msg_box和comm_user_activity集合删除合并资源数据（repairMongondbData.py）".encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'

def repairComm_msg_box():
    combindIds = getAllCombindResourceId()
    for out in db.comm_msg_box.find({"appRes":{"$ne":None}}).batch_size(10000):
        id = out["_id"];
        noticeType = out["noticeType"]
        if out.has_key("appRes"):
            appRes = out["appRes"]
            userId = out["revUserId"]
            if appRes["resType"]==1 and combindIds.has_key(appRes["resId"]):
                if noticeType == 2: ##评论相关更新节点
                    #print 'update'
                    appRes['resId']=combindIds[appRes['resId']]
                    db.comm_msg_box.update({"_id":id}, {"$set":{"appRes":appRes}})
                else:## 应用更新 应用发布 应用资讯，与应用相关的资讯，包括新闻、测评、攻略 删除节点
                    resId = combindIds[appRes['resId']]
                    re = db.comm_msg_box.find_one({"revUserId":userId,"appRes.resId":resId})
                    if re :
                        #print 'del'
                        db.comm_msg_box.remove({"_id":id})
                        db.comm_user_feed.update({"_id":userId,"msgCount":{"$ne":None}},{"$inc":{"msgCount":-1}})
                    else:
                        #print 'del update'
                        appRes['resId']=combindIds[appRes['resId']]
                        db.comm_msg_box.update({"_id":id}, {"$set":{"appRes":appRes}})
def repairComm_user_activity():
    combindIds = getAllCombindResourceId()
    for out in db.comm_user_activity.find({"appRes":{"$ne":None}}).batch_size(10000):
        id = out["_id"];
        activityType = out["activityType"]
        if out.has_key("appRes"):
            appRes = out["appRes"]
            userId = out["cuserId"]
            if appRes["resType"]==1 and combindIds.has_key(appRes["resId"]):
                if activityType in [1,3]: ##发表评论 资讯发表 相关更新节点
                    #print 'update'
                    appRes['resId']=combindIds[appRes['resId']]
                    db.comm_user_activity.update({"_id":id}, {"$set":{"appRes":appRes}})
                else:##  下载应用  喜欢应用 评分 删除节点
                    #print 'del'
                    re = db.comm_user_activity.find_one({"cuserId":userId,"appRes.resId":combindIds[appRes['resId']]})
                    if re:
                        db.comm_user_activity.remove({"_id":id})
                        db.comm_user_feed.update({"_id":userId,"activityCount":{"$ne":None}},{"$inc":{"activityCount":-1}})
                    else:
                       appRes['resId']=combindIds[appRes['resId']]
                       db.comm_user_activity.update({"_id":id}, {"$set":{"appRes":appRes}})

def chekRepairComm_msg_boxIsDone():
    combindIds = getAllCombindResourceId()
    keys = combindIds.keys()
    for gameId in keys:
        re =  db.comm_msg_box.find_one({"appRes.resId":gameId})
        if re :
           print re
           print u'修正msg_box数据失败'
           return
    print u'修正msg_box数据成功'
def chekRepairComm_user_activityIsDone():
    combindIds = getAllCombindResourceId()
    keys = combindIds.keys()
    for gameId in keys:
        re =  db.comm_user_activity.find_one({"appRes.resId":gameId})
        if re :
           print re
           print u'修正user_activity数据失败'
    print u'修正user_activity数据成功'

def getAllCombindResourceId():
    sql="SELECT ID, CHANNEL_ID FROM GAME WHERE ID <> CHANNEL_ID AND CHANNEL_ID > 0 ORDER BY ID ASC"
    idMap = {}
    cursor.execute(sql)
    for row in cursor.fetchall():
        idMap[row[0]] = row[1];
    return idMap

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

###############################################################
if __name__ == '__main__':
    try:
        repairComm_msg_box()
        repairComm_user_activity()
        print 'done'
        # chekRepairComm_user_activityIsDone()
        # chekRepairComm_msg_boxIsDone()
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
