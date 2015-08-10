#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.12 $"
__date__ = "$Date: 2013/09/27 09:09:22 $"
###########################################
#统计每天网游下载量数据
###########################################
import os
import sys
import time
import datetime
import ftplib
import StringIO
import traceback
import simplejson
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_168 = DBUtil('download_stat_168')
dbUtil_stat_168 = DBUtil('droid_stat_168')
#获取日志产生时间
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
#新版地瓜日志存放目录
username = "ftpdownjoy"
password = "djftp119"
localDir = "/opt/logs/addownlog/"
NETGAME_RESOURCE_TYPE = 5
WEB_CHANNEL_FLAG = 10
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"安卓主站网游下载量统计错误信息".encode("gbk")
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

#FTP下载日志文件
def getFile(srcDir, srcFile, localDir, localFile, ip, port):
    print localDir
    if not os.path.exists(localDir):
        os.makedirs(localDir)
    rs = FtpUtil.getFile(srcDir, srcFile, localDir, localFile, ip, port, username, password)
    #if not rs:
        #raise Exception, "ftp error: %s %s!" % (ip, srcFile)

def insertDataToLog(dbUtil, sql, dataList):
    #print sql
    #print dataList
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

#日志入库
def statFile(localDir, localFile, channelFlag):
    fileName=localDir+localFile
    #if not os.path.exists(fileName):
    #os.system('tar -zxvf %sbak/%s.tar.gz -C %s'%(localDir,localFile,localDir))
    # 如果该文件不存在，抛出异常
    if os.path.exists(fileName):
        f = open(fileName, 'rb')
        sql = "insert into ANDROID_NETGAME_DOWNLOAD_LOG (CHANNEL_ID, PKG_ID, RESOURCE_TYPE, CHANNEL_FLAG, CREATED_DATE, IP) values (%s, %s, %s, %s, %s, %s)"
        dataList = []
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            array = line.split('|')
            if len(array) != 5:
                continue
            resourceType = array[2]
            createdDate = array[3]
            ip = array[4].strip()
            #print "resourceType=%s"%(resourceType)
            if int(resourceType) == 5:
                try:
                    dataList.append((int(array[0]), int(array[1]), int(resourceType), channelFlag, createdDate, ip))
                except:
                    continue
                if len(dataList) >= 1000:
                    insertDataToLog(dbUtil_168, sql, dataList)
                    dataList = []
        if dataList:
            insertDataToLog(dbUtil_168, sql, dataList)
            dataList = []
        f.close()

def handleFtpFile():
    sql="select ID, SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where ID in (6,7,8,9,10,11,12,13,14,15,16,17,97,98,99,100) order by ID;"
    rows = dbUtil_stat_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        localDir=row[3]
        localFile=row[4]%(handledate)
        if row[0] == 6 or row[0] == 7 or row[0] == 8 or row[0] == 97:#web
            statFile(localDir, localFile, 10)
        if row[0] == 9 or row[0] == 10 or row[0] == 11 or row[0] == 98:#360
            statFile(localDir, localFile, 50)
        if row[0] == 12 or row[0] == 13 or row[0] == 14 or row[0] == 99:#豌豆荚
            statFile(localDir, localFile, 70)
        if row[0] == 15 or row[0] == 16 or row[0] == 17 or row[0] == 100:#腾讯
            statFile(localDir, localFile, 100)
        print localFile, 'over'
        time.sleep(1)

def clearData():
    nextDate = datetime.datetime.strftime(datetime.datetime.strptime(handledate, '%Y-%m-%d') + datetime.timedelta(days = 0), '%Y-%m-%d')
    sql1 = "delete from ANDROID_NETGAME_DOWNLOAD_LOG where CREATED_DATE >=%s and CREATED_DATE < %s and CHANNEL_FLAG in (10,20,50,70,100)"
    dbUtil_168.delete(sql1, (handledate, nextDate))

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
        '''WEB_FILE_LIST = [
               ['', "android.netgame.downs.%s.txt" % (handledate), localDir, "155_android.netgame.downs.%s.txt" % (handledate), '211.147.5.155', 21, 10, None],
               ['', "android.netgame.downs.%s.txt" % (handledate), localDir, "167_android.netgame.downs.%s.txt" % (handledate), '211.147.5.167', 21, 10, None],
               ['', "android.netgame.downs.%s.txt" % (handledate), localDir, "135_android.netgame.downs.%s.txt" % (handledate), '211.147.5.135', 21, 10, None],
               #360#
               ['', "android.qihu.downs.%s.txt" % (handledate), localDir, "155_android.qihu.downs.%s.txt" % (handledate), '211.147.5.155', 21, 50, None],
               ['', "android.qihu.downs.%s.txt" % (handledate), localDir, "167_android.qihu.downs.%s.txt" % (handledate), '211.147.5.167', 21, 50, None],
               ['', "android.qihu.downs.%s.txt" % (handledate), localDir, "135_android.qihu.downs.%s.txt" % (handledate), '211.147.5.135', 21, 50, None],
               #豌豆荚#
               ['', "android.wdj.downs.%s.txt" % (handledate), localDir, "155_android.wdj.downs.%s.txt" % (handledate), '211.147.5.155', 21, 70, None],
               ['', "android.wdj.downs.%s.txt" % (handledate), localDir, "167_android.wdj.downs.%s.txt" % (handledate), '211.147.5.167', 21, 70, None],
               ['', "android.wdj.downs.%s.txt" % (handledate), localDir, "135_android.wdj.downs.%s.txt" % (handledate), '211.147.5.135', 21, 70, None],
               #腾讯#
               ['', "android.tencent.downs.%s.txt" % (handledate), localDir, "155_android.tencent.downs.%s.txt" % (handledate), '211.147.5.155', 21, 100, None],
               ['', "android.tencent.downs.%s.txt" % (handledate), localDir, "167_android.tencent.downs.%s.txt" % (handledate), '211.147.5.167', 21, 100, None],
               ['', "android.tencent.downs.%s.txt" % (handledate), localDir, "135_android.tencent.downs.%s.txt" % (handledate), '211.147.5.135', 21, 100, None],
          ]'''

        #清理数据
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_stat_168 : dbUtil_stat_168 .close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()


