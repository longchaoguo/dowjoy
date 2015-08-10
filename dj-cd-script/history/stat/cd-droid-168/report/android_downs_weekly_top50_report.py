#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#功能描述：android周下载量top50报表
################################################
import re
import os
import datetime
import urllib
import xlwt
import xlrd
import traceback
import smtplib
import email
from djutil.DBUtil import DBUtil
#####################全局变量####################
today = datetime.datetime.today()
#today=datetime.date(2012,11,15)
handledate = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m-%d')
todaydate = datetime.datetime.strftime(today, '%Y-%m-%d')
#print lastWeekFirstDay

#数据库连接
dbUtil_168 = DBUtil('download_stat_168')
dbUtil_10=DBUtil('droid_game_10')
gamelist = {}
softlist = {}
netgamelist = {}
gameDownslist = {}
softDownslist = {}
netgameDownslist = {}


fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "android周下载量top50报表_%s.xls"%(todaydate)
mailToUsers = ["chao.nie@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################


def writeFile():
    '''写sheet1工作表'''
    sheet = workbook.add_sheet(u'android周下载量top50报表', cell_overwrite_ok=True)
    sheet.write(0, 0, '统计日期')
    sheet.write(0, 1, todaydate)
    sheet.write(1, 0, '单机名称')
    sheet.write(1, 1, '下载量')
    sheet.write(1, 2, '软件名称')
    sheet.write(1, 3, '下载量')
    sheet.write(1, 4, '网游名称')
    sheet.write(1, 5, '下载量')

    i = 2
    sql = "select GAME_ID, SUM(DOWNS) as downsSum FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE datediff(%s, created_date)<7 and resource_type=1 group by GAME_ID order by downsSum desc limit 50"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:

        sheet.write(i, 0, gamelist[row[0]])
        sheet.write(i, 1, row[1])
        i = i+1

    i = 2
    sql = "select GAME_ID, SUM(DOWNS) as downsSum FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE datediff(%s, created_date)<7 and resource_type=2 group by GAME_ID order by downsSum desc limit 50"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:
        sheet.write(i, 2, softlist[row[0]])
        sheet.write(i, 3, row[1])
        i = i+1

    i = 2
    sql = "select CHANNEL_ID, SUM(DOWNS) as downsSum FROM ANDROID_NETGAME_DOWNLOAD_DAILY WHERE datediff(%s, created_date)<7 group by CHANNEL_ID order by downsSum desc limit 50"
    rows = dbUtil_168.queryList(sql, (handledate))
    for row in rows:
        sheet.write(i, 4, netgamelist[row[0]])
        sheet.write(i, 5, row[1])
        i = i+1

    workbook.save(reportFile)

def initGames():
    sql="SELECT ID, NAME FROM GAME where resource_type=1"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        gamelist[row[0]] = row[1]

def initSofts():
    sql="SELECT ID, NAME FROM GAME where resource_type=2"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        softlist[row[0]] = row[1]

def initNetgames():
    sql="SELECT ID, NAME FROM NETGAME_CHANNEL"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        netgamelist[row[0]] = row[1]

#发送邮件
def sendmail(To):
    body = "您好：<br>android周下载量top50报表，见附件<br>如有需求和问题，请和蒙启成联系。"

    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(body, 'html', 'gbk')
    main_msg.attach(text_msg)

    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)
    data = open(reportFile, 'rb')
    file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
    file_msg.set_payload(data.read( ))
    data.close( )
    email.Encoders.encode_base64(file_msg)

    basename = os.path.basename(reportFile)
    file_msg.add_header('Content-Disposition','attachment', filename = basename)
    main_msg.attach(file_msg)

    main_msg['From'] = "webmaster@downjoy.com"
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = "android周下载量top50报表_%s.xls" % todaydate
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()

def main():
    print "===start time %s" % datetime.datetime.now()
    initGames()
    initSofts()
    initNetgames()
    writeFile()
    sendmail(mailToUsers)

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()

    print "===over time %s" % datetime.datetime.now()

