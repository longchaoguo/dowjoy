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
dbUtil_187 = DBUtil('download_stat_187')
dbUtil_10=DBUtil('droid_game_10')
#获取日志产生时间
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
#2013-11-06 00:02:05@!@get@!@/dir/ngchannel/recommand@!@{"resolutionWidth":720,"resolutionHeight":1280,"osName":"4.1.1","version":"6.4.2","clientChannelId":"100351","device":"MI_2","imei":"869630018310593","hasRoot":"true","num":"","sdk":16,"ss":2,"sswdp":360,"dd":320,"it":"2","verifyCode":"e6c66170933583c8f03d053cb3dc3867"
#pattern = re.compile("(?P<TIME>\S{10} \S{8}).+clientChannelId\":\"(?P<CHANNEL_ID>\d+).+imei\":\"(?P<IMEI>\w+\_?\w+)")
#pattern1 = re.compile("(?P<TIME>\S{10} \S{8}).+imei\":\"(?P<IMEI>\w+\_?\w*).+clientChannelId\":\"(?P<CHANNEL_ID>\d+)")
channelPattern = re.compile(".+clientChannelId\":\"(?P<CHANNEL_ID>\d+)\"")
imeiPattern = re.compile(".+imei\":\"(?P<IMEI>\w*\_?\w*)\"")
numPattern = re.compile(".+num\":\"(?P<NUM>15555215554)\"")

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
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")

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
        print fileName
        sql = "insert into DIGUA_STAT_USER_LOG_TEMP(CLIENT_CHANNEL_ID, IMEI, VERSION, CREATED_DATE) values (%s, %s, %s, %s)"
        #sql_a="insert into CLIENT_DAILY_STAT_TEMP(IMEI, IP, RESOLUTION_ID, OS_ID, VERSION, CLIENT_CHANNEL_ID, DEVICE, CREATED_DATE,
        # EVENT_TYPE, RESOLUTION_NAME, OS_NAME, CLIENT_CHANNEL_NAME, INSTALL_TYPE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #fw = open("/usr/local/bin/cdroid/temp/digua_stat_not_match.txt", 'wb')
        dataList = []
        while True:
            line = f.readline()
            if not line:
                break
            #print line
            array = line.split('|')
            '''if len(array) != 4:
                continue
            headStr = array[3].strip()
            if headStr == 'null':
                continue
            createdDate = array[0]
            #正则
            #2013-11-06 00:02:05@!@get@!@/dir/ngchannel/recommand@!@{"resolutionWidth":720,"resolutionHeight":1280,"osName":"4.1.1","version":"6.4.2","clientChannelId":"100351","device":"MI_2","imei":"869630018310593","hasRoot":"true","num":"","sdk":16,"ss":2,"sswdp":360,"dd":320,"it":"2","verifyCode":"e6c66170933583c8f03d053cb3dc3867"}
            numMatch = numPattern.match(headStr)
            if numMatch:
                continue
            '''
            clientChannelId = ''
            imei = ''
            versionStr = ''
            try:
                createdDate = array[7]
                clientChannelId = array[5]
                versionStr = array[4]
                imei = array[0]
            except:
                continue
            if len(clientChannelId) == 0 or len(imei) == 0 or len(imei) > 20:
                continue
            '''
            #json
            headArray = array[3].replace("{", "").replace("}", "").split(",")
            headDict = {}
            for headstr in headArray:
                element = headstr.split('":')
                if len(element) > 1:
                    headDict[element[0].replace('"', '')]=element[1].replace('"', '')
            if not headDict.has_key("clientChannelId") or not headDict.has_key("imei"):
                #fw.write(line)
                continue
            clientChannelId = headDict["clientChannelId"]
            imei = headDict["imei"]
            '''
            try:
                dataList.append((clientChannelId, imei, versionStr, createdDate))
            except:
                continue
            if len(dataList) >= 1000:
                insertData(dbUtil_187, sql, dataList)
                dataList = []
        if dataList:
            insertData(dbUtil_187, sql, dataList)
            dataList = []
        f.close()
        #fw.close()

def handleFtpFile():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (1, 2, 3) order by ID;"
    rows = dbUtil_187.queryList(sql, ())
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
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP"
    dbUtil_187.truncate(sql1, ())
    #sql1 = "delete from DIGUA_STAT_USER_LOG where datediff(%s,CREATED_DATE) = 0"
    #dbUtil_187.delete(sql1, (handledate))

def insertUserLogs():
    sql = "select T.imei, T.client_channel_id, ifnull(T.version, ''), count(*), T.created_date from (select imei, client_channel_id, version, created_date from DIGUA_STAT_USER_LOG_TEMP order by created_date) T group by T.imei"
    rows = dbUtil_187.queryList(sql, ())
    dataList = []
    insertsql = "INSERT INTO DIGUA_STAT_USER_LOG(IMEI, CLIENT_CHANNEL_ID, VERSION, PV, CREATED_DATE) values(%s, %s, %s, %s, %s)"
    for row in rows:
        if not row:
            continue
        try:
            dataList.append((row[0], row[1], row[2], row[3], row[4]))
        except:
            continue
        if len(dataList) >= 1000:
            insertData(dbUtil_187, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_187, insertsql, dataList)
        dataList = []


def process(datestr):
    clearData()
    statFile("/usr/local/logs/android.client.stat.%s.txt"%(datestr))
    insertUserLogs()

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        sql = "SELECT G.ID, G.NAME, G.VENDOR_ID, V.NAME FROM GAME G INNER JOIN VENDOR V ON G.VENDOR_ID=V.ID WHERE G.STATUS=1 AND V.STATUS=1"
        rows = dbUtil_10.queryList(sql, ())
        #print len(rows)
        for row in rows:
            sql = "update TEMP_STAT set VENDOR_ID=%s, VENDOR_NAME=%s, GAME_NAME=%s where GAME_ID=%s"
            dbUtil_187.update(sql, (row[2], row[3], row[1], row[0]))

        '''
        #init()
        #清理数据
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        #handleFtpFile()
        statFile("E://diguastat/diguastat_10temp/android.client.stat.%s.txt"%(handledate))
        insertUserLogs()
        '''
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_187: dbUtil_187.close()
        if dbUtil_10: dbUtil_10.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()


