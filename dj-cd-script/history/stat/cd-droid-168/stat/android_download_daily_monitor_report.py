#/usr/bin/python
# -*- #coding:cp936

#########################################
import re
import datetime
import sys
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

#########################################
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))

droid_game_10 = DBUtil('droid_game_10')
download_stat_168 = DBUtil('download_stat_168')

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"��׿������(��ʷ��_�ܱ�_�±�_GAME��)ͳ�ƴ�����Ϣ".encode("gbk")
mailTo = ['zhou.wu@downjoy.com','guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
#########################################
'''
@param dayStr: yyyy-MM-dd��ʽ�������ַ���
'''
def statHistory(dayStr):
    sqlDel = "delete from ANDROID_GAME_DOWNLOAD_HISTORY where STAT_DATE='%s'" %(dayStr)
    download_stat_168.delete(sqlDel)
    sql = """select CHANNEL_FLAG, RESOURCE_TYPE, sum(DOWNS) from ANDROID_GAME_DOWNLOAD_DAILY 
             where CREATED_DATE='%s' group by CHANNEL_FLAG, RESOURCE_TYPE""" % (dayStr)
    rows = download_stat_168.queryList(sql)
    sqlHistory = "insert into ANDROID_GAME_DOWNLOAD_HISTORY(CHANNEL_FLAG, TYPE, DOWNS, STAT_DATE) values(%s,%s,%s,%s)"
    for row in rows:
        download_stat_168.insert(sqlHistory, (row[0], row[1], row[2], dayStr))

'''
@param dayStr: yyyy-MM-dd��ʽ�������ַ���
'''
def statWeeklyAndMonthly(dayStr):
    weekFirstDay = getWeekFirstDay(dayStr)
    weekLastDay = getWeekLastDay(dayStr)
    statRangeData(weekFirstDay,weekLastDay,"ANDROID_DOWNLOAD_WEEKLY_SUM")
    print 'week data over'
    monthFirstDay = getMonthFirstDay(dayStr)
    monthLastDay = getMonthLastDay(dayStr)
    statRangeData(monthFirstDay,monthLastDay,"ANDROID_DOWNLOAD_MONTHLY_SUM")
    print 'month data over'

def statRangeData(startDateStr,endDateStr,tableName):
    sqldel = '''delete from '''+tableName+''' where STAT_DATE = %s'''%startDateStr
    sql = """select GAME_ID, CHANNEL_FLAG, sum(DOWNS) from ANDROID_GAME_DOWNLOAD_DAILY 
             where CREATED_DATE >= '%s' and CREATED_DATE <= '%s' 
             group by GAME_ID, CHANNEL_FLAG""" % (startDateStr, endDateStr)
    rows = download_stat_168.queryList(sql)
    tempDataList = []
    for row in rows:
        tempDataList.append((row[0], row[1], row[2], startDateStr))
        if len(tempDataList) >= 1000:
            addRangeData(tempDataList,tableName)
            tempDataList = []
    if tempDataList and len(tempDataList) > 0:
        addRangeData(tempDataList,tableName)
        tempDataList = []

def addRangeData(dataList,tableName): 
    sql = "insert into "+tableName+"(GAME_ID, CHANNEL_FLAG, DOWNS, STAT_DATE) values(%s,%s,%s,%s)"
    try:
        download_stat_168.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                download_stat_168.insert(sql, data)
            except:
                print data

'''
@param dayStr: yyyy-MM-dd��ʽ�������ַ���
'''
def statGame(dayStr):
    sql = """select GAME_ID, sum(DOWNS) from ANDROID_GAME_DOWNLOAD_DAILY where CREATED_DATE = '%s' group by GAME_ID""" % (dayStr)
    rows = download_stat_168.queryList(sql)
    sqlUpdate = "update GAME set DOWNS = DOWNS + %s where ID = %s"
    for row in rows:
        droid_game_10.update(sqlUpdate, (row[1], row[0]))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), handledate, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

##############################


def getNextDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr) + datetime.timedelta(days=1), formatStr)

'''
��ȡ�����������ڵĵ�һ�죨����һ��
'''
def getWeekFirstDay(crtDayStr, formatStr='%Y-%m-%d'):
    crtDay = datetime.datetime.strptime(crtDayStr, formatStr) 
    days = crtDay.weekday()
    return datetime.datetime.strftime(crtDay - datetime.timedelta(days=days), formatStr)
'''
��ȡ�����������ڵ����һ�죨�����죩
'''
def getWeekLastDay(crtDayStr, formatStr='%Y-%m-%d'):
    crtDay = datetime.datetime.strptime(crtDayStr, formatStr) 
    days = 6-crtDay.weekday()
    return datetime.datetime.strftime(crtDay + datetime.timedelta(days=days), formatStr)

'''
��ȡ���������µĵ�һ��
@param crtDayStr: yyyy-MM-dd��ʽ������
'''
def getMonthFirstDay(crtDayStr):
    crtDay = datetime.datetime.strptime(crtDayStr, '%Y-%m-%d') 
    oneday = datetime.timedelta(days=1)
    days = [datetime.date(crtDay.year, crtDay.month, 1),]
    for x in xrange(32):
        d = days[0]+x*oneday
        if d.month == days[0].month:
            days.append(d)
    return "%s-%s-%s"%(crtDay.year, crtDay.month, days[0].day)
'''
��ȡ���������µ����һ��
@param crtDayStr: yyyy-MM-dd��ʽ������
'''
def getMonthLastDay(crtDayStr):
    crtDay = datetime.datetime.strptime(crtDayStr, '%Y-%m-%d') 
    oneday = datetime.timedelta(days=1)
    days = [datetime.date(crtDay.year, crtDay.month, 1),]
    for x in xrange(32):
        d = days[0]+x*oneday
        if d.month == days[0].month:
            days.append(d)
    return "%s-%s-%s"%(crtDay.year, crtDay.month, days[-1].day)

##############################
if __name__ == '__main__':
    print "android_download_daily_monitor_report.py==========start %s========"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
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
            if m:
                statHistory(manualFileDate)
                print 'stat %s history over' % manualFileDate
                statWeeklyAndMonthly(manualFileDate)
                print 'stat %s weekly and monthly over' % manualFileDate
                #����ֶ������˲����������϶�����Ϊͳ�Ƴ������ĳ��ԭ�����ﲻִ��statGame(),��ֹ�ظ�ͳ��
            else:
                print "dateformat is invalid:%s"%manualFileDate
        else:
            fileDateStr = datetime.datetime.strftime(day_before_yesterday, "%Y-%m-%d")
            statGame(fileDateStr)
            print 'stat %s game over' % fileDateStr
            statHistory(fileDateStr)
            print 'stat %s history over' % fileDateStr
            statWeeklyAndMonthly(fileDateStr)
            print 'stat %s weekly and monthly over' % fileDateStr

    except Exception , ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: download_stat_168.close()
        if droid_game_10: droid_game_10.close()
        if ERROR_MSG:
            sendMail()
    print "android_download_daily_monitor_report.py==========end   %s========"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
