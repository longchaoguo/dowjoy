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
dbUtil_10=DBUtil('droid_game_10')
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
CHANNEL_RETENTIONS_CNT_TODAY={}
CHANNEL_RETENTIONS_CNT_1DAY={}
CHANNEL_RETENTIONS_CNT_7DAY={}
CHANNEL_RETENTIONS_CNT_30DAY={}
CHANNEL_RETENTIONS_RATE_1DAY={}
CHANNEL_RETENTIONS_RATE_7DAY={}
CHANNEL_RETENTIONS_RATE_30DAY={}
CHANNEL_NAME={}

CHANNEL_RATE_LIST={}
CHANNEL_PV_DICT = {}
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"地瓜用户留存错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com','shan.liang@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate, datetime1, datetime7, datetime30
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    date=time.strptime(fileDate, "%Y-%m-%d")
    date=datetime.datetime(date[0],date[1],date[2])
    datetime1 = datetime.datetime.strftime(date - datetime.timedelta(days = 1), "%Y-%m-%d")
    datetime7 = datetime.datetime.strftime(date - datetime.timedelta(days = 7), "%Y-%m-%d")
    datetime30 = datetime.datetime.strftime(date - datetime.timedelta(days = 30), "%Y-%m-%d")

def clearData():
    #sql1 = "delete from DIGUA_STAT_USER_LOG where datediff(%s,CREATED_DATE) = 0"
    #dbUtil_168.delete(sql1, (handledate))
    sql = "delete from DIGUA_USER_APACHE_NOT_MAC where datediff(%s,CREATED_DATE) = 0"
    dbUtil_168.delete(sql, (handledate))
    sql = "delete from DIGUA_USER_RETENTION_STAT_APACHE_NOT_MAC where datediff(%s,stat_date) = 0"
    dbUtil_168.delete(sql, (handledate))
    #sql = "truncate table DIGUA_USER_NUM_BLACKLIST_APACHE_NOT_MAC"
    #dbUtil_168.delete(sql, ())
    #sql = "truncate table DIGUA_STAT_NEW_ADDED_LOG_APACHE_NOT_MAC"
    #dbUtil_168.delete(sql, ())
    sql = "delete from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT_APACHE_NOT_MAC where datediff(%s,stat_date) = 0"
    dbUtil_168.delete(sql, (handledate))

def clearRepeatedNumData():
    sql = "insert into DIGUA_STAT_NEW_ADDED_LOG_APACHE_NOT_MAC (IMEI, NUM) SELECT IMEI, NUM FROM DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC WHERE IMEI NOT IN (SELECT IMEI FROM DIGUA_USER_APACHE_NOT_MAC where DATEDIFF(created_date, %s)<0)"
    rows = dbUtil_168.insert(sql, (handledate))

    sql = "SELECT num, COUNT(imei) AS cnt FROM (SELECT num, imei FROM DIGUA_STAT_NEW_ADDED_LOG_APACHE_NOT_MAC WHERE LENGTH(num)>0 UNION ALL SELECT num, imei FROM DIGUA_USER_APACHE_NOT_MAC WHERE LENGTH(num)>0 AND DATEDIFF(%s, created_date)<367)T GROUP BY num having cnt>3"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:
        dbUtil_168.insert("insert into DIGUA_USER_NUM_BLACKLIST_APACHE_NOT_MAC(IMEI, NUM) select IMEI, NUM FROM DIGUA_STAT_NEW_ADDED_LOG_APACHE WHERE NUM=%s", (row[0]))
    sql = "select imei, num from DIGUA_USER_NUM_BLACKLIST_APACHE"
    rows = dbUtil_168.queryList(sql)
    for row in rows:
        sql = "delete from DIGUA_STAT_USER_LOG_DAILY_APACHE where IMEI=%s and NUM=%s"
        dbUtil_168.delete(sql, (row[0], row[1]))
    

def insertUserLog():
    sql = "insert into DIGUA_STAT_USER_LOG_APACHE_NOT_MAC(IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV) select IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV from DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
    dbUtil_168.insert(sql, ())

def insertNewUser():
    sql = "SELECT IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE FROM DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC WHERE IMEI NOT IN (SELECT IMEI FROM DIGUA_USER_APACHE_NOT_MAC where DATEDIFF(created_date, %s)<0)"
    rows = dbUtil_168.queryList(sql, (handledate))
    insertsql = "insert into DIGUA_USER_APACHE_NOT_MAC(id, IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dataList = []
    id = dbUtil_168.queryCount("select id from DIGUA_USER_APACHE_NOT_MAC order by id desc limit 1", ())
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

#渠道留存人数   
def initChannelRetentionCnt():
    sql = '''SELECT U.client_channel_id, COUNT(U.imei) 
            FROM DIGUA_USER_APACHE_NOT_MAC U
            WHERE DATEDIFF(%s,  created_date)=0 
            AND EXISTS(SELECT imei FROM DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC L WHERE U.imei = L.imei)
            GROUP BY U.client_channel_id; '''
    # 今日新增
    rows = dbUtil_168.queryList(sql, (handledate))
    if rows:
        for row in rows:
            if not row:
                continue
            CHANNEL_RETENTIONS_CNT_TODAY[str(row[0])]=row[1]
    
    # 1日留存人数
    rows = dbUtil_168.queryList(sql, (datetime1))
    if rows:
        for row in rows:
            if not row:
                continue
            CHANNEL_RETENTIONS_CNT_1DAY[str(row[0])]=row[1]
    
    # 7日留存人数    
    rows = dbUtil_168.queryList(sql, (datetime7))
    if rows:
        for row in rows:
            if not row:
                continue
            CHANNEL_RETENTIONS_CNT_7DAY[str(row[0])]=row[1]
        
    # 30日留存人数    
    rows = dbUtil_168.queryList(sql, (datetime30))
    if rows:
        for row in rows:
            if not row:
                continue
            CHANNEL_RETENTIONS_CNT_30DAY[str(row[0])]=row[1]

#渠道留存率
def initChannelRetentionRate():
    sql = "select CLIENT_CHANNEL_ID, added_cnt from DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT_APACHE_NOT_MAC where datediff(%s, stat_date)= 0"
    
    # 1日留存率
    rows = dbUtil_168.queryList(sql, (datetime1))
    if rows: 
        for row in rows:
            if not row:
                continue
            channelId = str(row[0])
            if CHANNEL_RETENTIONS_CNT_1DAY.has_key(channelId) and row[1]>0:
                CHANNEL_RETENTIONS_RATE_1DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_1DAY[channelId]*100)/row[1], 2)*100)
            else:
                CHANNEL_RETENTIONS_RATE_1DAY[channelId]=0
            
    # 7日留存率
    rows = dbUtil_168.queryList(sql, (datetime7))
    if rows:
        for row in rows:
            if not row:
                continue
            channelId = str(row[0])
            if CHANNEL_RETENTIONS_CNT_7DAY.has_key(channelId) and row[1]>0:
                CHANNEL_RETENTIONS_RATE_7DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_7DAY[channelId]*100)/row[1], 2)*100)
            else:
                CHANNEL_RETENTIONS_RATE_7DAY[channelId]=0
    
    # 30日留存率
    rows = dbUtil_168.queryList(sql, (datetime30))
    if rows:
        for row in rows:
            if not row:
                continue
            channelId = str(row[0])
            if CHANNEL_RETENTIONS_CNT_30DAY.has_key(channelId) and row[1]>0:
                CHANNEL_RETENTIONS_RATE_30DAY[channelId]=int(round(float(CHANNEL_RETENTIONS_CNT_30DAY[channelId]*100)/row[1], 2)*100)
            else:
                CHANNEL_RETENTIONS_RATE_30DAY[channelId]=0

#插入渠道留存率信息
def insertClientChannelUserRetention():
    sql = '''SELECT client_channel_id, client_channel_name, COUNT(imei), SUM(pv), created_date 
            FROM DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC
            GROUP BY client_channel_id
          '''
    rows = dbUtil_168.queryList(sql)
    insertsql = "insert into DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT_APACHE_NOT_MAC(CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, LOG_CNT, PV, STAT_DATE, ADDED_CNT, 1DAY_CNT, 7DAY_CNT, 30DAY_CNT, 1DAY_RATE, 7DAY_RATE, 30DAY_RATE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
    sql = "insert into DIGUA_USER_RETENTION_STAT_APACHE_NOT_MAC(LOG_CNT, ADDED_CNT, 1DAY_CNT, 7DAY_CNT, 30DAY_CNT, 1DAY_RATE, 7DAY_RATE, 30DAY_RATE, PV, STAT_DATE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dbUtil_168.insert(sql, (logCnt, addedCnt, dayCnt1, dayCnt7, dayCnt30, dayRate1, dayRate7, dayRate30, pv, handledate))

def getUserLogCnt():
    sql = "select count(imei) from DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
    return dbUtil_168.queryCount(sql, ())

def getUserDayCnt(datetimeStr):
    #sql = "select count(*) from DIGUA_USER U inner join DIGUA_STAT_USER_LOG L on U.IMEI=L.IMEI where datediff(%s, U.created_date)=0 and datediff(%s, L.created_date)=0"
    sql = "select count(U.imei) from (select imei from DIGUA_USER_APACHE_NOT_MAC where datediff(%s,  created_date)=0) U inner join DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC L on U.imei=L.imei"
    return dbUtil_168.queryCount(sql, (datetimeStr))

def getUserRetentionRate(datetiemStr, dayCnt):
    sql = "select added_cnt from DIGUA_USER_RETENTION_STAT_APACHE_NOT_MAC where datediff(%s, stat_date)=0"
    cnt = dbUtil_168.queryCount(sql, (datetiemStr))
    if cnt == 0:
        return 0
    return int(round(float(dayCnt*100)/cnt, 2)*100)

def getUserPv():
    sql = "select sum(pv) from DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
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
    sql1 = "truncate DIGUA_STAT_USER_LOG_TEMP_APACHE_NOT_MAC"
    dbUtil_168.truncate(sql1, ())
    sql1 = "truncate DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
    dbUtil_168.truncate(sql1, ())

def updateOldUserData():
    sql1 = "truncate DIGUA_STAT_USER_LOG_DAILY_APACHE_NOT_MAC"
    dbUtil_168.truncate(sql1, ())
    sql = "delete from DIGUA_STAT_DAILY_CLIENT_CHANNEL_CNT where datediff(%s, STAT_DATE)=0"
    dbUtil_168.delete(sql, (handledate))
    sql = "delete from DIGUA_STAT_UNIQUE_ADDED_USER_FOR_CLIENT_CHANNEL where datediff(%s, STAT_DATE)=0"
    dbUtil_168.delete(sql, (handledate))
    sql = "insert into DIGUA_STAT_USER_LOG_DAILY (IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV) select IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, NUM, CREATED_DATE, PV from DIGUA_STAT_USER_LOG where datediff(%s, created_date)=0"
    dbUtil_168.insert(sql, (handledate))
    sql="insert DIGUA_STAT_DAILY_CLIENT_CHANNEL_CNT(CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, CNT, STAT_DATE) select CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, count(ID) as CNT, CREATED_DATE from DIGUA_STAT_USER_LOG_DAILY group by CLIENT_CHANNEL_ID order by CLIENT_CHANNEL_ID;"
    dbUtil_168.insert(sql, ())
    initClientChannelRate()
    sql ="SELECT COUNT(U.imei), U.client_channel_id, U.client_channel_name, L.VERSION, L.IT, L.created_date FROM DIGUA_STAT_USER_LOG_DAILY L inner join DIGUA_USER U on U.imei=L.imei where datediff(%s, U.created_date)=0 GROUP BY U.client_channel_id, L.VERSION, L.IT"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:
        cnt=row[0]
        clientChannelId=row[1]
        clientCnt=int(round((cnt * 100)/100.0))
        if CHANNEL_RATE_LIST.has_key(clientChannelId):
            clientCnt=int(round((cnt * CHANNEL_RATE_LIST[clientChannelId])/100.0))
        clentChannelName=row[2]
        version=row[3]
        installType=row[4]
        statDate=row[5]
        sql = "insert into DIGUA_STAT_UNIQUE_ADDED_USER_FOR_CLIENT_CHANNEL(CNT, CHANNEL_CNT, CLIENT_CHANNEL_ID, VERSION, INSTALL_TYPE, STAT_DATE) values(%s, %s, %s, '%s', %s, '%s')"%(cnt, clientCnt, clientChannelId, version, installType, statDate)
        dbUtil_168.insert(sql, ())


def initClientChannelRate():
    sql=" select id, RATE from CLIENT_CHANNEL "
    #print sql
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        if row and row[1]:
            CHANNEL_RATE_LIST[row[0]]=row[1]
        if row and not row[1]:
            CHANNEL_RATE_LIST[row[0]]=100

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
        clearData()
        print 'init and clear data over %s'%datetime.datetime.now()
        #clearRepeatedNumData()
        print 'clear repeated Num data over %s'%datetime.datetime.now()
        insertUserLog()
        print 'insert user log data over %s'%datetime.datetime.now()
        #获取新增用户，并入表DIGUA_USER
        insertNewUser()
        print 'insert user over %s'%datetime.datetime.now()

        #获取总用户留存率，并更新表DIGUA_USER_RETENTION_STAT
        insertUserRetention()
        print 'insert user retention over %s'%datetime.datetime.now()
        #updateOldUserData()

        #获取渠道总登录用户数和pv数并入表DIGUA_CLIENT_CHANNEL_USER_RETENTION_STAT
        initChannelRetentionCnt()
        initChannelRetentionRate()
        insertClientChannelUserRetention()
        print 'insert client channel user over %s'%datetime.datetime.now()
        
        #清理数据
        clearTempTableData()
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


