#!/usr/bin/python
# -*- #coding:utf-8
#
#统计地瓜最多安装top400
#部署服务器：192.168.0.38
#部署路径：
#脚本执行时间：每日凌晨2点
#

import re
import datetime
import time
import os
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_10 = DBUtil('droid_game_10')

delayday =1

#获取日志产生时间
handledate = str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(delayday), "%Y-%m-%d"))

APPTOPDDAILY = {}

def isValid(line):
    temp = line.split('|')
    if len(temp) < 3:
        return False
    else:
        return True

def isEndWithDate(line):
    p = re.compile(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
    m = p.search(line)
    if m:
        return True
    else:
        return False


def insertDeviceInfo(imei, createdDate):
    sql = "insert into DEVICE_INFO(IMEI, CNT, LAST_DATE, CREATED_DATE) values ('%s','%s', '%s', '%s') on duplicate key update CNT = CNT + 1, LAST_DATE = '%s'" % (imei, 1, createdDate, createdDate, createdDate)
    dbUtil_10.insert(sql, ())


def insertApp(apps, createdDate):
    for app in apps:
        sql = "select APP_NAME from APP where PKG_NAME = '%s'" %(app.get("pkgname"))
        cords = dbUtil_10.queryRow(sql, ())
        if len(cords) == 0:
            sql = "insert into APP(PKG_NAME, APP_NAME, CNT, LAST_DATE, CREATED_DATE) values ('%s', '%s', '%s', '%s', '%s')" %(app.get("pkgname"), app.get("name"), 1, createdDate, createdDate)
            dbUtil_10.insert(sql, ())
        else:
            sql = "update APP set CNT=CNT+1, LAST_DATE='%s' where PKG_NAME='%s'" %(createdDate, app.get("pkgname"))
            dbUtil_10.update(sql, ())
            if app.get("name") != cords[0][1]:
                sql = "select NAME from APP_NAME where PKG_NAME = '%s' and NAME = '%s'" % (app.get("pkgname"), app.get("name"))
                cords = dbUtil_10.queryRow(sql, ())
                if len(cords) == 0:
                    sql = "insert into APP_NAME(PACKAGE_NAME, NAME, CREATED_DATE) values ('%s', '%s', now())"%(app.get("pkgname"), app.get("name"))
                    dbUtil_10.insert(sql, ())


def insertAppTopDaily():
    dbUtil_10.truncate("truncate table DAILY_APP_TOP_400")
    #print len(APPTOPDDAILY)
    count=0
    sorted(APPTOPDDAILY.iteritems(), key=lambda d:d[1], reverse=False)
    for apptopdaily in APPTOPDDAILY.keys():
        if count >= 400:
            break
        sql="select G.ID from GAME G inner join GAME_PKG P on P.GAME_ID = G.ID where G.STATUS = 1 and P.STATUS = 1 and P.PACKAGE_NAME = '%s' group by G.ID order by G.HOT_CNT desc limit 1"%(apptopdaily)
        dbUtil_10.queryRow(sql, ())
	if len(rs) != 0:
	    gameId=rs[0][0]
            sql = "insert into DAILY_APP_TOP_400(PACKAGE_NAME, GAME_ID, CNT, CREATED_DATE) values ('%s', '%s', '%s', now())" %(apptopdaily, gameId, APPTOPDDAILY[apptopdaily])
            dbUtil_10.insert(sql, ())
            count = count + 1


def analyzePacakgeNames(packageNames):
    apps=[]
    if(len(packageNames) == 0):
        return apps
    packageNameStr=packageNames.replace("{", "").replace("}", "")
    packageArray=packageNameStr.split(",")
    for i in range(0, len(packageArray)) :
        array=packageArray[i].split("=")
        #print array
        if len(array) != 2:
            continue
        key=array[0]
        value=array[1]
        result = {}
        result['pkgname'] = key
        result['name'] = value
        #apps[i] = result
        if APPTOPDDAILY.has_key(key):
            APPTOPDDAILY[key] = APPTOPDDAILY[key] + 1
        else:
            APPTOPDDAILY[key] = 1
    return apps



def doTask():
    sql = "select LOCAL_DIR, LOCAL_FILE from FTP_LOG_CONFIG where id in (49,50,51,110) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    fileName = ""
    for row in rows:
        fileName = row[0]+row[1]
        fileName = fileName%(handledate)

        if os.path.isfile(fileName) == False:
            continue
        ts = open(fileName, 'rb')
        while True:
            line = ts.readline()
            if len(line) == 0:
                continue
            if not isValid(line) or  not isEndWithDate(line):
                continue
            array=line.replace("\r", "").replace("\n", "").replace(" ", "").split("|")
            imei=array[0]
            packageNames=array[1]
            createdDate=array[2]
            #记录用户imei
            #insertDeviceInfo(imei, createdDate)
            apps=analyzePacakgeNames(packageNames)
            #insertApp(apps, createdDate)
        ts.close()


def main():
    start = datetime.datetime.now()
    doTask()
    insertAppTopDaily()
    if dbUtil_168: dbUtil_168.close()
    if dbUtil_10: dbUtil_10.close()
    end = datetime.datetime.now()
    print 'use  ' + str((end-start).seconds) + '  seconds'

main()



