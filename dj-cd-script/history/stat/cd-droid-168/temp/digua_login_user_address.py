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
import httplib
import json
###########################################
dbUtil_168 = DBUtil('droid_stat_168')

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


def main():
    sql = "select imei, ip from TEMP_DIGUA_LANGUAGE_USER_1 where COUNTRY is null"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        getAddress(row[0], row[1])

def getTaobaoJson(ip):
    url="/service/getIpInfo.php?ip=%s"%(str(ip))
    conn = httplib.HTTPConnection("ip.taobao.com")
    conn.request("GET", url)
    res = conn.getresponse()
    data = res.read()
    return data

def getAddress(imei, ip):
    date = json.loads(getTaobaoJson(ip))
    COUNTRY=date["data"]["country"].encode("utf8")
    REGION=date["data"]["region"].encode("utf8")
    sql = "update TEMP_DIGUA_LANGUAGE_USER_1 set COUNTRY=%s, PROVINCE=%s where imei=%s"
    dbUtil_168.update(sql, (COUNTRY, REGION, imei))

###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    main()
    if dbUtil_168: dbUtil_168.close()
    print "=================end   %s======" % datetime.datetime.now()


