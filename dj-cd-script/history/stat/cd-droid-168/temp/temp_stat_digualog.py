#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
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
from djutil.MailUtil import MailUtil
###########################################
pattern = re.compile("\[(?P<TIME>\S*) \S*\] \S* (?P<URL>\S*) \S* (?P<IP>\S*), \S* (?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {(?P<HEAD>.+)}")

dbUtil_10=DBUtil('droid_stat_168')

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"�ع�ͳ����־ͳ�ƴ�����Ϣ".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################

#����־���
def statFile():
    # ������ļ������ڣ��׳��쳣
    fileName="/opt/logs/digua.version.txt"
    if os.path.exists(fileName):
        f = open(fileName, 'rb')
        dataList = []
        sql = "insert into TEMP_DIGUA_LANGUAGE_USER_1(LANGUAGE, IMEI) value(%s, %s)"
        while True:
            line = f.readline()
            line = line.replace("imei","").replace("languageType","").replace("\n","")
            urlStr = line[22:].split("|")
            #print urlStr
            dataList.append((urlStr[2], urlStr[0]))
            if len(dataList) >= 1000:
                #print len(dataList)
                insertData(dbUtil_10, sql, dataList)
                dataList = []
        if dataList:
            insertData(dbUtil_10, sql, dataList)
            dataList = []
        f.close()

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


###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    statFile()
    dbUtil_10.close()
    print "=================end   %s======" % datetime.datetime.now()


