#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#功能描述：收费游戏(即有合作游戏)下载量详情报表
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
lastmonth = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m')
#lastmonth= "2013-11"
#print lastWeekFirstDay

#数据库连接
dbUtil_168 = DBUtil('droid_stat_168')


fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "地瓜用户月版本统计_%s.xls"%(lastmonth)
mailToUsers = ["lin.he@downjoy.com", "degang.yang@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################


def writeFile():
    '''写sheet1工作表'''
    sheet = workbook.add_sheet(u'地瓜用户月版本统计', cell_overwrite_ok=True)
    sheet.write(0, 0, '统计月份')
    sheet.write(0, 1, lastmonth)
    sheet.write(1, 0, '版本号')
    sheet.write(1, 1, '月独立用户数')

    i = 2
    sql="SELECT T.version, COUNT(T.imei) AS CNT FROM(SELECT VERSION, imei FROM DIGUA_STAT_USER_LOG WHERE date_format(created_date, '%Y-%m')='"+lastmonth+"' GROUP BY imei) T GROUP BY T.version ORDER BY CNT DESC"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        sheet.write(i, 0, row[0])
        sheet.write(i, 1, row[1])
        i = i+1
    workbook.save(reportFile)



#发送邮件
def sendmail(To):
    body = "您好：<br>地瓜用户月版本统计报表，见附件<br>如有需求和问题，请和蒙启成联系。"

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
    main_msg['Subject'] = "地瓜用户月版本统计_%s.xls" % lastmonth
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

