#!/usr/bin/python
#encoding=utf-8
'''
Created on 2015年03月30日

@author: qiu.zhong@downjoy.com

因资源合并需求，修复对应数据
'''
import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO
from djutil.MailUtil import MailUtil

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment

mysql = MySQLdb.connect(host="192.168.0.4", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"repairUserResourceForResourceCombind.py".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

#楼层怎么搞
def main():
    combindIds = getAllCombindResourceId()
    print combindIds
    for out in db.userResource.find({},{"resourceKey":1, "comment":1}).batch_size(10000):
        if out.has_key("resourceKey"):
            id = out["_id"]
            resourceKey = out["resourceKey"]
            tmp = resourceKey.split(":")
            resId = long(tmp[0])
            resType = int(tmp[1])
            if resType==1 and combindIds.has_key(resId):
                primaryId = combindIds.get(resId)
                newResourceKey = str(primaryId)+":1"
                setValue = {"resourceKey":newResourceKey}
                comment = out["comment"]
                comment.replace(resourceKey, newResourceKey)
#                 if out.has_key("subComments"):
#                     subComments = out["subComments"]
#                     if(subComments!=None and len(subComments)>0):
#                         for subComment in subComments:
#                             subComment["resourceKey"] = newResourceKey
#                         setValue["subComments"] = subComments
#                 if out.has_key("subs"):
#                     subs = out["subs"]
#                     if(subs!=None and len(subs)>0):
#                         for sub in subs:
#                             sub["resourceKey"] = newResourceKey
#                         setValue["subs"] = subs
                        
                db.userResource.update({"_id":id}, {"$set":setValue})
                
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
