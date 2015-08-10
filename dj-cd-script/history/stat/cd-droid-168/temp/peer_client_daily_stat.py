#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.4 $"
__date__ = "$Date: 2012/09/14 08:34:16 $"

import pymssql
import re
import os
import datetime
from djutil.DBUtil import DBUtil
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

delayDay = 1
yesterdayDate = datetime.datetime.now() - datetime.timedelta(days=delayDay)
#yesterdayDate = datetime.date(2014,01,16)#数据恢复
dbUtilStat187 = DBUtil('stat_187')
execute = ScriptExecuteUtil(dbUtil=dbUtilStat187, handleDate=yesterdayDate)

handledate = str(datetime.datetime.strftime(yesterdayDate, "%Y-%m-%d"))
conn = pymssql.connect(host="192.168.0.111", user="moster", password="shzygjrmdwg", database="droid_stat")
cursor = conn.cursor()

def main():
    cursor.execute("delete from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cursor.execute("delete from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER_SUM where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cursor.execute("insert into CLIENT_STAT_DAILY_UNIQUE_ADDED_USER(IMEI, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, STAT_DATE, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, DEVICE, INSTALL_TYPE) select IMEI, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, STAT_DATE, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, DEVICE, INSTALL_TYPE from CLIENT_STAT_DAILY_UNIQUE_USER where imei not in (select imei from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where datediff(day, STAT_DATE , '%s')>0)"%handledate)
    cursor.execute("insert CLIENT_STAT_DAILY_UNIQUE_ADDED_USER_SUM(CNT, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, STAT_DATE) select count(*) as CNT, max(CLIENT_CHANNEL_ID) CLIENT_CHANNEL_ID, max(CLIENT_CHANNEL_NAME) CLIENT_CHANNEL_NAME, convert(varchar(100), max(STAT_DATE), 23) STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_ADDED_USER where datediff(day, STAT_DATE , '%s')=0 group by (CLIENT_CHANNEL_ID)"%handledate)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    try:
        execute.start(main)
    finally:
        if dbUtilStat187: dbUtilStat187.close()

