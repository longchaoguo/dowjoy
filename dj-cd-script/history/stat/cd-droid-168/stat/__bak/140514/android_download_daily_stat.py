#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.12 $"
__date__ = "$Date: 2013/01/22 09:09:22 $"
###########################################
#每天统计WEB\WAP\地瓜数据，操作表ANDROID_GAME_DOWNLOAD_LOG、ANDROID_GAME_DOWNLOAD_HISTORY
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
dbUtil_10 = DBUtil('droid_game_10')
dbUtil_168 = DBUtil('download_stat_168')
dbUtil_stat_168 = DBUtil('droid_stat_168')
#获取日志产生时间
handledate = None
#初始化参数
GAME_RESOURCE_TYPE = 1
SOFTWARE_RESOURCE_TYPE = 2
WEB_CHANNEL_FLAG = 10
ID_DICT = {}
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"安卓主站下载量统计错误信息".encode("gbk")
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

def initIdDictForResId(): # 获取资源类型
    sql = 'select g.ID, gc.RESOURCE_TYPE from GAME g inner join GAME_CATEGORY gc on gc.ID=g.GAME_CATEGORY_ID '
    rows = dbUtil_10.queryList(sql, ())
    if not rows: return
    for row in rows:
        ID_DICT[int(row[0])] = int(row[1])

def insertDataToLog(dbUtil, sql, dataList): #批量插入数据
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

#将web日志入库
def statFileForWeb(fileName):
    # 如果该文件不存在，抛出异常
    if not os.path.exists(fileName):
        raise Exception, 'can not find file: %s' % fileName
    f = open(fileName, 'rb')
    sql = "insert into ANDROID_GAME_DOWNLOAD_LOG (GAME_ID, PKG_ID, RESOURCE_TYPE, CHANNEL_FLAG, CREATED_DATE, IP) values (%s, %s, %s, %s, %s, %s)"
    dataList = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        array = line.split('|')
        if len(array) < 4:
            continue
        resourceType = GAME_RESOURCE_TYPE
        createdDate = array[2]
        ip = array[3]
        if len(array) == 5:
            resourceType = array[2]
            createdDate = array[3]
            ip = array[4].strip()
        try:
            dataList.append((int(array[0]), int(array[1]), int(resourceType), WEB_CHANNEL_FLAG, createdDate, ip))
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
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (19,20,21,123) order by ID;"
    rows = dbUtil_stat_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        #clearData()
        #statFile(row[2] + localFile)
        statFileForWeb(row[2] + localFile)
        print localFile, 'over'

def clearData():
    nextDate = datetime.datetime.strftime(datetime.datetime.strptime(handledate, '%Y-%m-%d') + datetime.timedelta(days = 1), '%Y-%m-%d')
    sql1 = "delete from ANDROID_GAME_DOWNLOAD_LOG where CREATED_DATE >=%s and CREATED_DATE < %s and CHANNEL_FLAG in (10,20)"
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
        '''
        WEB_FILE_LIST = [
               ['', "android.downs.%s.txt" % (handledate), localDir, "155_android.downs.%s.txt" % (handledate), '211.147.5.155', 21, 10, None],
               ['', "android.downs.%s.txt" % (handledate), localDir, "167_android.downs.%s.txt" % (handledate), '211.147.5.167', 21, 10, None],
               ['', "android.downs.%s.txt" % (handledate), localDir, "135_android.downs.%s.txt" % (handledate), '211.147.5.135', 21, 10, None],
          ]
        WAP_FILE_LIST = [
               ['download/', 'download2.%s.txt' % (handledate), localDir, '135_download2.%s.txt' % (handledate), '211.147.5.135', 21, 20, None],
               ['download/', 'download2.%s.txt' % (handledate), localDir, '155_download2.%s.txt' % (handledate), '211.147.5.155', 21, 20, None],
               ['download/', 'download2.%s.txt' % (handledate), localDir, '167_download2.%s.txt' % (handledate), '211.147.5.167', 21, 20, None]
                       ]
        '''
        #清理数据
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        initIdDictForResId()
        handleFtpFile()
        #handleFtpFile('wap')
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()
        if dbUtil_stat_168: dbUtil_stat_168.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()


