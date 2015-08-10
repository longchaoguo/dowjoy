#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.3 $"
__date__ = "$Date: 2012/09/14 08:34:16 $"

import ftplib
import datetime
import pymssql
import shutil
import time
from djutil.DBUtil import DBUtil
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

yesterdayDate = datetime.datetime.now() - datetime.timedelta(days=1)
#yesterdayDate = datetime.date(2014,01,16)#数据恢复
dbUtilStat187 = DBUtil('stat_187')
execute = ScriptExecuteUtil(dbUtil=dbUtilStat187, handleDate=yesterdayDate)

yesterday = datetime.datetime.strftime(yesterdayDate, '%Y-%m-%d')
handledate = str(datetime.datetime.strftime(yesterdayDate, "%Y-%m-%d"))
logdir="E:/diguastat/"
fileName="android.client.stat.%s.txt"%yesterday

##################################################
#连接ftp下载前一日的日志文件
def downloadFtp(ip, username, password, fileName, typeStr):
    ftp=ftplib.FTP(ip)
    ftp.login(username, password)
    f=open('E://data.txt', typeStr)
    try:
        ftp.retrbinary("RETR %s"%fileName, f.write)
    except Exception, ex:
        print '%s nfs file not exist: %s'%(ip, fileName)
    f.close()
    ftp.quit()

def isErrorLine(array):
   for i in range(0, len(array)):
       if array[i] is None or len(array[i]) == 0:
           return True
   return False

def statFile():
    fo=open('E://diguastat/data.txt', 'wb')
    fi=open('E://data.txt', 'rb')
    errorCount=0
    count=0
    sumCount=0
    i=0
    while True:
        line = fi.readline()
        if len(line) == 0:
            if i == 3:
                break
            else:
                i = i + 1
                continue
        array=line.split("|")
        if len(array) == 12 or len(array) == 13:
            if isErrorLine(array):
                errorCount = errorCount + 1
            else:
                count = count + 1
                fo.write(line)
        else:
            errorCount = errorCount + 1
        sumCount = sumCount + 1
    fi.close()
    fo.close()
    print "error:  " + str(errorCount)
    print "count: "+ str(count)
    print "sumCount: " + str(sumCount)

def insertData(handleFile):
    conn = pymssql.connect(host="192.168.0.111", user="sa", password="qwertyuiop@123", database="droid_stat")
    cur = conn.cursor()
    cur.execute("truncate table CLIENT_DAILY_STAT_TEMP;")
    conn.commit()
    sql_a="insert into CLIENT_DAILY_STAT_TEMP(IMEI, IP, RESOLUTION_ID, OS_ID, VERSION, CLIENT_CHANNEL_ID, DEVICE, CREATED_DATE, EVENT_TYPE, RESOLUTION_NAME, OS_NAME, CLIENT_CHANNEL_NAME, INSTALL_TYPE) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    sql_b="insert into CLIENT_DAILY_STAT_TEMP(IMEI, IP, RESOLUTION_ID, OS_ID, VERSION, CLIENT_CHANNEL_ID, DEVICE, CREATED_DATE, EVENT_TYPE, RESOLUTION_NAME, OS_NAME, CLIENT_CHANNEL_NAME, INSTALL_TYPE) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"
    f=open(handleFile, 'rb')
    fo=open('E://diguastat/data_error.txt', 'wb')
    rows=[]
    errCnt=0
    while True:
        line=f.readline()
        if not line:
            break
        line=line.strip()
        cols=line.split('|')
        if len(cols)<12 or len(cols) >13:
            continue
        if len(cols)==12:
            cols.append(3) #表最后一字段默认为3
        rows.append(tuple(cols))
        if len(rows)==1000:
            try:
                cur.executemany(sql_a, rows) #
                conn.commit()
            except:
                for col in rows:
                    try:
                        cur.execute(sql_b%col)
                        conn.commit()
                    except Exception, e:
                        errCnt += 1
                        #if errCnt >= 1000: raise e
                        #print "error:", col
                        fo.write(sql_b%col+"\n")
                        continue
            del rows[:]
    if rows:
        try:
            cur.executemany(sql_a, rows) #
            conn.commit()
        except:
            for col in rows:
                try:
                    cur.execute(sql_b%col)
                    conn.commit()
                except Exception , e:
                    errCnt += 1
                    #if errCnt>= 1000: raise e
                    #print "error:", col
                    fo.write(sql_b%col+"\n")
                    continue
    fo.close()
    f.close()
    print "CLIENT_STAT_DAILY_UNIQUE_USER start"
    #清空昨天的日独立用户表
    cur.execute("truncate table CLIENT_STAT_DAILY_UNIQUE_USER;")
    #取出相同IMEI下最大ID的记录存入日独立用户记录表
    cur.execute("""
    insert CLIENT_STAT_DAILY_UNIQUE_USER(IMEI, IP, RESOLUTION_ID, RESOLUTION_NAME, OS_ID, OS_NAME, VERSION, CLIENT_CHANNEL_ID, CLIENT_CHANNEL_NAME, DEVICE, STAT_DATE, INSTALL_TYPE)
    select C.IMEI, C.IP, C.RESOLUTION_ID, C.RESOLUTION_NAME, C.OS_ID, C.OS_NAME, C.VERSION, C.CLIENT_CHANNEL_ID, C.CLIENT_CHANNEL_NAME, C.DEVICE, C.CREATED_DATE, coalesce(C.INSTALL_TYPE, 3) INSTALL_TYPE
    from CLIENT_DAILY_STAT_TEMP as C
    inner join(
      select min(T.ID) as ID
      from CLIENT_DAILY_STAT_TEMP as T 
      inner join (
        select IMEI, min(CREATED_DATE) as STAT_DATE 
        from CLIENT_DAILY_STAT_TEMP group by IMEI ) as TT 
        on T.IMEI = TT.IMEI 
        and T.CREATED_DATE = TT.STAT_DATE
      group by T.IMEI, T.CLIENT_CHANNEL_ID, T.CREATED_DATE
      )as TEMP
    on C.ID=TEMP.ID
    """)
    print "CLIENT_STAT_DAILY_UNIQUE_USER end"

    #插入操作系统统计表
    cur.execute("delete from CLIENT_STAT_DAILY_OS_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("delete from CLIENT_STAT_DAILY_RESOLUTION_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("delete from CLIENT_STAT_DAILY_CLIENT_CHANNEL_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("delete from CLIENT_STAT_DAILY_DEVICE_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("delete from CLIENT_STAT_DAILY_VERSION_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("delete from CLIENT_STAT_DAILY_USER_CNT where datediff(day, STAT_DATE , '%s')=0"%handledate)
    cur.execute("insert  CLIENT_STAT_DAILY_OS_CNT select OS_ID, (select top 1 C2.OS_NAME from CLIENT_STAT_DAILY_UNIQUE_USER C2 where C2.OS_ID = C.OS_ID) as OS_NAME, count(*) as CNT, convert(varchar(100), STAT_DATE, 23) as STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_USER C group by OS_ID, convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23) , OS_ID;")
    #插入分辨率统计表
    cur.execute("insert CLIENT_STAT_DAILY_RESOLUTION_CNT select RESOLUTION_ID, (select top 1 C2.RESOLUTION_NAME from CLIENT_STAT_DAILY_UNIQUE_USER C2 where C2.RESOLUTION_ID = C.RESOLUTION_ID) as RESOLUTION_NAME, count(*) as CNT, convert(varchar(100), STAT_DATE, 23) as STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_USER C group by RESOLUTION_ID, convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23) , RESOLUTION_ID;")
    #插入渠道统计表
    cur.execute("insert CLIENT_STAT_DAILY_CLIENT_CHANNEL_CNT select CLIENT_CHANNEL_ID, (select top 1 C2.CLIENT_CHANNEL_NAME from CLIENT_STAT_DAILY_UNIQUE_USER C2 where C2.CLIENT_CHANNEL_ID = C.CLIENT_CHANNEL_ID) as CLIENT_CHANNEL_NAME, count(*) as CNT, convert(varchar(100), STAT_DATE, 23) as STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_USER C group by CLIENT_CHANNEL_ID, convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23) , CLIENT_CHANNEL_ID;")
    #插入机型统计表
    cur.execute("insert CLIENT_STAT_DAILY_DEVICE_CNT select DEVICE, count(*) as CNT, convert(varchar(100), STAT_DATE, 23) as STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_USER C group by DEVICE, convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23) , DEVICE;")
    #插入地瓜版本统计表
    cur.execute("insert CLIENT_STAT_DAILY_VERSION_CNT select VERSION, count(*) as CNT, convert(varchar(100), STAT_DATE, 23) as STAT_DATE from CLIENT_STAT_DAILY_UNIQUE_USER C group by VERSION, convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23) , VERSION;")
    #插入每日独立用户数统计表
    cur.execute("insert CLIENT_STAT_DAILY_USER_CNT select convert(varchar(100), STAT_DATE, 23), count(*) as CNT from CLIENT_STAT_DAILY_UNIQUE_USER C group by convert(varchar(100), STAT_DATE, 23) order by convert(varchar(100), STAT_DATE, 23);")
    conn.commit()
    conn.close()

def main():
    downloadFtp('192.168.0.135','ftpdownjoy','djftp119',fileName,'wb')
    time.sleep(2)
    downloadFtp('192.168.0.135','ftpdownjoy','djftp119','./client/%s'%fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.135','ftpdownjoy','djftp119','./client_350/%s'%fileName,'ab')
    time.sleep(2)

    downloadFtp('192.168.0.167','ftpdownjoy','djftp119',fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.167','ftpdownjoy','djftp119','./client/%s'%fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.167','ftpdownjoy','djftp119','./client_350/%s'%fileName,'ab')
    time.sleep(2)
  
    downloadFtp('192.168.0.155','ftpdownjoy','djftp119',fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.155','ftpdownjoy','djftp119','./client/%s'%fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.155','ftpdownjoy','djftp119','./client_350/%s'%fileName,'ab')
    time.sleep(2)
  
    downloadFtp('192.168.0.174','ftpdownjoy','djftp119',fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.174','ftpdownjoy','djftp119','./client/%s'%fileName,'ab')
    time.sleep(2)
    downloadFtp('192.168.0.174','ftpdownjoy','djftp119','./client_350/%s'%fileName,'ab')
    time.sleep(2)
    #下载天语服务器的stat日志文件，拼接进149服务器data.txt
#    downloadFtp('192.168.0.172', 'ftpdownjoy', 'djftp119', 'ktouch.android.client.stat.%s.txt'%yesterday, 'ab')
#    time.sleep(2)
    #下载173服务器stat日志文件，英特圣及英贝尔，拼接进149服务器data.txt
#    downloadFtp('192.168.0.173', 'ftpdownjoy', 'djftp119', 'intson.android.client.stat.%s.txt'%yesterday, 'ab') #英特圣
#    time.sleep(2)
#    downloadFtp('192.168.0.173', 'ftpdownjoy', 'djftp119', 'ceadic.android.client.stat.%s.txt'%yesterday, 'ab') #英贝尔
    statFile()
    #将日志备份
    shutil.copy('E://diguastat/data.txt', 'E://diguastat/%s'%fileName)
    insertData(logdir+fileName)
    print "over~!"

if __name__ == '__main__':
    try:
        execute.start(main)
    finally:
        if dbUtilStat187: dbUtilStat187.close()
