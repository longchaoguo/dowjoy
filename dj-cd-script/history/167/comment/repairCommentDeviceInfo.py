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
mailSubject = u"评论系统修复机型信息，（repairCommentDeviceInfo.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

def main():
    deviceMap = getAllDeviceInfo()
    for out in db.resourceComment.find({},{"device":1, "subComments":1}).batch_size(10000):
        id = out["_id"]
        if out.has_key("device"):
            device = deviceMap.get(out["device"])
            if(device!=None):
                db.resourceComment.update({"_id":id}, {"$set":{"device":device}})
        if out.has_key("subComments"):
            needModify = False
            subComments = out["subComments"]
            if(subComments!=None and len(subComments)>0):
                for subComment in subComments:
                    if subComment.has_key("device"):
                        subDevice = deviceMap.get(subComment["device"])
                        if(subDevice!=None):
                            subComment["device"] = subDevice
                            needModify = True
            if needModify:
                db.resourceComment.update({"_id":id}, {"$set":{"subComments":subComments}})

def getAllDeviceInfo():
    sql="SELECT MODEL_SERIAL,DISPLAY_NAME FROM MODEL WHERE MODEL_SERIAL IS NOT NULL AND MODEL_SERIAL<>'' "
    deviceMap = {}
    cursor.execute(sql)
    for row in cursor.fetchall():
        model_serial = str(row[0])
        if(model_serial.find(",")>0):
            mss = model_serial.split(",")
            for ms in mss:
                tmp = str(ms)
                deviceMap[tmp.strip()] = row[1]
        else:
            deviceMap[model_serial] = row[1]
    return deviceMap

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
