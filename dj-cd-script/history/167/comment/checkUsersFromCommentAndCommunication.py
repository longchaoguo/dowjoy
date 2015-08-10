#!/usr/bin/python
#encoding=utf-8
'''
Created on 2015年05月22日

@author: qiu.zhong@downjoy.com

注：
    临时统计用户乐号脚本，只执行一次 2015年5月22日15:13:05
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

reload(sys)
sys.setdefaultencoding('utf-8')

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment
db2 = connection.communication

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"临时统计用户乐号脚本错误信息（dailyStatResCommentHot.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

def main():
    #每日集赞
    try:
        statUsersFromResourceComment()
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
     
    #每日交互  
    try:    
        statUsersFromCommUserFeed()
    except Exception:
        fp = StringIO.StringIO()    
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG 
     


def statUsersFromResourceComment():
    condition = {}

    mapfun = Code("function () {emit(this.user, 1)}")
    reducefun = Code("function (key, values) {"
                     "  var total = 0;"
                     "  for (var i = 0; i < values.length; i++) {"
                     "    total += values[i];"
                     "  }"
                     "  return total;"
                     "}")

    result = db.resourceComment.map_reduce(mapfun, reducefun, "tmp_mr_stat_activeUsersOfResourceComment", query=condition)

    file_object = open('statUsersFromResourceComment.txt', 'w')
    try:
        for doc in result.find().sort("value",pymongo.DESCENDING):
            userId = doc["_id"]
            try:
                userId = long(userId)
            except Exception:
                continue
            file_object.write(str(userId)+"\n")
    
    except Exception:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
    finally:   
        if file_object: 
            file_object.write("==end===\n")
            file_object.close( )


def statUsersFromCommUserFeed():
    file_object = open('statUsersFromCommUserFeed.txt', 'w')
    try:
        for out in db2.comm_user_feed.find({},{"_id":1}):
            userId = out["_id"]
            try:
                userId = long(userId)
            except Exception:
                continue
            file_object.write(str(userId)+"\n")
    except Exception:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
    finally:   
        if file_object: 
            file_object.write("==end===\n")
            file_object.close( )

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

