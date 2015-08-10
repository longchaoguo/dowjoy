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
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
handledate = None

def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    date=time.strptime(fileDate, "%Y-%m-%d")

def handleWeb():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in(157,158) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        if not os.path.exists(row[2]+localFile):
            continue
        print "%s%s"%(row[2], localFile)
        statWebKeyword(row[2] + localFile)
        print localFile, 'over'

def handleDigua():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in(161,162,163,164,205) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        if not os.path.exists(row[2]+localFile):
            continue
        print "%s%s"%(row[2],localFile)
        statDigauKeyword(row[2]+localFile)
        print localFile, 'over'

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
def statDigauKeyword(fileName):
    # 如果该文件不存在，抛出异常
    f = open(fileName, 'rb')
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

def statWebKeyword(fileName):
    # 如果该文件不存在，抛出异常
    f = open(fileName, 'rb')
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



###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    init()
    handleWeb()
    handleDigua()
    if dbUtil_168: dbUtil_168.close()
    #if dbUtil_111: dbUtil_111.close()
    if dbUtil_111: dbUtil_111.close()
    print "=================end   %s======" % datetime.datetime.now()


