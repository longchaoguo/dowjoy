#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/12/24 17:48:22 $"
###########################
#Android专题点击量每日统计
###########################
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
SPECIAL_TOPIC_VIEWS_LIST={}

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"Android专题点击量统计错误信息".encode("gbk")
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

def statFile(fileName):
    # 如果该文件不存在，抛出异常
    print fileName
    if os.path.exists(fileName):
        print "======="
        f = open(fileName, 'rb')
        dataList = []
        while True:
            line = f.readline()
            if not line:
                break
            array = line.split('|')
            if len(array) != 4:
                continue
            specialTopicId = str(array[1])
            #print specialTopicId
            if not SPECIAL_TOPIC_VIEWS_LIST.has_key(specialTopicId):
                SPECIAL_TOPIC_VIEWS_LIST[specialTopicId] = 0
            SPECIAL_TOPIC_VIEWS_LIST[specialTopicId] = SPECIAL_TOPIC_VIEWS_LIST[specialTopicId]+1
        f.close()

def handleFtpFile():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (92,93,94,125,140,141,142,143) order by ID;"
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

def updateViews():
    updatesql = "update SPECIAL_TOPIC set VIEWS=VIEWS+%s where ID=%s"
    for k, v in SPECIAL_TOPIC_VIEWS_LIST.items():
        #print k
        #print updatesql%(str(v),k) 
        if k == '507':
            continue
        dbUtil_35.update(updatesql, (v, k))

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
        #FTP获取日志文件，并进行数据插入
        handleFtpFile()
        updateViews()
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

