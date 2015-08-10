#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: qicheng.meng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#功能描述：渠道新增用户和独立用户月报表
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
#数据库连接
dbUtil_168 = DBUtil('droid_stat_168')

def getLastMonth():
    d = datetime.datetime.now()
    
    year = d.year
    month = d.month
     
    if month == 1 :
        month = 12
        year -= 1
    else :
        month -= 1
    return datetime.datetime(year,month,1).strftime('%Y-%m')


last_month = getLastMonth()

fileDir = "./"
reportFile = fileDir + "channel_month_report_%s.xls" % last_month
#mailToUsers = ["zi.li@downjoy.com", "eric@downjoy.com", "lu.gan@downjoy.com", "jacky@downjoy.com", "xinjie.wang@downjoy.com"]
mailToUsers = ["qicheng.meng@downjoy.com","dong.wei@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
pattern = xlwt.Pattern() # Create the Pattern
pattern.pattern = xlwt.Pattern.NO_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
pattern.pattern_fore_colour = 1 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
style = xlwt.XFStyle() # Create the Pattern
style.pattern = pattern # Add Pattern to Style

#################################################


def writeFile():
    sheet1 = workbook.add_sheet(u'新增用户', cell_overwrite_ok=True)
    sheet2 = workbook.add_sheet(u'独立用户', cell_overwrite_ok=True)
    i=0
    statDate="2014-12"
    rows = getAddedUserCnt(0,statDate)
    for row in rows:
        if not row:
            continue
        #try:
        print row
        sheet1.write(i, 0, row[0].decode('utf-8').encode('gbk'), style)
        sheet1.write(i, 1, row[1], style)
        sheet1.write(i, 2, row[2], style)
        i=i+1
        
    i=0
    rows = getLoginUserCnt(0,statDate)
    for row in rows:
        if not row:
            continue
        #try:
        sheet2.write(i, 0, row[0].decode('utf-8').encode('gbk'), style)
        sheet2.write(i, 1, row[1], style)
        sheet2.write(i, 2, row[2], style)
        i=i+1
        
    workbook.save(reportFile)

def getAddedUserCnt(clientChannelId, statDate):
    sql='select CLIENT_CHANNEL_ID,CLIENT_CHANNEL_NAME,count(IMEI) from DIGUA_USER_APACHE where date_format(created_date, "%Y-%m")="'+statDate+'" GROUP BY CLIENT_CHANNEL_ID'
    return dbUtil_168.queryList(sql, ())

def getLoginUserCnt(clientChannelId, statDate):
    clearsql='TRUNCATE TABLE DIGUA_STAT_USER_LOG_APACHE_mqc'
    dbUtil_168.truncate(clearsql, ())
    sql='insert into DIGUA_STAT_USER_LOG_APACHE_mqc (select * from DIGUA_STAT_USER_LOG_APACHE where date_format(created_date, "%Y-%m")="'+statDate+'"  group by imei)'
    dbUtil_168.insert(sql,())
    querysql='select CLIENT_CHANNEL_ID,CLIENT_CHANNEL_NAME,count(id) from DIGUA_STAT_USER_LOG_APACHE_mqc GROUP BY CLIENT_CHANNEL_ID'
    return dbUtil_168.queryList(querysql, ())

#发送邮件
def sendmail(To):
    body = "您好：<br>渠道用户月报表，见附件<br>如有需求和问题，请和启成联系。"

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
    main_msg['Subject'] = "渠道用户月报表_%s.xls" % last_month
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()

def main():
    print "===start time %s" % datetime.datetime.now()
    writeFile()
    sendmail(mailToUsers)

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtil_168: dbUtil_168.close()

    print "===over time %s" % datetime.datetime.now()

