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
import urllib
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_187 = DBUtil('droid_stat_187')
#��ȡ��־����ʱ��
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"�ع�ͳ����־ͳ�ƴ�����Ϣ".encode("gbk")
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

def insertDataToLog(dbUtil, sql, dataList):
    #print "insertDataToLog start....."
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

#����־���
def statFile(fileName):
    # ������ļ������ڣ��׳��쳣
    if not os.path.exists(fileName):
        raise Exception, 'can not find file: %s' % fileName
    f = open(fileName, 'rb')
    sql = "insert into DIGUA_PCWEB_PV_URL(NAME, url) values (%s, %s)"
    dataList = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        array = line.split('@!@')
        if len(array) != 4:
            continue
        #2013-11-06 00:02:05@!@get@!@/dir/ngchannel/recommand@!@{"resolutionWidth":720,"resolutionHeight":1280,"osName":"4.1.1","version":"6.4.2","clientChannelId":"100351","device":"MI_2","imei":"869630018310593","hasRoot":"true","num":"","sdk":16,"ss":2,"sswdp":360,"dd":320,"it":"2","verifyCode":"e6c66170933583c8f03d053cb3dc3867"}
        keywordstr = urllib.unquote(array[2].replace("/dir/search/", ""))
        try:
            dataList.append((keywordstr, array[2]))
        except:
            continue
        if len(dataList) >= 1000:
            insertDataToLog(dbUtil_187, sql, dataList)
            dataList = []
    if dataList:
        insertDataToLog(dbUtil_187, sql, dataList)
        dataList = []
    f.close()

def handleFtpFile():
    statFile("/usr/local/logs/cdroid/135/client_350/search.txt")
    statFile("/usr/local/logs/cdroid/155/client_350/search.txt")
    statFile("/usr/local/logs/cdroid/167/client_350/search.txt")

def clearData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP"
    dbUtil_187.truncate(sql1, ())

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
        #��������
        #clearData()
        print 'clear data over'
        #FTP��ȡ��־�ļ������������ݲ���
        handleFtpFile()
        #insertUserLogs()
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_187: dbUtil_187.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()


