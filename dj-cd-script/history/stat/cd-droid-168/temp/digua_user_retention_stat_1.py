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

handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
CHANNEL_RETENTIONS_CNT_TODAY={}
CHANNEL_RETENTIONS_CNT_1DAY={}
CHANNEL_RETENTIONS_CNT_7DAY={}
CHANNEL_RETENTIONS_CNT_30DAY={}
CHANNEL_RETENTIONS_RATE_1DAY={}
CHANNEL_RETENTIONS_RATE_7DAY={}
CHANNEL_RETENTIONS_RATE_30DAY={}
CHANNEL_NAME={}


CHANNEL_PV_DICT = {}
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
    global handledate, datetime1, datetime7, datetime30,createdDate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    createdDate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%y%m%d")
    date=time.strptime(fileDate, "%Y-%m-%d")
    date=datetime.datetime(date[0],date[1],date[2])
    datetime1 = datetime.datetime.strftime(date - datetime.timedelta(days = 1), "%Y-%m-%d")
    datetime7 = datetime.datetime.strftime(date - datetime.timedelta(days = 7), "%Y-%m-%d")
    datetime30 = datetime.datetime.strftime(date - datetime.timedelta(days = 30), "%Y-%m-%d")

def clearData():
    sql1 = "delete from DIGUA_STAT_USER_LOG where datediff(%s,CREATED_DATE) = 0"
    dbUtil_168.delete(sql1, (handledate))
    sql = "delete from DIGUA_USER where datediff(%s,CREATED_DATE) = 0"
    dbUtil_168.delete(sql, (handledate))
    sql = "delete from DIGUA_USER_RETENTION_STAT where datediff(%s,stat_date) = 0"
    dbUtil_168.delete(sql, (handledate))
    sql = "delete from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT where datediff(%s,stat_date) = 0"
    dbUtil_168.delete(sql, (handledate))

def clearRepeatedNumData():
    sql = "SELECT num, COUNT(imei) AS cnt FROM (SELECT num, imei FROM DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" WHERE LENGTH(num)>0 UNION ALL SELECT num, imei FROM DIGUA_USER WHERE LENGTH(num)>0 AND DATEDIFF(%s, created_date)<367 and DATEDIFF(%s, created_date)>0)T GROUP BY num having cnt>3"
    rows = dbUtil_168.queryList(sql, (handledate, handledate))
    for row in rows:
        try:
            sql = "delete from DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" where num=%s order by created_date desc limit %s"
            dbUtil_168.delete(sql, (row[0], int(row[1])-3))
            #dbUtil_168.insert("insert into DIGUA_USER_NUM_BLACKLIST(NUM) values(%s)", (row[0]))
        except:
            continue


def insertUserLog():
    sql = "insert into DIGUA_STAT_USER_LOG(IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV) select IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV from DIGUA_STAT_USER_LOG_DAILY_"+createdDate
    dbUtil_168.insert(sql, ())

def insertNewUser():
    sql = "SELECT IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE FROM DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" WHERE IMEI NOT IN (SELECT IMEI FROM DIGUA_USER where DATEDIFF(created_date, %s)<0)"
    rows = dbUtil_168.queryList(sql, (handledate))
    insertsql = "insert into DIGUA_USER(id, IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dataList = []
    id = dbUtil_168.queryCount("select id from DIGUA_USER order by id desc limit 1", ())
    for row in rows:
        if not row:
            continue
        #try:
        id = id + 1
        #print id
        dataList.append((id, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
        #except:
        #    continue
        if len(dataList) >= 1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

def initChannelRetentionCnt():
    sql = "select U.client_channel_id, count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 group by U.client_channel_id"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:
        if not row:
            continue
        CHANNEL_RETENTIONS_CNT_TODAY[str(row[0])]=row[1]
    sql = "select U.client_channel_id, count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 group by U.client_channel_id"
    rows = dbUtil_168.queryList(sql, (datetime1))
    for row in rows:
        if not row:
            continue
        CHANNEL_RETENTIONS_CNT_1DAY[str(row[0])]=row[1]
    sql = "select U.client_channel_id, count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 and datediff(%s, L.created_date)=0 group by U.client_channel_id"
    rows = dbUtil_168.queryList(sql, (datetime7))
    for row in rows:
        if not row:
            continue
        CHANNEL_RETENTIONS_CNT_7DAY[str(row[0])]=row[1]
    sql = "select U.client_channel_id, count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 and datediff(%s, L.created_date)=0 group by U.client_channel_id"
    rows = dbUtil_168.queryList(sql, (datetime30))
    for row in rows:
        if not row:
            continue
        CHANNEL_RETENTIONS_CNT_30DAY[str(row[0])]=row[1]


def initChannelRetentionRate():
    sql = "select CLIENT_CHANNEL_ID, added_cnt from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT where datediff(%s, stat_date)=0"
    rows = dbUtil_168.queryList(sql, (datetime1))
    for row in rows:
        if not row:
            continue
        channelId = str(row[0])
        if CHANNEL_RETENTIONS_CNT_1DAY.has_key(channelId) and row[1]>0:
            CHANNEL_RETENTIONS_RATE_1DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_1DAY[channelId]*100)/row[1], 2)*100)
        else:
            CHANNEL_RETENTIONS_RATE_1DAY[channelId]=0
    sql = "select CLIENT_CHANNEL_ID, added_cnt from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT where datediff(%s, stat_date)=0"
    rows = dbUtil_168.queryList(sql, (datetime7))
    for row in rows:
        if not row:
            continue
        channelId = str(row[0])
        if CHANNEL_RETENTIONS_CNT_7DAY.has_key(channelId) and row[1]>0:
            CHANNEL_RETENTIONS_RATE_7DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_7DAY[channelId]*100)/row[1], 2)*100)
        else:
            CHANNEL_RETENTIONS_RATE_7DAY[channelId]=0
    sql = "select CLIENT_CHANNEL_ID, added_cnt from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT where datediff(%s, stat_date)=0"
    rows = dbUtil_168.queryList(sql, (datetime30))
    for row in rows:
        if not row:
            continue
        channelId = str(row[0])
        if CHANNEL_RETENTIONS_CNT_30DAY.has_key(channelId) and row[1]>0:
            CHANNEL_RETENTIONS_RATE_30DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_30DAY[channelId]*100)/row[1], 2)*100)
        else:
            CHANNEL_RETENTIONS_RATE_30DAY[channelId]=0


def insertClientChannelUser():
    sql = "SELECT U.client_channel_id, U.client_channel_name, COUNT(U.imei), SUM(L.pv), L.created_date FROM DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L inner join DIGUA_USER U on U.imei=L.imei GROUP BY U.client_channel_id"
    rows = dbUtil_168.queryList(sql, ())
    insertsql = "insert into DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT(CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, LOG_CNT, PV, STAT_DATE, ADDED_CNT, 1DAY_CNT, 7DAY_CNT, 30DAY_CNT, 1DAY_RATE, 7DAY_RATE, 30DAY_RATE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dataList = []
    for row in rows:
        if not row:
            continue
        channelId = str(row[0])
        addedCnt = 0
        dayCnt1 = 0
        dayCnt7 = 0
        dayCnt30 = 0
        dayRate1 = 0
        dayRate7 = 0
        dayRate30 = 0
        if CHANNEL_RETENTIONS_CNT_TODAY.has_key(channelId) : addedCnt = CHANNEL_RETENTIONS_CNT_TODAY[channelId]
        if CHANNEL_RETENTIONS_CNT_1DAY.has_key(channelId) : dayCnt1 = CHANNEL_RETENTIONS_CNT_1DAY[channelId]
        if CHANNEL_RETENTIONS_CNT_7DAY.has_key(channelId) : dayCnt7 = CHANNEL_RETENTIONS_CNT_7DAY[channelId]
        if CHANNEL_RETENTIONS_CNT_30DAY.has_key(channelId) : dayCnt30 = CHANNEL_RETENTIONS_CNT_30DAY[channelId]
        if CHANNEL_RETENTIONS_RATE_1DAY.has_key(channelId) : dayRate1 = CHANNEL_RETENTIONS_RATE_1DAY[channelId]
        if CHANNEL_RETENTIONS_RATE_7DAY.has_key(channelId) : dayRate7 = CHANNEL_RETENTIONS_RATE_7DAY[channelId]
        if CHANNEL_RETENTIONS_RATE_30DAY.has_key(channelId) : dayRate30 = CHANNEL_RETENTIONS_RATE_30DAY[channelId]
        try:
            dataList.append((channelId, row[1], row[2], row[3], row[4], addedCnt, dayCnt1, dayCnt7, dayCnt30, dayRate1, dayRate7, dayRate30))
        except:
            continue
        if len(dataList) >= 1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

def insertUserRetention():
    logCnt = getUserLogCnt()
    addedCnt = getUserDayCnt(handledate)
    dayCnt1 = getUserDayCnt(datetime1)
    dayCnt7 = getUserDayCnt(datetime7)
    dayCnt30 = getUserDayCnt(datetime30)
    dayRate1 = getUserRetentionRate(datetime1, dayCnt1)
    dayRate7 = getUserRetentionRate(datetime7, dayCnt7)
    dayRate30 = getUserRetentionRate(datetime30, dayCnt30)
    pv = getUserPv()
    sql = "insert into DIGUA_USER_RETENTION_STAT(LOG_CNT, ADDED_CNT, 1DAY_CNT, 7DAY_CNT, 30DAY_CNT, 1DAY_RATE, 7DAY_RATE, 30DAY_RATE, PV, STAT_DATE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dbUtil_168.insert(sql, (logCnt, addedCnt, dayCnt1, dayCnt7, dayCnt30, dayRate1, dayRate7, dayRate30, pv, handledate))

def getUserLogCnt():
    sql = "select count(imei) from DIGUA_STAT_USER_LOG_DAILY_"+createdDate
    return dbUtil_168.queryCount(sql, ())

def getUserDayCnt(datetimeStr):
    #sql = "select count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 and datediff(%s, L.created_date)=0"
    sql = "select count(U.imei) from (select imei from DIGUA_USER where datediff(%s,  created_date)=0) U inner join DIGUA_STAT_USER_LOG_DAILY_"+createdDate+" L on U.imei=L.imei"
    return dbUtil_168.queryCount(sql, (datetimeStr))

def getUserRetentionRate(datetiemStr, dayCnt):
    sql = "select added_cnt from DIGUA_USER_RETENTION_STAT where datediff(%s, stat_date)=0"
    cnt = dbUtil_168.queryCount(sql, (datetiemStr))
    if cnt == 0:
        return 0
    return int(round(float(dayCnt*100)/cnt, 2)*100)

def getUserPv():
    sql = "select sum(pv) from DIGUA_STAT_USER_LOG_DAILY_"+createdDate
    return dbUtil_168.queryCount(sql, ())


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

def clearTempTableData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP"
    dbUtil_168.truncate(sql1, ())
    sql1 = "truncate DIGUA_STAT_USER_LOG_DAILY"
    dbUtil_168.truncate(sql1, ())

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
        #initChannelName()
        #清理数据
   
        #clearData()
        print 'init and clear data over %s'%datetime.datetime.now()
        clearRepeatedNumData()
        print 'clear repeated Num data over %s'%datetime.datetime.now()
        insertUserLog()
        print 'insert user log data over %s'%datetime.datetime.now()
        #获取新增用户，并入表DIGUA_USER
        #insertNewUser()
        print 'insert user over %s'%datetime.datetime.now()

        #获取总用户留存率，并更新表DIGUA_USER_RETENTION_STAT
        #insertUserRetention()
        print 'insert user retention over %s'%datetime.datetime.now()

        #获取渠道总登录用户数和pv数并入表DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT
        #initChannelRetentionCnt()
        #initChannelRetentionRate()
        #insertClientChannelUser()
        print 'insert client channel user over %s'%datetime.datetime.now()

        #clearTempTableData()


        #获取渠道用户留存率，并更新表DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT
        #updateClientChannelUserRetention()
        #print 'update client channel user retention over'
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


