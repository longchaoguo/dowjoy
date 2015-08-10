#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#每天统计地瓜访问日志，操作表DIGUA_STAT_TEMP_LOG
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
OS_ID_LIST={}
RESOLUTION_ID_LIST={}
RESOLUTION_NAME_LIST={}
CHANNEL_NAME_LIST={}
#获取日志产生时间
handledate = None
BLACKLIST_NUM_LIST = {}
pattern = re.compile("\[(?P<TIME>\S*) \S*\] \S* (?P<URL>\S*) \S* (?P<IP>\S*), \S* (?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {(?P<HEAD>.+)}")
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"地瓜统计日志统计错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate, createdDate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%y%m%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%y%m%d")
    createdDate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%Y-%m-%d")
    sql = "select num from DIGUA_USER_NUM_BLACKLIST group by num"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        BLACKLIST_NUM_LIST[row]=1

    sql = "select ID, NAME from OS where status=1"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        OS_ID_LIST[row[1]]=str(row[0])
    OS_ID_LIST["4.3"]="17"
    OS_ID_LIST["4.4"]="18"
    sql = "SELECT ID, NAME, WIDTH, HEIGHT FROM RESOLUTION"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        RESOLUTION_ID_LIST[str(row[2])+"*"+str(row[3])]=str(row[0])
        RESOLUTION_NAME_LIST[str(row[2])+"*"+str(row[3])]=row[1]
        RESOLUTION_ID_LIST[str(row[3])+"*"+str(row[2])]=str(row[0])
        RESOLUTION_NAME_LIST[str(row[3])+"*"+str(row[2])]=row[1]
    sql = "SELECT ID, NAME FROM CLIENT_CHANNEL"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        CHANNEL_NAME_LIST[str(row[0])]=row[1]

def getResolution(resolutionKey, resolutionWidth):
    i = -1
    for k, v in RESOLUTION_NAME_LIST.items():
        keyarry = k.split("*")
        tempAbs = abs(resolutionWidth-int(keyarry[0]))
        if i == -1 or tempAbs<i:
            i = tempAbs
            RESOLUTION_ID_LIST[resolutionKey]=RESOLUTION_ID_LIST[k]
            RESOLUTION_NAME_LIST[resolutionKey]=v


def insertData(dbUtil, sql, dataList):
    #print "insertData start....."
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

#将日志入库
def statFile(fileName):
    # 如果该文件不存在，抛出异常
    if os.path.exists(fileName):
        f = open(fileName, 'rb')
        sql = "insert into DIGUA_STAT_USER_LOG_TEMP_APACHE_0930 (IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        dataList = []
        while True:
            line = f.readline()
            #print line
            if not line:
                break
            match = pattern.match(line)
            if not match:
                #print line
                continue
            status = match.group('STATUS')
            if not status in ['200', '206']:
                continue
            timestr = (match.group("TIME"))[12:20]
            ip = match.group("IP")
            headStr = "{"+match.group("HEAD").replace("\\", "")+"}"
            #print headStr
            try:

                headDict = eval(headStr)
                #print headDict['num']
                num = ""
                if headDict.has_key("num"):
                    num = headDict['num']
                if headDict.has_key("mac"):
                    #print"==========6.9==============="
                    num = headDict['mac']
                num = num.replace("+86", "")
                num = num.replace("Unknown", "")
                if len(num)>20 or num == 'null' or num == '0':
                    num = ''
                if num == '15555215554':
                    #print "BLACKLIST_NUM_LIST"
                    continue
                imei = headDict['imei']
                if len(imei)<14 or len(imei)>18 or imei == '000000000000000':
                    continue
                clientChannelId = headDict['clientChannelId']
                if len(clientChannelId) == 0:
                    continue
                clientChannelName = CHANNEL_NAME_LIST[headDict['clientChannelId']]
                if len(clientChannelName) == 0:
                    continue

                resolutionKey = str(headDict["resolutionWidth"])+"*"+str(headDict["resolutionHeight"])
                if not RESOLUTION_ID_LIST.has_key(resolutionKey):
                    getResolution(resolutionKey, headDict["resolutionWidth"])
                resolutionId = RESOLUTION_ID_LIST[resolutionKey]
                resolutionName = RESOLUTION_NAME_LIST[resolutionKey]

                osName = headDict['osName'].replace("Android_", "").replace("Android ", "").replace("-update1", "")
                if len(osName)>20:
                    osName = osName[:19]
                osId = "4"
                osNameArray = osName.split(".")

                if osName!='2.0.1' and osName!='4.0.3' and len(osNameArray)>=3:
                    osName = osNameArray[0]+"."+osNameArray[1]
                if OS_ID_LIST.has_key(osName):
                    osId = OS_ID_LIST[osName]
                versionStr = headDict['version']
                device = headDict['device']
                it = headDict['it']
                if it != '1' and it != '2':
                    it = '3'
                #print "imei=%s, ip=%s, resolutionId=%s, resolutionName=%s, osId=%s, osName=%s, versionStr=%s, clientChannelId=%s, clientChannelName=%s, device=%s, num=%s, createdDate=%s"%(imei, ip, resolutionId, resolutionName, osId, osName, versionStr, clientChannelId, clientChannelName, device, num, createdDate)
                dataList.append((imei, ip, resolutionId, resolutionName, osId, osName, versionStr, clientChannelId, clientChannelName, device, num, it, createdDate +" "+ timestr))
                headDict.clear()

            except:
                continue
            if len(dataList) >= 1000:
                #print len(dataList)
                insertData(dbUtil_168, sql, dataList)
                dataList = []
        if dataList:
            insertData(dbUtil_168, sql, dataList)
            dataList = []
        f.close()
        #fw.close()

def handleFtpFile():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (73,74,75,118,173,174,175,176) order by ID;"
    #sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (74,75,118) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] + localFile)
        print localFile, 'over'


def clearData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP_APACHE"
    dbUtil_168.truncate(sql1, ())

def insertUserDailyLogs():
    sql = "select imei, count(ID) from  DIGUA_STAT_USER_LOG_TEMP_APACHE group by imei"
    rows = dbUtil_168.queryList(sql, ())
    dataList = []
    insertsql = "INSERT INTO DIGUA_STAT_USER_LOG_DAILY_APACHE (IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE, PV) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for row in rows:
        if not row:
            continue
        sql = "select IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE from DIGUA_STAT_USER_LOG_TEMP_APACHE where imei=%s order by created_date limit 1"
        rs = dbUtil_168.queryRow(sql, (row[0]))

        #print "imei=%s, ip=%s, resolutionId=%s, resolutionName=%s, osId=%s, osName=%s, versionStr=%s, clientChannelId=%s, clientChannelName=%s, device=%s, num=%s, createdDate=%s"%(imei, ip, resolutionId, resolutionName, osId, osName, versionStr, clientChannelId, clientChannelName, device, num, createdDate)
        dataList.append((row[0], rs[0], rs[1], rs[2], rs[3], rs[4], rs[5], rs[6], rs[7], rs[8], rs[9], rs[10], rs[11],  row[1]))

        if len(dataList) >= 1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

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
#        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
        #insertTempUserDailyLogs()
        print "stat file over %s"% datetime.datetime.now()
#        insertUserDailyLogs()
        print "insert user daily data over"
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()
        #if ERROR_MSG:
            #sendMail()
    print "=================end   %s======" % datetime.datetime.now()


