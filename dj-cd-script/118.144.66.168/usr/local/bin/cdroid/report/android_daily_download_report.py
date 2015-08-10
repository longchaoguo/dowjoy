#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: guoqiang.sun$"
################################################
#功能描述：android下载信息报表 并发发送邮件
################################################
import  sys
import re
import os
import datetime
import urllib
import xlwt
import xlrd
import traceback
import smtplib
import email
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
import calendar
REPORT_DATE = datetime.datetime.today()
REPORT_DATA_STR = datetime.datetime.strftime(REPORT_DATE, '%Y-%m-%d')
#数据库连接
dbUtil_168 = DBUtil('droid_stat_168')
fileDir = "/usr/local/bin/cdroid/report/data/"
#fileDir="e:/logs/"
REPORT_NAME=None
REPORT_FILE = None
#mailToUsers = ["jacky@downjoy.com","dong.wei@downjoy.com","fan.zhang@downjoy.com"]
MAIL_TO_USERS = None
WORKBOOK = None
def init(reportName=None,reportDate=None,mailToUsers=[]):
    global REPORT_NAME,REPORT_DATE,REPORT_FILE,REPORT_DATA_STR,MAIL_TO_USERS,WORKBOOK
    if reportDate:
        REPORT_DATE = datetime.datetime.strptime(reportDate,'%Y%m%d')
    REPORT_DATA_STR = datetime.datetime.strftime(REPORT_DATE, '%Y-%m-%d')
    REPORT_NAME = reportName
    REPORT_FILE =  fileDir + "%s_%s.xls"%(REPORT_NAME,REPORT_DATA_STR)
    MAIL_TO_USERS = mailToUsers
    WORKBOOK = xlwt.Workbook(encoding='gbk')


def writeFile(titles=[],datas=()):
    '''写sheet1工作表'''
    sheet = WORKBOOK.add_sheet(REPORT_NAME, cell_overwrite_ok=True)
    sheet.write(0, 0, u'统计日期')
    sheet.write(0, 1, REPORT_DATA_STR)
    sheet.write(1,0,u"序号")
    i = 1;
    for title in titles:
        sheet.write(1,i,title)
        i = i+1
    i = 2
    #print sql
    for cols in datas:
        sheet.write(i, 0, i-1)
        j = 1
        for col in cols:
            if isinstance(col,(datetime.datetime)):
                col = str(col)
            sheet.write(i,j,col)
            j = j+1
        i = i+1
    WORKBOOK.save(REPORT_FILE)

#发送附件邮件
def sendmail(reportFile=None):
    global REPORT_FILE
    if reportFile:
        REPORT_FILE = reportFile
    body = "您好：<br>%s，见附件<br>如有需求和问题，请和孙国强联系。" %(REPORT_NAME,)
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("guoqiang.sun@downjoy.com","Pa12345678")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(body, 'html', 'gbk')
    main_msg.attach(text_msg)
    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)
    data = open(REPORT_FILE, 'rb')
    file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
    file_msg.set_payload(data.read( ))
    data.close( )
    email.Encoders.encode_base64(file_msg)
    basename = os.path.basename(REPORT_FILE)
    file_msg.add_header('Content-Disposition','attachment', filename = basename)
    main_msg.attach(file_msg)
    main_msg['From'] = "webmaster@downjoy.com"
    main_msg['To'] = ', '.join(MAIL_TO_USERS)
    main_msg['Subject'] = ("%s_%s.xls" % (REPORT_NAME,REPORT_DATA_STR))
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("guoqiang.sun@downjoy.com", MAIL_TO_USERS, fullText)
    finally:
        server.quit()
'''
统计下载量
'''
def stat_android_download(handleDate):
    handleDate_str = datetime.datetime.strftime(handleDate,'%Y%m%d')
    init("总下载量报表",handleDate_str,["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    cal = calendar.month(handleDate.year,handleDate.month)
    values = week_get(handleDate)
    sql = '''select a.*,b.BT_TOTAL from (SELECT STAT_DATE,SUM(COUNT) AS `total` FROM ANDROID_DAILY_DOWNLOAD_STAT WHERE STAT_DATE>='%s' and STAT_DATE<='%s'  GROUP BY STAT_DATE)a
            INNER JOIN (SELECT STAT_DATE,SUM(COUNT) AS `BT_TOTAL` FROM ANDROID_DAILY_DOWNLOAD_STAT WHERE STAT_DATE>='%s' AND STAT_DATE<='%s' AND DATATYPE=2  GROUP BY STAT_DATE )b
            on a.STAT_DATE=b.STAT_DATE; ''' %(values[0],values[1],values[0],values[1])
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'日期',u'总下载量',u'BT下载量'],rows)
    sendmail()
'''
按资源类型统计下载量
'''
def stat_android_download_by_catergory(handleDate):
    handleDate_str = datetime.datetime.strftime(handleDate,'%Y%m%d')
    init("按资源类型统计下载量报表",handleDate_str,["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    cal = calendar.month(handleDate.year,handleDate.month)
    values = week_get(handleDate)
    sql = '''SELECT STAT_DATE,RESOURCECATERGORY,SUM(COUNT) AS `total` FROM ANDROID_DAILY_DOWNLOAD_STAT WHERE STAT_DATE>='%s' AND STAT_DATE<='%s'
     GROUP BY STAT_DATE,RESOURCECATERGORY; ''' %(values[0],values[1])
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'日期',u'资源类型',u'下载量'],rows)
    sendmail()
def stat_android_download_by_channel(handleDate):
    handleDate_str = datetime.datetime.strftime(handleDate,'%Y%m%d')
    init("按渠道统计下载量报表",handleDate_str,["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    cal = calendar.month(handleDate.year,handleDate.month)
    values = week_get(handleDate)
    sql = '''SELECT STAT_DATE,CHANNELID,SUM(COUNT) AS `total` FROM ANDROID_DAILY_DOWNLOAD_STAT WHERE STAT_DATE>='%s' AND STAT_DATE<='%s'
     GROUP BY STAT_DATE,CHANNELID; ''' %(values[0],values[1])
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'日期',u'渠道编号',u'下载量'],rows)
    sendmail()
def stat_android_download_detail(handleDate):
    handleDate_str = datetime.datetime.strftime(handleDate,'%Y%m%d')
    init("按游戏统计下载量报表",handleDate_str,["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    cal = calendar.month(handleDate.year,handleDate.month)
    values = week_get(handleDate)
    sql = '''SELECT STAT_DATE,GAMEID,GAMENAME,RESOURCECATERGORY,GAMETYPE ,SUM(COUNT) AS `total` FROM ANDROID_DAILY_DOWNLOAD_STAT  WHERE STAT_DATE>='%s' AND STAT_DATE<='%s'
     GROUP BY STAT_DATE, GAMEID ; ''' %(values[0],values[1])
    rows = dbUtil_168.queryList(sql,())
    global REPORT_NAME
    i = 0
    while len(rows)>60000:
         writeFile([u'日期',u'资源id',u'资源名称',u'资源分类',u'资源类型',u'下载量'],rows[:60000])
         rows=rows[60000:]
         REPORT_NAME = REPORT_NAME+str(i)
         i=i+1
    if len(rows)>0:
        writeFile([u'日期',u'资源id',u'资源名称',u'资源分类',u'资源类型',u'下载量'],rows)
    sendmail()

def day_get(d):
    oneday = datetime.timedelta(days=1)
    day = d - oneday
    date_from = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    date_to = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
    return [date_from,date_to]

def week_get(d):
    dayscount = datetime.timedelta(days=d.isoweekday())
    dayto = d - dayscount
    sixdays = datetime.timedelta(days=6)
    dayfrom = dayto - sixdays
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    return [date_from,date_to]

def month_get(d):
    dayscount = datetime.timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    return [date_from,date_to]
mailServer_ = "mail.downjoy.com"
mailFromName_ = u"当乐数据中心".encode("cp936")
mailFromAddr_ = "webmaster@downjoy.com"
mailLoginUser_ = "webmaster@downjoy.com"
mailLoginPass_ = "htbp3dQ1sGcco!q"
mailSubject_ = u"android下载信息报表统计错误信息".encode("cp936")
mailTo_ = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
def sendMail(mailContents=None):
    try:
        mail = MailUtil(None, mailServer_,mailFromName_, mailFromAddr_,['guoqiang.sun@downjoy.com'],mailLoginUser_,mailLoginPass_,mailSubject_)
        mail.sendMailMessage(mailContents)
    except Exception, e:
        traceback.print_exc()
        print e.message
if __name__ == '__main__':
    opts = OptsUtil.getOpts(sys.argv)
    fileDate = None
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
    else:
        fileDate = opts.get('--FILE_DATE')
    handleDate = datetime.datetime.strptime(fileDate, '%Y-%m-%d')
    try:
        stat_android_download(handleDate)
        stat_android_download_by_channel(handleDate)
        stat_android_download_by_catergory(handleDate)
        stat_android_download_detail(handleDate)
    except Exception, e:
        traceback.print_exc()
        sendMail(e.message)