#!/usr/bin/python
#encoding=utf-8
'''
Created on 2015年03月30日

@author: qiu.zhong@downjoy.com

因资源合并需求，修复对应resourceComment集合中的合并资源的评论到主资源
注意：favCount使用inc而不是set，避免数据混乱
'''
import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO
import json
from djutil.MailUtil import MailUtil

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.communication

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"评论系统resourceComment集合合并评论到主资源，并更新resourceInfo集合commentCount和firstCommentCount字段（repairResourceCommentForResourceCombind.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

resId=52070#52070
resType=1

def main():
    file_object = open('thefile.txt', 'r')
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close( )
    users = json.loads(all_the_text)
    for user in users:
        id = user["uid"]
        ex = db.comm_user_feed.find_one({"_id":id, "favorites.id":resId, "favorites.resType":1})
        if not ex:
            db.comm_user_feed.update({"_id":id}, {"$push":{"favorites":user["favorites"]}, "$inc":{"favCount":1}})
        

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
