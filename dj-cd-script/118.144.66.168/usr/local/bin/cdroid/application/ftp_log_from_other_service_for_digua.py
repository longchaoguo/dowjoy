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
import ftplib
import StringIO
import traceback
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
#��ȡ��־����ʱ��
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
#��־���Ŀ¼
username = "ftpdownjoy"
password = "djftp119"
username2 = "downlog"
password2 = "ftp119@1104>data"
#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"��־FTP�ű�����".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate,bakdate,antherhandledate,antherbakdate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    bakdate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d') - datetime.timedelta(days = 2), "%Y-%m-%d")
    antherhandledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%y%m%d")
    antherbakdate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d') - datetime.timedelta(days = 2), "%y%m%d")

#FTP������־�ļ�
def getFile(srcDir, srcFile, localDir, localFile, ip, port):
    if not os.path.exists(localDir):
        os.makedirs(localDir)
    fileName = localFile%(handledate)
    print localFile
    print fileName
    rs = FtpUtil.getFile(srcDir, srcFile, localDir, fileName, ip, port, username, password)

def handleLogFile():
    sql="select ID, SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in  (169,170,171,172,207,227) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[2]
        localFile=row[4]%(handledate)
        bakFile=row[4]%(bakdate)
        antherbakFile=row[4]%(antherbakdate)
        bakDir=str(row[3])+"bak"
        print os.path.exists(row[3] + localFile)
        if not os.path.exists(row[3] + localFile): # ���ļ���������ftp
            print localFile
            print "============="
            getFile(str(row[1]), row[2], str(row[3]), row[4], str(row[5]), int(row[6]))
        print '%s %s ftp over!' % (row[3], srcFile)
        if os.path.exists(row[3] + bakFile): # ���ļ�������gzip��ɾ��Դ�ļ�
            if not os.path.exists(bakDir):
                os.makedirs(str(bakDir))
            cmdstr="cd %s && tar -zcvf bak/%s.tar.gz %s && rm %s"%(str(row[3]), bakFile, bakFile, bakFile)
            os.system(cmdstr)
        if os.path.exists(row[3] + antherbakFile): # ���ļ�������gzip��ɾ��Դ�ļ�
            if not os.path.exists(bakDir):
                os.makedirs(str(bakDir))
            cmdstr="cd %s && tar -zcvf bak/%s.tar.gz %s && rm %s"%(str(row[3]), antherbakFile, antherbakFile, antherbakFile)
            os.system(cmdstr)
        time.sleep(1)
        print srcFile, 'over'


def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        #��ʼ��
        init()
        #��־�ļ���ش���
        handleLogFile()
        #ѹ���Ѵ�����־�ļ�

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
    print "=================end   %s======" % datetime.datetime.now()


