#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/01 17:37:45 $"
################################################
#�����������ع����30����ʻ���top200
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
#####################ȫ�ֱ���####################
today = datetime.datetime.today()
today = datetime.datetime.strftime(today, '%Y-%m-%d')
#print lastWeekFirstDay

#���ݿ�����
dbUtil_168 = DBUtil('droid_stat_168')
fileDir = "/usr/local/bin/cdroid/report/data/"
#fileDir="e:/logs/"
reportFile = fileDir + "�ع����30����ʻ���top200_%s.xls"%(today)
#mailToUsers = ["jacky@downjoy.com","dong.wei@downjoy.com","fan.zhang@downjoy.com"]
mailToUsers = ["guoqiang.sun@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################


def writeFile():
    '''дsheet1������'''
    sheet = workbook.add_sheet(u'�ع����30����ʻ���top200ͳ��', cell_overwrite_ok=True)
    sheet.write(0, 0, 'ͳ������')
    sheet.write(0, 1, today)
    sheet.write(1, 0, '���')
    sheet.write(1, 1, '�豸����')
    sheet.write(1, 2, '������')
    i = 2
    sql="SELECT DEVICE,COUNT from DIGUA_STAT_DEVICE_APACHE_TOP_200_TEMP ORDER BY `COUNT` desc"
    rows = dbUtil_168.queryList(sql, ())
    #print sql
    for row in rows:
        sheet.write(i, 0, i-1)
        sheet.write(i, 1, row[0])
        sheet.write(i, 2, row[1])
        i = i+1
    workbook.save(reportFile)

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>�ع����30����ʻ���top200ͳ�Ʊ���������<br>������������⣬������ǿ��ϵ��"
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","bourne@8.3")
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
    main_msg['Subject'] = "�ع����30����ʻ���top200ͳ�Ʊ���_%s.xls" % today
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

