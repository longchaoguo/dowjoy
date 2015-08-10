#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#
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
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
#dbUtil_111 = DBUtil('droid_stat_111')
dbUtil_35 = DBUtil('droid_game_10')
dbUtil_111 = DBUtil('droid_stat_111')
pattern = re.compile("\[(?P<TIME>\S*) \S*\] \S* (?P<URL>\S*) \S* (?P<IP>\S*), \S* (?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {(?P<HEAD>.+)}")
MODEL_BRAND_LIST={}

########################################################
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
def statFile():
    # 如果该文件不存在，抛出异常
    f = open("/opt/logs/digua.coreseek.keyword.txt", 'rb')
    sql = "insert into CACHE_KEYS_DIGUA(CACHE_KEY) values (%s)"
    dataList = []
    i=0
    while True:
        line = f.readline()
        if not line:
            break
        i=i+1
        #if i<=2305000:
        #    continue
        array = line.split('|')
        if len(array)<2:
            continue
        dataList.append((array[1]))

        if len(dataList) >= 1000 :
            print i
            insertData(dbUtil_168, sql, dataList)
            dataList = []
    if len(dataList)>0:
        insertData(dbUtil_168, sql, dataList)
        dataList = []
    f.close()

def statWebFile():
    # 如果该文件不存在，抛出异常
    f = open("/opt/logs/keyword-web.txt", 'rb')
    sql = "insert into CACHE_KEYS_WEB(CACHE_KEY) values (%s)"
    dataList = []
    i=0
    while True:
        line = f.readline()
        if not line:
            break
        i=i+1
        #if i<=2305000:
        #    continue
        array = line.split('|')
        if len(array)<2:
            continue
        dataList.append((array[1]))

        if len(dataList) >= 1000 :
            print i
            insertData(dbUtil_168, sql, dataList)
            dataList = []
    if len(dataList)>0:
        insertData(dbUtil_168, sql, dataList)
        dataList = []
    f.close()

def delRepetitionData():
    sql="SELECT temp_imei, COUNT(*) AS CNT FROM TEMP_IMEI_211 GROUP BY temp_imei HAVING CNT>1"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        sql = "delete from TEMP_IMEI_211 where temp_imei=%s order by ID desc limit %s"
        dbUtil_168.delete(sql, (str(row[0]), int(row[1])-1))

def checkImei():
    sql = "select id, temp_imei from TEMP_IMEI_211 where imei is null or length(imei)=0 order by id"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        sql = "select top 1 imei from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where ID>17402202 and imei like '%"+row[1]+"' order by ID"
        print sql
        imei = dbUtil_111.queryCount(sql, ())
        print "imei="+str(imei)
        if imei != 0 and imei != '':
            updatesql = "update TEMP_IMEI_211 set imei=%s where id=%s and temp_imei=%s"
            dbUtil_168.update(updatesql, (imei, row[0], row[1]))

def statImei():
    fileName="/opt/logs/djdiguaserverdcn.txt"
    if os.path.exists(fileName):
        f = open(fileName, 'rb')
        dataList = []
        sql="insert into TEMP_DIGUA_IMEI_211(IMEI) value(%s)"
        while True:
            line = f.readline()
            if not line:
                break
            match = pattern.match(line)
            if not match:
                continue
            try:
                headStr = "{"+match.group("HEAD").replace("\\", "")+"}"
                headDict = eval(headStr)
                #\"verifyCode\":\"0774337b197fa8dcd7b3ae2da648d88d\",\"it\":\"2\",\"resolutionWidth\":320,\"imei\":\"867083017989516\",\"clientChannelId\":\"100400\",\"version\":\"6.6\",\"dd\":160,\"num\":\"null\",\"sswdp\":320,\"hasRoot\":\"true\",\"device\":\"ZTE_U790\",\"ss\":2,\"sdk\":10,\"resolutionHeight\":480,\"OsName\":\"2.3.6\",\"gpu\":\"PowerVR SGX 531\"
                imei = match.group("TIME")
                dataList.append((imei))
                if len(dataList) >= 1000:
                    insertData(dbUtil_168, insertsql, dataList)
                    dataList = []
            except:
                continue
        if dataList :
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
        f.close()

def checkImei2():
    sql = "select id, temp_imei from TEMP_IMEI_211 where imei is null or length(imei)=0 order by id"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        sql = "select imei from DIGUA_STAT_USER_LOG_TEMP where imei like '%"+row[1]+"' order by created_date limit 1"
        print sql
        imei = dbUtil_168.queryCount(sql, ())
        print "imei="+str(imei)
        if imei != 0 and imei != '':
            updatesql = "update TEMP_IMEI_211 set imei=%s where id=%s and temp_imei=%s"
            dbUtil_168.update(updatesql, (imei, row[0], row[1]))


def insertTempUserDailyLogs():
    #sql = "select ID from TEMP_DIGUA_STAT_USER_LOG  order by ID desc limit 1"
    #maxIndex = 17413900
    #print maxIndex
    #startIndex = 1
    #stepIndex = 500000
    sql = "select CLIENT_CHANNEL_ID, IMEI , VERSION , PV, CREATED_DATE, NUM from TEMP_DIGUA_STAT_USER_LOG where created_date>='2014-01-16 00:00:00'  and created_date<'2014-01-17 00:00:00' order by ID "
    rows = dbUtil_168.queryList(sql, ())
    dataList = []
    insertsql = "INSERT INTO DIGUA_STAT_USER_LOG(CLIENT_CHANNEL_ID,  IMEI ,  VERSION ,  PV,  CREATED_DATE,  NUM) values(%s, %s, %s, %s, %s, %s)"
    for row in rows:
        if not row:
            continue
        dataList.append((row[0], row[1], row[2], row[3], row[4], row[5]))
        if len(dataList) >= 1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []

    if dataList :
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

def statModel():

    #sql="select min(ID) from MODEL GROUP BY BRAND"
    #rows = dbUtil_35.queryList(sql, ())
    #for row in rows:
    #    MODEL_BRAND_LIST[str(row[0])]=0

    sql = "SELECT T.DEVICE, COUNT(T.imei) AS CNT from DIGUA_STAT_USER_MONTH_STAT T GROUP BY T.DEVICE"
    rows = dbUtil_168.queryList(sql, ())
    insertsql = "insert into DIGUA_STAT_MODEL_TEMP_STAT(DEVICE, cnt) values(%s, %s)"
    dataList = []
    for row in rows:
        dataList.append((row[0].replace("'", ""), row[1]))
    insertData(dbUtil_168, insertsql, dataList)

def updateModel():
    sql = "select id, DEVICE from DIGUA_STAT_MODEL_TEMP_STAT WHERE brand IS NULL"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        try:
            serial = (row[1].split("-"))[0].replace("!", "").replace("'", "").replace('"', '')
            if len(serial) == 0:
                continue
            serial = row[1]
            sql = "select brand from MODEL where model_serial like '%"+serial.decode('utf8')+"%' limit 1"
            print sql
            rs = dbUtil_35.queryRow(sql, ())
            if rs:
            #print sql 
            #print rs[0]
                sql = "update DIGUA_STAT_MODEL_TEMP_STAT set brand=%s where id=%s"
                dbUtil_168.update(sql, (rs[0], row[0]))
        except:
            continue

    #print MODEL_BRAND_LIST
    #fw = open("/usr/local/bin/cdroid/temp/model.txt", 'wb')
    #for k,v in MODEL_BRAND_LIST.items():
    #    print(str(k)+"|"+str(v))
    #fw.close()

def loadData():
    '''
    sql = "select CNT, CHANNEL_CNT, CLIENT_CHANNEL_ID, VERSION, INSTALL_TYPE, STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER_SUM_FOR_CLIENT_CHANNEL"
    rows = dbUtil_111.queryList(sql, ())
    insertsql = "insert into DIGUA_STAT_UNIQUE_ADDED_USER_FOR_CLIENT_CHANNEL(CNT, CHANNEL_CNT, CLIENT_CHANNEL_ID, VERSION, INSTALL_TYPE, STAT_DATE) values(%s, %s, %s, %s, %s, %s)"
    dataList = []
    for row in rows:
        dataList.append((row[0],row[1],row[2],row[3],row[4],row[5]))
        if len(dataList)>=1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []
    '''
    sql = "select CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, CNT, STAT_DATE from CLIENT_STAT_DAILY_CLIENT_CHANNEL_CNT"
    rows = dbUtil_111.queryList(sql, ())
    insertsql = "insert DIGUA_STAT_DAILY_CLIENT_CHANNEL_CNT(CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, CNT, STAT_DATE) values(%s, %s, %s, %s)"
    dataList = []
    for row in rows:
        dataList.append((row[0],row[1],row[2],row[3]))
        if len(dataList)>=1000:
            insertData(dbUtil_168, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_168, insertsql, dataList)
        dataList = []

def updateGamePackage():
    #QUAL_COMM(1L, "高通"), NVIDIA_TEGRA(2L, "nVIDIA Tegra"), OMAP(4L, "德州仪器TI OMAP"), EXYNOS(8L, "三星猎户座Exynos");
    sql=" select GAME_ID, SUPPORT_CPU, CPU_TYPE_SET, ID FROM GAME_PKG WHERE SUPPORT_CPU is not null and CPU_TYPE_SET=0 AND STATUS=1 order by id desc"
    rows = dbUtil_35.queryList(sql, ())
    for row in rows:
        cpuSet=0
        print row[0]
        print row[3]
        cpuArray=row[1].split(",")
        for cpu in cpuArray:
            #print cpu.encode('utf-8')
            #print '高通'.decode("gbk").encode('utf-8')
            #cpuSet=cpuSet+CPU_LIST[]
            if cpu.encode('utf-8') == '高通'.decode("gbk").encode('utf-8'):
                cpuSet=cpuSet+1
                #print cpuSet
            if cpu.encode('utf-8') == 'nVIDIA Tegra'.decode("gbk").encode('utf-8'):
                cpuSet=cpuSet+2
                #print cpuSet
            if cpu.encode('utf-8') == '德州仪器TI OMAP'.decode("gbk").encode('utf-8'):
                cpuSet=cpuSet+4
                #print cpuSet
            if cpu.encode('utf-8') == '三星猎户座Exynos'.decode("gbk").encode('utf-8'):
                cpuSet=cpuSet+8
                #print cpuSet
        dbUtil_35.update("update GAME_PKG set CPU_TYPE_SET=%s where id=%s", (cpuSet, row[3]))
def updateOutline():
    cpu=u'高通,nVIDIA Tegra,德州仪器TI OMAP,三星猎户座Exynos'
    dbUtil_35.update(sql, (cpu))

def updateGameOutline():
    updateOutline(u'你我之间,无“微”不至的“爱”。专为情侣设计的甜蜜应用。',19946)

def updateActivityNetgameId():
    sql="SELECT ID, GAME_IDS FROM ACTIVITY WHERE RESOURCE_TYPE=5"
    rows=dbUtil_35.queryList(sql, ())
    for row in rows:
        print row[0]
        sql="select group_concat(channel_id) from NETGAME_GAME where ID IN ("+row[1]+")"
        #print sql
        rs=dbUtil_35.queryRow(sql, ())
        #print rs[0]
        updatesql="update ACTIVITY set GAME_IDS=%s where ID=%s"
        dbUtil_35.update(updatesql, (rs[0],row[0]))


###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    #statFile()
    #statWebFile()
    #delRepetitionData()
    #checkImei()
    #statImei()
    #checkImei2()
    #insertTempUserDailyLogs()
    #statModel()
    updateModel()
    #loadData()
    #updateGameOutline()
    #updateGamePackage()
    #updateActivityNetgameId()
    #updateOutline()
    if dbUtil_168: dbUtil_168.close()
    #if dbUtil_111: dbUtil_111.close()
    if dbUtil_35: dbUtil_35.close()
    if dbUtil_111: dbUtil_111.close()
    print "=================end   %s======" % datetime.datetime.now()


