#!/usr/bin/python
# -*- #coding:utf-8

__author__ = "$Author: guoqiang.sun$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015年4月3日10:56:14 $"
###########################################
#每天统计地瓜访问日志，操作表DIGUA_STAT_TEMP_LOG
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
dbUtil_168 = DBUtil('droid_stat_168')
device_stat_count={}
#获取日志产生时间
handledate = None
pattern = re.compile("\[(?P<TIME>\S*) \S*\] \S* (?P<URL>\S*) \S* (?P<IP>\S*), \S* (?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {(?P<HEAD>.+)}")
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"地瓜统计日志统计错误信息".encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'

########################################################
def init(fileDate):
    global handledate, createdDate
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%y%m%d")
    createdDate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%y%m%d'), "%Y-%m-%d")


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
def statFile(dir,fileName,flag = 'False'):
    # 如果该文件不存在，抛出异常
    if os.path.exists(dir+fileName):
        f = open(dir+fileName, 'rb')
        while True:
            line = f.readline()
            #print line
            if not line:
                break
            match = pattern.match(line)
            if not match:
                #print line
                continue
            status = match.group('STATUS')
            if not status in ['200', '206']:
                continue
            ua = None
            try:
                 ua = match.group("UA")
            except:
                continue
            if ua:
                ua = str(ua)
                ua = ua[ua.rindex(';')+1:ua.rindex(' ')]
                if(device_stat_count.has_key(ua)):
                    device_stat_count[ua]=device_stat_count[ua]+1
                else:
                    device_stat_count[ua]=1
        f.close()
        os.system('rm -rf %s'%(dir+fileName,))
    else:
        if(str(flag) == 'True'):
            ERROR_MSG = '解压文件%sbak/%s.tar.gz失败' %(dir,fileName)
            sendMail()
            return
        #os.system("tar -xzvf  %sbak/%s.tar.gz -C %s" %(dir,fileName,dir))
        #cmd = "xcopy  %sbak\\%s %s" %(dir,fileName,dir)
        cmd = "tar -xzvf  %sbak/%s.tar.gz -C %s" %(dir,fileName,dir)
        print cmd
        os.system(cmd)
        flag = 'True'
        statFile(dir,fileName,flag)


def handleFtpFile():
    #statFile('E:\\logs\\','djdiguaserverdcn_ex150303.log')
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (73,74,75,118,173,174,175,176,197,208,221) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] , localFile)
        print localFile, 'over'


def clearData():
    device_stat_count={}
    cretateTable()
    sql1 = "delete from  DIGUA_STAT_DEVICE_APACHE_TEMP where STAT_DATE=%s"
    dbUtil_168.delete(sql1, (createdDate,))
    sql1 = "truncate table  DIGUA_STAT_DEVICE_APACHE_TOP_200_TEMP"
    dbUtil_168.delete(sql1, ())
def cretateTable():
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="DIGUA_STAT_DEVICE_APACHE_TEMP"'
    count = dbUtil_168.queryCount(sql)
    if(count==0):
        sql = '''create table DIGUA_STAT_DEVICE_APACHE_TEMP
                (`ID` int(11) NOT NULL AUTO_INCREMENT,
                      `DEVICE` varchar(200) default null,
                      `COUNT` int(11) DEFAULT '0',
                      `STAT_DATE` datetime DEFAULT NULL,
                      PRIMARY KEY (`ID`),
                      KEY `IX_DIGUA_STAT_DEVICE_STAT_DATE` (`STAT_DATE`),
                      KEY `IX_DIGUA_STAT_DEVICE_DEVICE_NAME` (`DEVICE`)
                ) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''
        dbUtil_168.update(sql)
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="DIGUA_STAT_DEVICE_APACHE_TOP_200_TEMP"'
    count = dbUtil_168.queryCount(sql)
    if(count==0):
        sql = '''create table DIGUA_STAT_DEVICE_APACHE_TOP_200_TEMP
                (`ID` int(11) NOT NULL AUTO_INCREMENT,
                      `DEVICE` varchar(200) default null,
                      `COUNT` int(11) DEFAULT '0',
                      `STAT_DATE` datetime DEFAULT NULL,
                      PRIMARY KEY (`ID`),
                      KEY `IX_DIGUA_STAT_DEVICE_STAT_DATE` (`STAT_DATE`),
                      KEY `IX_DIGUA_STAT_DEVICE_DEVICE_NAME` (`DEVICE`)
                ) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''
        dbUtil_168.update(sql)
def insertIntoData():
    sql = "insert into DIGUA_STAT_DEVICE_APACHE_TEMP(DEVICE,COUNT,STAT_DATE) values (%s,%s,%s)"
    dataList = []
    sorted(device_stat_count.items(),key=lambda dsc:dsc[1],reverse=True)
    for row in device_stat_count.items():
        if not row:
            continue
        dataList.append((row[0],row[1],createdDate))
    if dataList:
        insertData(dbUtil_168, sql, dataList)
        dataList = []
def statDataTop200():
    sql = "insert into DIGUA_STAT_DEVICE_APACHE_TOP_200_TEMP(DEVICE,COUNT,STAT_DATE) select DEVICE,SUM(`COUNT`),%s FROM DIGUA_STAT_DEVICE_APACHE_TEMP" \
          " GROUP BY DEVICE ORDER BY SUM(`COUNT`) desc limit 200"
    dbUtil_168.update(sql,(handledate,))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print "=================start %s======" % datetime.datetime.now()
    opts = OptsUtil.getOpts(sys.argv)
    startDate = None
    interval_day = 1
    if not opts or not opts.get('--START_DATE'):
        startDate = datetime.datetime.strftime(datetime.datetime.today(),'%y%m%d')
        print startDate
    else:
        fileDate = opts.get('--START_DATE')
    if opts or opts.get('--INTERVAl_DAY'):
        interval_day = opts.get('--INTERVAl_DAY')
    try:
        begin = datetime.datetime.strptime(startDate, '%y%m%d')
        for i in range(int(interval_day)):
            fileDate = begin+datetime.timedelta(days=i)
            fileDate = datetime.date.strftime(fileDate, '%y%m%d')
            init(fileDate)
            #清理数据
            clearData()
            print 'clear data over %s' % fileDate
            #FTP获取日志文件，并进行数据插入
            handleFtpFile()
            print "stat file over %s"% datetime.datetime.now()
            insertIntoData()
            print "insert data over"
            i=i+1
        statDataTop200()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
           sendMail()
    print "=================end   %s======" % datetime.datetime.now()
