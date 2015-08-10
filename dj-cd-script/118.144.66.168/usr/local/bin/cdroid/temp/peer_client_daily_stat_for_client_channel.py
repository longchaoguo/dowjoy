#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: zongquan.xie $"
__version__ = "$Revision: 1.3 $"
__date__ = "$Date: 2011/06/09 06:44:58 $"

import pymssql
import MySQLdb
import datetime
import re
import os
from djutil.DBUtil import DBUtil
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

yesterdayDate = datetime.datetime.now() - datetime.timedelta(days=1)
#yesterdayDate=datetime.date(2014,01,16)#huifu data
dbUtilStat187 = DBUtil('stat_187')
execute = ScriptExecuteUtil(dbUtil=dbUtilStat187, handleDate=yesterdayDate)

#获取日志产生时间
handledate = str(datetime.datetime.strftime(yesterdayDate, "%Y-%m-%d"))

connStat = pymssql.connect(host="192.168.0.111", user="moster", password="shzygjrmdwg", database="droid_stat")
cursorStat = connStat.cursor()

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()

def getClientChannelRate(clientChannelId):
    sql=" select RATE from CLIENT_CHANNEL where ID =%s"%(clientChannelId)
    #print sql
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows:
        return rows[0][0]
    return 100

def main():
    sql="select count(*), max(CLIENT_CHANNEL_ID), max(CLIENT_CHANNEL_NAME), max(VERSION), max(CLIENT_CHANNEL_ID), max(INSTALL_TYPE), convert(varchar(100), max(STAT_DATE), 23) from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where datediff(day, STAT_DATE , '%s')=0 group by CLIENT_CHANNEL_ID, VERSION, INSTALL_TYPE"%(handledate)
    cursorStat.execute(sql)
    rs = cursorStat.fetchall()
    cursorStat.execute("delete from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER_SUM_FOR_CLIENT_CHANNEL where datediff(day,STAT_DATE,'%s')=0"%(handledate))
    for row in rs:
        cnt=row[0]
        clientChannelId=row[1]
        clientCnt=int(round((cnt * getClientChannelRate(clientChannelId))/100.0))
        clentChannelName=row[2]
        version=row[3]
        clientChannelId=row[4]
        installType=row[5]
        statDate=row[6]
        cursorStat.execute("insert into CLIENT_STAT_DAILY_UNIQUE_ADDED_USER_SUM_FOR_CLIENT_CHANNEL(CNT, CHANNEL_CNT, CLIENT_CHANNEL_ID, VERSION, INSTALL_TYPE, STAT_DATE) values(%s, %s, %s, '%s', %s, '%s')"%(cnt, clientCnt, clientChannelId, version, installType, statDate))
        connStat.commit()

if __name__ == '__main__':
    try:
        execute.start(main)
    finally:
        if cursor: cursor.close()
        if cursorStat: cursorStat.close()
        if conn: conn.close()
        if connStat: connStat.close()
        if dbUtilStat187: dbUtilStat187.close()
