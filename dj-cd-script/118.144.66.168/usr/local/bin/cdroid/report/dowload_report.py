#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: guoqiang.sun$"
################################################
#功能描述：根据2-3月的下载明细数据，统计报表（BT下载报表，top20报表，新游戏下载top20）并发发送邮件
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

def top3Month20Download():
    init("2015年3月份下载top20报表","20150331",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''SELECT C.*,B.pc from (select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
        where TIME<='2015-03-31 23:59:59' and TIME>='2015-03-01 00:00:00' GROUP BY GAMEID ORDER BY c desc LIMIT 20)C
        LEFT JOIN (SELECT GAMEID,GAMENAME,COUNT(GAMEID)as pc from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG where
         TIME<='2015-02-28 23:59:59' and TIME>='2015-02-01 00:00:00' GROUP BY GAMEID )B   on B.GAMEID=C.GAMEID '''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量',u'上月下载量'],rows)
    sendmail()
def top2Month20Download():
    init("2015年2月份下载top20报表","20150228",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where TIME<='2015-02-28 23:59:59' and TIME>='2015-02-01 00:00:00' GROUP BY GAMEID ORDER BY c desc LIMIT 20'''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
def top3MonthBTDownload():
    init("2015年3月份BT下载报表","20150331",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where TIME<='2015-03-31 23:59:59' and TIME>='2015-03-01 00:00:00' and DATATYPE='2' GROUP BY GAMEID '''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
def top2MonthBTDownload():
    init("2015年2月份BT下载报表","20150228",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where TIME<='2015-02-28 23:59:59' and TIME>='2015-02-01 00:00:00' and DATATYPE='2' GROUP BY GAMEID'''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
def top3NewGameMonth20Download():
    init("2015年3月份新游戏下载top20报表","20150331",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where TIME<='2015-03-31 23:59:59' and TIME>='2015-03-01 00:00:00' and MONTH(GAMEONLINETIME)=3  GROUP BY GAMEID ORDER BY c desc LIMIT 20'''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
def top2NewGameMonth20Download():
    init("2015年2月份新游戏下载top20报表","20150228",["guoqiang.sun@downjoy.com","chaoguo.long@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,COUNT(GAMEID) as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where TIME<='2015-02-28 23:59:59' and TIME>='2015-02-01 00:00:00' and MONTH(GAMEONLINETIME)=2  GROUP BY GAMEID ORDER BY c desc LIMIT 20;
'''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
def test():
    init("2015年2月份新游戏下载top20报表","20150228",["guoqiang.sun@downjoy.com"])
    sql = '''select GAMEID,GAMENAME,id as c from ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG
where  MONTH(GAMEONLINETIME)=2 limit 1;
'''
    rows = dbUtil_168.queryList(sql,())
    writeFile([u'游戏ID',u'游戏名称',u'本月下载量'],rows)
    sendmail()
mailServer_ = "mail.downjoy.com"
mailFromName_ = u"当乐数据中心".encode("cp936")
mailFromAddr_ = "guoqiang.sun@downjoy.com"
mailLoginUser_ = "guoqiang.sun@downjoy.com"
mailLoginPass_ = "Pa12345678"
mailSubject_ = u"根据2-3月的下载明细数据，统计报表".encode("cp936")
mailTo_ = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
from djutil.MailUtil import MailUtil
def sendMail(mailContents=None):
    try:
        mail = MailUtil(None, mailServer_,mailFromName_, mailFromAddr_,['guoqiang.sun@downjoy.com'],mailLoginUser_,mailLoginPass_,mailSubject_)
        mail.sendMailMessage(mailContents)
    except Exception, e:
        traceback.print_exc()
        print e.message
if __name__ == '__main__':
    try:
        top3Month20Download()
        top2Month20Download()
        top3MonthBTDownload()
        top2MonthBTDownload()
        top3NewGameMonth20Download()
        top2NewGameMonth20Download()
    except Exception, e:
        traceback.print_exc()
        sendMail(e.message)