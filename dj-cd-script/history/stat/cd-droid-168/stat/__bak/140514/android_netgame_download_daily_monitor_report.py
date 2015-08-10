#/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.12 $"
__date__ = "$Date: 2013/09/27 02:40:15 $"
#########################################
#ÿ�췢�� ������android_download_daily_stat.py�ű�(crontab: ÿ��6��)
#########################################
import datetime
import sys
import xlwt
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

#########################################
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
beforHandledate = None

hadleDateFlagList = ['10','50','70','100']
beforHadleDateFlagList = ['30']
dbUtil_10 = DBUtil('droid_game_10')
dbUtil_168 = DBUtil('download_stat_168')

sqlStoreWeekFile = '/opt/logs/stat/android_netgame_weekly_save_data_%s.txt'
sqlStoreMonthFile = '/opt/logs/stat/android_netgame_monthly_save_data_%s.txt'
sqlStoreGameFile = '/opt/logs/stat/android_netgame_save_data_%s.txt'
#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"��׿����������(��ʷ��_�ܱ�_�±�_GAME��)ͳ�ƴ�����Ϣ".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
#########################################
def init():
    global handledate, beforHandledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'): #raise Exception, 'can not find the datetime params!'
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d")
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    beforHandledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d') - datetime.timedelta(days=1), "%Y-%m-%d")

def statHistory(day, channelFlagList):
    channelFlags = ','.join(channelFlagList)
    nextDay = getNextDay(day)
    sqlDel = "delete from ANDROID_NETGAME_DOWNLOAD_HISTORY where STAT_DATE>='%s' and STAT_DATE<'%s' and CHANNEL_FLAG in (%s)" % (day, nextDay, channelFlags)
    dbUtil_168.delete(sqlDel, ())
    sql = "select CHANNEL_FLAG, RESOURCE_TYPE, sum(DOWNS) from ANDROID_NETGAME_DOWNLOAD_DAILY where CREATED_DATE>='%s' and CREATED_DATE<'%s' and CHANNEL_FLAG in (%s) group by CHANNEL_FLAG, RESOURCE_TYPE" % (day, nextDay, channelFlags)
    rows = dbUtil_168.queryList(sql, ())
    sqlHistory = "insert into ANDROID_NETGAME_DOWNLOAD_HISTORY(CHANNEL_FLAG, DOWNS, TYPE, STAT_DATE) values(%s,%s,%s,%s)"
    for row in rows:
        dbUtil_168.insert(sqlHistory, (row[0], row[2], row[1], day))
    
def statWeeklyAndMonthly(day, channelFlagList):
    nextDay = getNextDay(day)
    last6Day = getLast6Day(day)
    monthFirstDay = getMonthFirstDay(day)
    weekFirstDay = getWeekFirstDay(day)
    channelFlags = ','.join(channelFlagList)
    sql = "select CHANNEL_ID, CHANNEL_FLAG, sum(DOWNS) from ANDROID_NETGAME_DOWNLOAD_DAILY where CREATED_DATE >= '%s' and CREATED_DATE < '%s' and CHANNEL_FLAG in (%s) group by CHANNEL_ID, CHANNEL_FLAG" % (day, nextDay, channelFlags)
    rows = dbUtil_168.queryList(sql, ())
    insertSumData(rows, 'ANDROID_NETGAME_DOWNLOAD_WEEKLY_SUM_TEMP', 'ANDROID_NETGAME_DOWNLOAD_WEEKLY_SUM', weekFirstDay, sqlStoreWeekFile % day)
    print 'week data over'
    insertSumData(rows, 'ANDROID_NETGAME_DOWNLOAD_MONTHLY_SUM_TEMP', 'ANDROID_NETGAME_DOWNLOAD_MONTHLY_SUM', monthFirstDay, sqlStoreMonthFile % day)
    print 'month data over'

def insertSumData(rows, TABLE_TEMP, TABLE, day, saveFile): 
    sqlDataTempDel = "truncate table %s" % TABLE_TEMP
    dbUtil_168.delete(sqlDataTempDel, ())
    sqlData = "insert into " + TABLE_TEMP + " select * from " + TABLE + " where STAT_DATE = %s"
    dbUtil_168.insert(sqlData, (day))
    f = open(saveFile , 'ab')
    f.write('---------------------\n')
    for row in rows:
        channelId = row[0]
        channelFlag = row[1]
        f.write(str(channelId) + ',' + str(channelFlag) + ',' + str(row[2]) + ',' + day + '\n')
        sqlExist = "select ID from " + TABLE_TEMP + " where CHANNEL_ID=%s and STAT_DATE=%s and CHANNEL_FLAG=%s"
        id = dbUtil_168.queryRow(sqlExist, (channelId, day, channelFlag))
        if not id or not id[0]:
            sqlInsert = "insert into " + TABLE_TEMP + "(CHANNEL_ID, CHANNEL_FLAG, DOWNS, STAT_DATE) values(%s,%s,%s,%s)"
            dbUtil_168.insert(sqlInsert, (channelId, channelFlag, row[2], day))
        else:
            sqlUpdate = "update " + TABLE_TEMP + " set DOWNS=DOWNS+%s where ID=%s"
            dbUtil_168.update(sqlUpdate, (row[2], id[0]))
    f.write('insert done\n')
    f.close()
    sqlDel = "delete from " + TABLE + " where STAT_DATE = %s"
    dbUtil_168.delete(sqlDel, (day))
    sqlTo = "insert into " + TABLE + " (CHANNEL_ID, CHANNEL_FLAG, DOWNS, STAT_DATE) select CHANNEL_ID, CHANNEL_FLAG, DOWNS, STAT_DATE from " + TABLE_TEMP 
    dbUtil_168.insert(sqlTo, ())

def statGame(day, channelFlagList):
    nextDay = getNextDay(day)
    channelFlags = ','.join(channelFlagList)
    sql = "select CHANNEL_ID, sum(DOWNS) from ANDROID_NETGAME_DOWNLOAD_DAILY where CREATED_DATE >= '%s' and CREATED_DATE < '%s' and CHANNEL_FLAG in (%s) group by CHANNEL_ID" % (day, nextDay, channelFlags)
    rows = dbUtil_168.queryList(sql, ())
    sqlUpdate = "update NETGAME_CHANNEL set DOWNS = DOWNS + %s where ID = %s"
    f = open(sqlStoreGameFile % day, 'ab')
    f.write('----%s----\n' % str(channelFlagList))
    for row in rows:
        dbUtil_10.update(sqlUpdate, (row[1], row[0]))
        f.write(str(row[1]) + ',' + str(row[0]) + '\n')
    f.close()

def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

##############################
def getMonthFirstDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr).replace(day=1), formatStr)

def getNextMonthFirstDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime((datetime.datetime.strptime(dayStr, formatStr) + datetime.timedelta(days=31)).replace(day=1), formatStr)

def getNextDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr) + datetime.timedelta(days=1), formatStr)

def getLast6Day(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr) - datetime.timedelta(days=6), formatStr)

def getWeekFirstDay(crtDayStr, formatStr='%Y-%m-%d'): #��һ
    crtDay = datetime.datetime.strptime(crtDayStr, formatStr) 
    days = crtDay.weekday()
    return datetime.datetime.strftime(crtDay - datetime.timedelta(days=days), formatStr)
##############################
if __name__ == '__main__':
    print "==========start %s========" % datetime.datetime.now()
    try:
        init()
        ################ͳ��ǰ��ع�������HISTORY\��\�±�##########################
        #statHistory(beforHandledate, beforHadleDateFlagList)
        #print '%s history over' % beforHandledate
        #statWeeklyAndMonthly(beforHandledate, beforHadleDateFlagList)
        #statGame(beforHandledate, beforHadleDateFlagList)
        #print '%s game over' % beforHandledate
        ################ͳ��������������##########################
        statHistory(handledate, hadleDateFlagList)
        print '%s history over' % handledate
        statWeeklyAndMonthly(handledate, hadleDateFlagList)
        statGame(handledate, hadleDateFlagList)
        print '%s game over' % handledate
    except Exception , ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()
        if ERROR_MSG:
            sendMail()
    print "==========end   %s========" % datetime.datetime.now()
