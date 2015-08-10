#!/usr/bin/python
#-*-#coding: cp936

'''
���������������ݱ����������Դid����Դ����ͳ��ĳ�������
'''
import re
import sys
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

download_stat_168 = DBUtil('download_stat_168')

#####�ʼ���������
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"������������".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"��׿������ͳ�ƴ�����Ϣ".encode("gbk")
mailTo=['zhou.wu@downjoy.com','guoqiang.sun@downjoy.com']
mailContents=u'Hi: \n'
#############################################
'''
fileDate ���ڶ���
'''
def handleData(fileDate):
    
    fileDateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    nextDateStr = datetime.datetime.strftime(fileDate + datetime.timedelta(days=1), '%Y-%m-%d')

    sql_clear="delete from ANDROID_GAME_DOWNLOAD_DAILY where CREATED_DATE = '%s'"%(fileDateStr)
    download_stat_168.delete(sql_clear)
    
    sqlLog="""select GAME_ID, RESOURCE_TYPE, CHANNEL_FLAG, count(ID) from ANDROID_GAME_DOWNLOAD_LOG
            force index(IX_ANDROID_LOG_CREATED_DATE, IX_ANDROID_LOG_GAME_ID)
           where CREATED_DATE >='%s' and CREATED_DATE<'%s' group by GAME_ID, CHANNEL_FLAG, RESOURCE_TYPE"""%(fileDateStr, nextDateStr)
    rows=download_stat_168.queryList(sqlLog)
    dataList=[]
    for row in rows:
        dataList.append((row[0], row[1], row[2], row[3], fileDateStr))
        if len(dataList) >= 1000:
            insertData(dataList)
            dataList = []
    if dataList and len(dataList) > 0:
        insertData(dataList)
        dataList = []

def insertData(dataList): 
    sql="insert into ANDROID_GAME_DOWNLOAD_DAILY(GAME_ID, RESOURCE_TYPE, CHANNEL_FLAG, DOWNS, CREATED_DATE) values(%s,%s,%s,%s,%s)"
    try:
        download_stat_168.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                download_stat_168.insert(sql, data)
            except:
                print data


def sendMail():
    global mailContents
    mailContents=(mailContents+u'������ͳ�ƽű�ִ�г���\n������Ϣ��%s\nлл'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#############################################
if __name__ == '__main__':
    print "android_download_log_to_daily_stat.py===start time %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
    try:
        #����
        today = datetime.datetime.today()
        #ǰ��
        day_before_yesterday = today - datetime.timedelta(days = 2)
        statDate = None #�ֶ������ʱ��
        opts = OptsUtil.getOpts(sys.argv)
        if opts and opts.get('--FILE_DATE'): 
            manualFileDate = opts.get('--FILE_DATE')
            pattern = re.compile("^\d{4}-\d{2}-\d{2}$")
            m=pattern.match(manualFileDate)
            if not m:
                print "invalid date format:%s , reset to the day before yesterday"%(manualFileDate)
                statDate = day_before_yesterday
            else:
                statDate = datetime.datetime.strptime(manualFileDate, '%Y-%m-%d')
        else:
            statDate = day_before_yesterday
        print "stat date : %s"%(datetime.datetime.strftime(statDate, "%Y-%m-%d"))
        handleData(statDate)
        
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: download_stat_168.close()
        if ERROR_MSG:
            sendMail()
    print "android_download_log_to_daily_stat.py=== end time %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
