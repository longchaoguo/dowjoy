#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/12/26 17:48:22 $"
########################
#�ع��û��������¶�ͳ��
########################
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

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"�ع�ͳ����־ͳ�ƴ�����Ϣ".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 10), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m")

def clearData():
    sql1 = "delete from DIGUA_USER_RETENTION_MONTH_STAT_APACHE_NOT_MAC where date_format(stat_date, '%Y-%m')='"+handledate+"'"
    dbUtil_168.delete(sql1, ())

def insertMonthData():
    sql = "select count(imei) from (select imei from DIGUA_STAT_USER_LOG_APACHE_NOT_MAC where date_format(created_date, '%Y-%m')='"+handledate+"' group by IMEI) T"
    logCnt = dbUtil_168.queryCount(sql, ())
    sql = "select count(imei) from DIGUA_USER_APACHE_NOT_MAC where date_format(created_date, '%Y-%m')='"+handledate+"'"
    addedCnt = dbUtil_168.queryCount(sql, ())
    sql = "insert into DIGUA_USER_RETENTION_MONTH_STAT_APACHE_NOT_MAC(LOGIN_CNT, ADDED_CNT, STAT_DATE) values(%s, %s, %s)"
    dbUtil_168.insert(sql, (logCnt, addedCnt, handledate+"-01"))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        init()
        #��������
        clearData()
        print 'clear data over'
        #��ȡ�¶ȵع��û����ݲ����
        insertMonthData()
        print 'insert month data over'

    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
            sendMail()
    print "=================end  %s======" % datetime.datetime.now()

