#!/usr/bin/python
#-*-#coding: cp936

'''
从下载量基础数据表分渠道、资源id、资源类型统计某天的数据
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

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"安卓下载量统计错误信息".encode("gbk")
mailTo=['zhou.wu@downjoy.com','guoqiang.sun@downjoy.com']
mailContents=u'Hi: \n'
#############################################
'''
fileDate 日期对象
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
    mailContents=(mailContents+u'下载量统计脚本执行出错，\n错误信息：%s\n谢谢'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#############################################
if __name__ == '__main__':
    print "android_download_log_to_daily_stat.py===start time %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
    try:
        #今天
        today = datetime.datetime.today()
        #前天
        day_before_yesterday = today - datetime.timedelta(days = 2)
        statDate = None #手动传入的时间
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
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: download_stat_168.close()
        if ERROR_MSG:
            sendMail()
    print "android_download_log_to_daily_stat.py=== end time %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
