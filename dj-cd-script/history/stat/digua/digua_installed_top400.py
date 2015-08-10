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
import MySQLdb
import os


delayday =1

#获取日志产生时间
handledate = str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(delayday), "%Y-%m-%d"))


conn = MySQLdb.connect(host='192.168.0.35',user='moster',passwd='shzygjrmdwg',db='droid_game', charset='utf8')
cursor = conn.cursor()

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
    cursor.execute(sql)
    conn.commit()


def insertApp(apps, createdDate):
    for app in apps:
        sql = "select APP_NAME from APP where PKG_NAME = '%s'" %(app.get("pkgname"))
        cursor.execute(sql)
        cords = cursor.fetchall()
        if len(cords) == 0:
            sql = "insert into APP(PKG_NAME, APP_NAME, CNT, LAST_DATE, CREATED_DATE) values ('%s', '%s', '%s', '%s', '%s')" %(app.get("pkgname"), app.get("name"), 1, createdDate, createdDate)
            cursor.execute(sql)
            conn.commit()
        else:
            sql = "update APP set CNT=CNT+1, LAST_DATE='%s' where PKG_NAME='%s'" %(createdDate, app.get("pkgname"))
            cursor.execute(sql)
            conn.commit()
            if app.get("name") != cords[0][1]:
                sql = "select NAME from APP_NAME where PKG_NAME = '%s' and NAME = '%s'" % (app.get("pkgname"), app.get("name"))
                cursor.execute(sql)
                cords = cursor.fetchall()
                if len(cords) == 0:
                    sql = "insert into APP_NAME(PACKAGE_NAME, NAME, CREATED_DATE) values ('%s', '%s', now())"%(app.get("pkgname"), app.get("name"))
                    cursor.execute(sql)
                    conn.commit()


def insertAppTopDaily():
    cursor.execute("truncate table DAILY_APP_TOP_400")
    conn.commit()
    #print len(APPTOPDDAILY)
    count=0
    sorted(APPTOPDDAILY.iteritems(), key=lambda d:d[1], reverse=False)
    for apptopdaily in APPTOPDDAILY.keys():
        if count >= 400:
            break
        sql="select G.ID from GAME G inner join GAME_PKG P on P.GAME_ID = G.ID where G.STATUS = 1 and P.STATUS = 1 and P.PACKAGE_NAME = '%s' group by G.ID order by G.HOT_CNT desc limit 1"%(apptopdaily)
        cursor.execute(sql)
        rs = cursor.fetchall()
	if len(rs) != 0:
	    gameId=rs[0][0]
            sql = "insert into DAILY_APP_TOP_400(PACKAGE_NAME, GAME_ID, CNT, CREATED_DATE) values ('%s', '%s', '%s', now())" %(apptopdaily, gameId, APPTOPDDAILY[apptopdaily])
            cursor.execute(sql)
            conn.commit()
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



def doTask(fileName):
    if os.path.isfile(fileName) == False:
        return
    ts = open(fileName, 'rb')
    while True:
        line = ts.readline()
        if len(line) == 0:
            break
        if not isValid(line) or  not isEndWithDate(line):
            break
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
    doTask("/home/downjoy/w3clog/client_350/upgrade.info." + handledate + ".txt")
    insertAppTopDaily()
    
start = datetime.datetime.now()
main()

cursor.close()
conn.close()
end = datetime.datetime.now()
print 'use  ' + str((end-start).seconds) + '  seconds'
