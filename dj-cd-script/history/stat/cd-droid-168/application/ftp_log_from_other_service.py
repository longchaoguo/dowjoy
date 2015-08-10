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
ERROR_MSG = ''
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("cp936")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"��־FTP�ű�����".encode("cp936")
mailTo = ['guoqiang.sun@downjoy.com','zhou.wu@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def init():
    global handledate,bakdate,antherhandledate,antherbakdate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
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
    fileName = srcFile%(handledate)
    rs = FtpUtil.getFile(srcDir, fileName, localDir, fileName, ip, port, username, password)
    if not rs:
        fileName=fileName+'.gz'
        rs = FtpUtil.getFile(srcDir, fileName, localDir, fileName, ip, port, username, password)
        if rs:
           os.system('gzip -d -f %s'%(localDir+"/"+fileName,))
    if not rs:
        fileName = srcFile%(antherhandledate)
        rs = FtpUtil.getFile(srcDir, fileName, localDir, fileName, ip, port, username, password)
    if not rs:
        fileName = srcFile%(antherhandledate)
        rs = FtpUtil.getFile(srcDir, fileName, localDir, fileName, ip, port, username2, password2)
    if not rs:
        fileName = srcFile%(antherhandledate)+'.gz'
        rs = FtpUtil.getFile(srcDir, fileName, localDir, fileName, ip, port, username2, password2)
        if rs:
           os.system('gzip -d -f %s'%(localDir+"/"+fileName,))
    if not rs:
         global ERROR_MSG
         ERROR_MSG = ERROR_MSG+u"\n�����ļ�%s,�ļ�������,Ŀ������%s,Ŀ���ļ���%s" %(fileName,ip,localFile)
         print 'down error'
    

def handleLogFile():
    sql="select ID, SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG  order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        src_dir = row[1];
        if str(row[0])=='144':
            src_dir = row[1] %(handledate[0:4],handledate[5:7])
        srcFile=row[2]%(handledate)
        localFile=row[4]%(handledate)
        bakFile=row[4]%(bakdate)
        antherbakFile=row[4]%(antherbakdate)
        bakDir=str(row[3])+"bak"
        if not os.path.exists(row[3] + localFile): # ���ļ���������ftp
            getFile(str(src_dir), row[2], str(row[3]), row[4], str(row[5]), int(row[6]))
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
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode("cp936")
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    mailContents = ''
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


