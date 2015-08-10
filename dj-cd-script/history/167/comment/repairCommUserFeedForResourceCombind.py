#!/usr/bin/python
#encoding=utf-8
'''
Created on 2015年03月30日

@author: qiu.zhong@downjoy.com

因资源合并需求，修复对应comm_user_feed集合中的favorites字段和对应favCount字段
注意：favCount使用inc而不是set，避免数据混乱
'''
import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO
from djutil.MailUtil import MailUtil

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.communication

mysql = MySQLdb.connect(host="192.168.0.4", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"交互系统comm_user_feed集合删除合并资源数据，并更新favCount字段（repairCommUserFeedForResourceCombind.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

def main():
    combindIds = getAllCombindResourceId()
    for out in db.comm_user_feed.find({},{"favorites":1}).batch_size(10000):
        id = out["_id"];
        if out.has_key("favorites"):
            favorites = out["favorites"]
            needModify = False
            modifiedFavorites = []
            matchCount = 0
            for favorite in favorites:
                appendedPrimary = {}
                if favorite["resType"]==1:
                    if combindIds.has_key(favorite["id"]):
                        primaryId = combindIds.get(favorite["id"])
                        ex = db.comm_user_feed.find_one({"_id":id, "favorites.id":primaryId, "favorites.resType":1})
                        
                        #如果存在主id
                        if ex:
                            matchCount = matchCount - 1
                        #如果不存在主id
                        else:
                            #如果还没转换为主id记录
                            if not appendedPrimary.has_key(primaryId): 
                                appendedPrimary[primaryId] = primaryId
                                favorite["id"] = primaryId
                                modifiedFavorites.append(favorite)
                            #如果已经转换
                            else:
                                matchCount = matchCount - 1
                        needModify = True
                        
                    else:
                        modifiedFavorites.append(favorite)
            if(needModify):
                db.comm_user_feed.update({"_id":id}, {"$set":{"favorites":modifiedFavorites}, "$inc":{"favCount":matchCount}})
                #更新$set:favorites, $inc:favCount
            

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
