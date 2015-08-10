#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#地瓜内嵌页统计
###########################################
import os
import sys
import time
import datetime
import ftplib
import StringIO
import traceback
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
#获取日志产生时间
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
#日志存放目录
username = "ftpdownjoy"
password = "djftp119"
#localDir="/usr/local/bin/stat/cdroid/66_144/pcdiguaweb/"
IP_PCWEB_DOWN_DATE={}
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
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
    if not rs:
        raise Exception, "ftp error: %s %s!" % (ip, srcFile)

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

#将web\wap日志入库
def statFile(fileName):
        
    f = open(fileName, 'rb')
    sql = "insert into DIGUA_PCWEB_DOWN_LOG (RESOURCE_TYPE, PKG_ID, CHANNEL_FLAG, IP, CREATED_DATE) values (%s, %s, %s, %s, %s)"
    dataList = []
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        #print line
        array = line.split('@!@')
        '''下载时间、资源ID、包ID、资源类型(1:单机, 2:软件, 5:网游)、IP'''
        if len(array) != 5 or int(array[1]) == 7446:
            continue
        createdDate = array[0]
        print createdDate
        resourceType = array[1]
        pkgId = array[2]
        channelFlag = array[3]
        ip=array[4]
        if not isRepeatingData(ip, channelFlag, pkgId, resourceType, createdDate):
            try:
                dataList.append((resourceType, pkgId, channelFlag, ip, createdDate))
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
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in(145,146,147,148,202,222) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        if not os.path.exists(row[2]+localFile):
            continue
        statFile(row[2] + localFile)
        print localFile, 'over'

def clearData():
    nextDate = datetime.datetime.strftime(datetime.datetime.strptime(handledate, '%Y-%m-%d') + datetime.timedelta(days = 1), '%Y-%m-%d')
    sql1 = "delete from DIGUA_PCWEB_DOWN_LOG where CREATED_DATE >=%s and CREATED_DATE < %s"
    dbUtil_168.delete(sql1, (handledate, nextDate))

def isRepeatingData(ip, channelFlag, pkgId, resourceType, createdDate):
    key = ip+"@_@"+channelFlag+"@_@"+pkgId+"@_@"+resourceType
    if not IP_PCWEB_DOWN_DATE.has_key(key):
        IP_PCWEB_DOWN_DATE[key] = createdDate
        return False
    if repeatingDataOutTime(key, createdDate):
        IP_PCWEB_DOWN_DATE[key] = createdDate
        return False
    return True
def repeatingDataOutTime(key, createdDate):
    print createdDate
    diffTime = (datetime.datetime.strptime(createdDate, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(IP_PCWEB_DOWN_DATE[key], '%Y-%m-%d %H:%M:%S')).seconds
    if diffTime > 600 :
        return True
    else :
        return False



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
        #清理数据
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
        #statFile(localDir+"pcdiguaweb_downs.log.2013-11-03")

    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        #if ERROR_MSG:
            #sendMail()
    print "=================end   %s======" % datetime.datetime.now()


