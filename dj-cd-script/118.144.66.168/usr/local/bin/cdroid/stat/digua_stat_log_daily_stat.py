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
import base64
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
mailLoginPass = "htbp3dQ1sGcco!q"
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
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), '%Y-%m-%d')
    print handledate
    #createdDate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%Y-%m-%d")
    sql = "select num from DIGUA_USER_NUM_BLACKLIST group by num"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        BLACKLIST_NUM_LIST[row]=1

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
def statFile(fileName, isNew):
    # 如果该文件不存在，抛出异常
    if os.path.exists(fileName):
        f = open(fileName, 'rb')
        sql = "insert into DIGUA_STAT_USER_LOG_TEMP (IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        dataList = []
        while True:
            line = f.readline()
            if not line:
                break
            rows=line.split("|")
            #print len(rows)
            if len(rows) != 13 and len(rows) != 14:
                continue
            #[2014-08-01 23:59:59] 358584055339551||117.27.184.97|14|1024*480|17|4.3|6.8.2|100380|???|SM-N9008V|2|/misc/newsevermessages
            # IMEI|NUM|IP|RESOLUTION_ID|RESOLUTION_NAME|OS_ID|OS_NAME|VERSION|CLIENT_CHANNEL_ID|CLIENT_CHANNEL_NAME|DEVICE|it
            timesList=rows[0].split("]")
            timeStr=handledate+timesList[0][11:]
            imei=timesList[1][1:]
            if imei==None or len(imei)==0 or len(imei)<15 or len(imei)>18:
                continue
            num=rows[1]
            if isNew and len(rows) == 13:
                num=base64.decodestring(num[:len(num)-16])
            num = num.replace("+86", "")
            num = num.replace("monitor", "").replace("Unknown",'')
            if len(rows)  == 14:
                num = rows[12]
            if len(num)>20 or num == 'null' or num == '0':
                num = ''
            if BLACKLIST_NUM_LIST.has_key(num) or num == '15555215554':
                #print "BLACKLIST_NUM_LIST"
                continue
            ips=rows[2].split(',')
            ip=ips[0]
            resolutionId=rows[3]
            if resolutionId==None or len(resolutionId)==0:
                continue
            resolutionName=rows[4]
            osId=rows[5]
            osName=rows[6]
            versionStr=rows[7]
            clientChannelId=rows[8]
            clientChannelName=rows[9].decode("gbk").encode("utf-8")
            device=rows[10]
            it=rows[11]
            dataList.append((imei, ip, resolutionId, resolutionName, osId, osName, versionStr, clientChannelId, clientChannelName, device, num, it, timeStr))
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
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (165,166, 167,168,206,226) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        #srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] + localFile, False)
        print localFile, 'over'

def newHandleFtpFile():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (169,170,171,172,207,227) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        #srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] + localFile, True)
        print localFile, 'over'



def clearData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP"
    dbUtil_168.truncate(sql1, ())

def insertUserDailyLogs():
    sql = "select imei, count(ID) from  DIGUA_STAT_USER_LOG_TEMP group by imei"
    rows = dbUtil_168.queryList(sql, ())
    dataList = []
    insertsql = "INSERT INTO DIGUA_STAT_USER_LOG_DAILY (IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE, PV) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for row in rows:
        if not row:
            continue
        sql = "select IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, IT, CREATED_DATE from DIGUA_STAT_USER_LOG_TEMP where imei=%s order by created_date limit 1"
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
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
        newHandleFtpFile()
        #insertTempUserDailyLogs()
        print "stat file over %s"% datetime.datetime.now()
        insertUserDailyLogs()
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


