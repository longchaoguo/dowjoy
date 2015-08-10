#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#每天统计地瓜用户留存。
###########################################
import os
import sys
import time
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
#初始化参数
dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_111 = DBUtil('droid_stat_111')

handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"地瓜用户留存错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    date=time.strptime(fileDate, "%Y-%m-%d")
    date=datetime.datetime(date[0],date[1],date[2])

def loadDiguaUser():
    #15675732
    sql = "select IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where ID>10000000 and id<=15675732"
    rows = dbUtil_111.queryList(sql, ())
    insertsql = "insert into DIGUA_USER(IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, CREATED_DATE) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dataList = []
    for row in rows:
        if not row:
            continue
        try:
            dataList.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
        except:
            continue
        if len(dataList) >= 1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

def insertData(dbUtil, sql, dataList):
    #print "insertDataToLog start....."
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        init()
        loadDiguaUser()
        

    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_111: dbUtil_111.close()
        #if ERROR_MSG:
            #sendMail()
    print "=================end   %s======" % datetime.datetime.now()


