#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/12/24 17:48:22 $"
#########################################################################################
#Android资讯点击量每日统计,获取7日内点击量前50入表droid_game.VIEWS_WEEKLY_NEWS_TOP50
#########################################################################################
import os
import sys
import time
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_35 = DBUtil('droid_game_10')
#获取日志产生时间
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"地瓜统计日志统计错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")

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
def statFile(fileName):
    # 如果该文件不存在，抛出异常
    print fileName
    if os.path.exists(fileName):
        print "======="
        f = open(fileName, 'rb')
        #资讯ID|资讯类型|点击时间
        sql = "insert into ANDROID_NEWS_VIEW_LOG_TEMP(NEWS_ID, NEWS_TYPE, CREATED_DATE) values (%s, %s, %s)"
        dataList = []
        while True:
            line = f.readline()
            if not line:
                break
            array = line.split('|')
            if len(array) != 4 or array[1] == 4177:
                continue
            try:
                dataList.append((array[1], array[2], array[0]))
            except:
                continue
            if len(dataList) >= 1000:
                insertData(dbUtil_168, sql, dataList)
                dataList = []
        if dataList:
            insertData(dbUtil_168, sql, dataList)
            dataList = []
        f.close()

def handleFtpFile():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (89,90,136,137) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] + localFile)
        print localFile, 'over'

def clearData():
    sql1 = "truncate ANDROID_NEWS_VIEW_LOG_TEMP"
    dbUtil_168.truncate(sql1, ())
    sql1 = "delete from ANDROID_NEWS_VIEW_DAILY where datediff(%s,STAT_DATE) = 0"
    dbUtil_168.delete(sql1, (handledate))

def insertLogs():
    sql = "insert into ANDROID_NEWS_VIEW_DAILY(news_id, cnt, stat_date) select news_id, count(*), created_date from ANDROID_NEWS_VIEW_LOG_TEMP where news_id!=4177 and news_id!=1470 group by news_id;"
    dbUtil_168.insert(sql, ())

def updateNewsTop50():
    sql = "select news_id, sum(cnt) as views from ANDROID_NEWS_VIEW_DAILY where datediff(%s, STAT_DATE)<7 AND datediff(%s, STAT_DATE) >= 0 group by news_id order by views desc limit 50"
    rows = dbUtil_168.queryList(sql, (handledate, handledate))
    datelist = []
    for row in rows:
        datelist.append((row[0], row[1]))
    sql = "truncate VIEWS_WEEKLY_NEWS_TOP50"
    dbUtil_35.truncate(sql, ())
    inserSql = "insert into VIEWS_WEEKLY_NEWS_TOP50(NEWS_ID, CNT) values(%s, %s)"
    insertData(dbUtil_35, inserSql, datelist)

def updateNewsViews():
    sql = "select cnt as views, news_id from ANDROID_NEWS_VIEW_DAILY where datediff(%s, STAT_DATE)=0"
    rows = dbUtil_168.queryList(sql, (handledate))
    datelist = []
    updatesql = "update NEWS set VIEWS=VIEWS+%s where ID=%s"
    for row in rows:
        dbUtil_35.update(updatesql, (row[0], row[1]))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        init()
        #清理数据
        clearData()
        print 'clear data over'
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
        insertLogs()
        updateNewsTop50()
        updateNewsViews()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_35: dbUtil_35.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()

