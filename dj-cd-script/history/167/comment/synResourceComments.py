#!/usr/bin/python
# -*- coding: cp936 -*-
__author__ = 'sgq'
'''
每天定时同步资源的评论数
'''

import pymongo
import time
import datetime
import MySQLdb
import traceback
import StringIO
from bson.code import Code

from djutil.MailUtil import MailUtil

connection = pymongo.MongoClient('192.168.0.72',27017)
db = connection.comment

mysql = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
cursor = mysql.cursor()

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"每天定时同步资源的评论数".encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
COMMENTS={}
def loadResourceComments():
    map = Code("function () {emit(this.resourceKey, 1)}")
    reduce = Code('''function (key, values) {
                       var total = 0;
                       for (var i = 0; i < values.length; i++) {
                         total += values[i];
                       }
                      return total;
                     }''')
    result = db.resourceComment.map_reduce(map, reduce, "tmp_stat_resourceComments")
    loop = 0
    global COMMENTS
    for r in result.find().sort("value",pymongo.DESCENDING):
        try:
            COMMENTS[r['_id']]=r['value']
        except Exception:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print ERROR_MSG




def updateResourceComments():
    keys = COMMENTS.keys()
    net_game_sql = "update NETGAME_CHANNEL set comments=%s where id=%s"
    game_data_list=[]
    game_sql = "update GAME set comments=%s where CHANNEL_ID=%s and RESOURCE_TYPE=%s"
    net_game_list=[]
    for key in keys:
        if not  key:
            continue
        id = key.split(":")[0]
        type = key.split(":")[1]
        if type=='5':
            net_game_list.append((COMMENTS[key],id))
        else:
            game_data_list.append((COMMENTS[key],id,type))
    cursor.executemany(game_sql,game_data_list)
    cursor.executemany(net_game_sql,net_game_list)
    mysql.commit()
def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

###############################################################
if __name__ == '__main__':
    try:
        loadResourceComments()
        updateResourceComments()
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
