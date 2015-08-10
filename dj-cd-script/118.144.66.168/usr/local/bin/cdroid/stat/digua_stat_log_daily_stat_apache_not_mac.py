#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#ÿ��ͳ�ƵعϷ�����־��������DIGUA_STAT_TEMP_LOG
###########################################
import os
import sys
import time
import datetime
import ftplib
import StringIO
import traceback
import re
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_10=DBUtil('droid_game_10')
#��ȡ��־����ʱ��
handledate = None
#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"�ع�ͳ����־ͳ�ƴ�����Ϣ".encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%y%m%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%y%m%d")

def insertData(dbUtil, sql, dataList):
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

def clearData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP_APACHE_NOT_MAC"
    dbUtil_168.truncate(sql1, ())
    sql1 = "truncate DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
    dbUtil_168.truncate(sql1, ())
def insertDailyLogs():
    sql = "insert into DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC select * from DIGUA_STAT_USER_LOG_DAILY_APACHE"
    dbUtil_168.insert(sql,())


def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        init()
        clearData()
        print 'clear data over'
        insertDailyLogs()
        print "insert user daily data over"
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()


