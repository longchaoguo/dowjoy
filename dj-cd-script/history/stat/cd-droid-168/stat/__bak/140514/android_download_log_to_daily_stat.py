#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2012/11/07 11:55:24 $"

import sys
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

dbUtil_168 = DBUtil('download_stat_168')
yesterdayStr=None
beforYesterdayStr=None

hadleDateFlagList=['10','20','40','41','50','51','60','61','70','71','80','81','90','91','100','101','110','111','120','121','130','131', '140']
beforHadleDateFlagList=['30']
#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject=u"安卓下载量天表统计错误信息".encode("gbk")
mailTo=['lin.he@downjoy.com']
mailContents=u'Hi: \n'
#############################################
def init():
    global yesterdayStr,beforYesterdayStr
    opts=OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):# raise Exception, 'can not find the datetime params!'
        fileDate=datetime.datetime.strftime(datetime.datetime.today()-datetime.timedelta(days=1),'%Y-%m-%d')
    else:
        fileDate=opts.get('--FILE_DATE')
    print fileDate
    yesterdayStr = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    beforYesterdayStr=datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d')-datetime.timedelta(days=1),'%Y-%m-%d')

def handleData(day, channelFlagList):
    nextDay=getNextDay(day)
    channelFlags=','.join(channelFlagList)
    sqlLog="""
    select GAME_ID, CHANNEL_FLAG, RESOURCE_TYPE, count(ID) 
    from ANDROID_GAME_DOWNLOAD_LOG
      force index(IX_ANDROID_LOG_CREATED_DATE, IX_ANDROID_LOG_GAME_ID)
    where CREATED_DATE >='%s' and CREATED_DATE<'%s' and CHANNEL_FLAG in (%s)
    group by GAME_ID, CHANNEL_FLAG, RESOURCE_TYPE
    """%(day, nextDay, channelFlags)
    rows=dbUtil_168.queryList(sqlLog, ())
    print 'get %s data (%s)'%(day, datetime.datetime.now())
    dataList=[]
    for row in rows:
        dataList.append((row[0], row[2], row[1], row[3], day))
    sqlDaily="insert into ANDROID_GAME_DOWNLOAD_DAILY(GAME_ID, RESOURCE_TYPE, CHANNEL_FLAG, DOWNS, CREATED_DATE) values(%s,%s,%s,%s,%s)"
    for dataTuple in dataList:
        dbUtil_168.insert(sqlDaily, dataTuple)

def clearData(day, channelFlagList):
    channelFlags=','.join(channelFlagList)
    nextDate=datetime.datetime.strftime(datetime.datetime.strptime(day, '%Y-%m-%d')+datetime.timedelta(days=1), '%Y-%m-%d')
    sql1="delete from ANDROID_GAME_DOWNLOAD_DAILY where CREATED_DATE >= '%s' and CREATED_DATE < '%s' and CHANNEL_FLAG in (%s)"%(day, nextDate, channelFlags)
    dbUtil_168.delete(sql1, ())

def sendMail():
    global mailContents
    mailContents=(mailContents+u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢'%(datetime.datetime.today(), yesterdayStr, ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

def getNextDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr)+datetime.timedelta(days=1), formatStr)
#############################################
if __name__ == '__main__':
    try:
        init()
        ###############操作前天地瓜的数据##############################
        clearData(beforYesterdayStr, beforHadleDateFlagList)
        print beforYesterdayStr,'digua clear'
        handleData(beforYesterdayStr, beforHadleDateFlagList)
        print beforYesterdayStr, 'digua over'
        ###############操作昨天的数据#######################
        clearData(yesterdayStr, hadleDateFlagList)
        print yesterdayStr, 'data clear'
        handleData(yesterdayStr, hadleDateFlagList)
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
            sendMail()
