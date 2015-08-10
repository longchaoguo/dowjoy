#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/01 17:37:45 $"
################################################
#����������ÿ��һ�������ܵع��û��ύ���ͱ���
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
#today=datetime.date(2014,9,14)
yesterday = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m-%d')
todaytime = datetime.datetime.strftime(today, '%Y-%m-%d 00:00:00')
today = datetime.datetime.strftime(today, '%Y-%m-%d')
#print lastWeekFirstDay

#���ݿ�����
dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_10=DBUtil('droid_game_10')


fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "android��Ƕҳ������ͳ���ձ���_%s.xls"%(today)
mailToUsers = ["jacky@downjoy.com","dong.wei@downjoy.com","fan.zhang@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com","dong.wei@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################


def writeFile():
    '''дsheet1������'''
    sheet = workbook.add_sheet(u'android��Ƕҳ������ͳ��', cell_overwrite_ok=True)
    sheet.write(0, 0, 'ͳ������')
    sheet.write(0, 1, yesterday)
    sheet.write(1, 0, '����ID')
    sheet.write(1, 1, '����')
    sheet.write(1, 2, '������')
    sheet.write(1, 5, '���ID')
    sheet.write(1, 6, '����')
    sheet.write(1, 7, '������')
    sheet.write(1, 10, '����ID')
    sheet.write(1, 11, '����')
    sheet.write(1, 12, '������')

    i = 2
    j = 2
    k = 2
    sql="SELECT CHANNEL_FLAG, resource_type, COUNT(*) as cnt FROM `DIGUA_PCWEB_DOWN_LOG` where datediff(%s, created_date)=1 GROUP BY CHANNEL_FLAG, resource_type order by cnt desc"
    rows = dbUtil_168.queryList(sql, (todaytime))
    #print sql
    for row in rows:
        if row[0] == 1: 
            sheet.write(i, 0, row[1])
            sheet.write(i, 1, getGameName(row[1]))
            sheet.write(i, 2, row[2])
            i = i+1
        if row[0] == 2:
            sheet.write(j, 5, row[1])
            sheet.write(j, 6, getGameName(row[1]))
            sheet.write(j, 7, row[2])
            j = j+1
        if row[0] == 5:
            sheet.write(k, 10, row[1])
            sheet.write(k, 11, getNetgameName(row[1]))
            sheet.write(k, 12, row[2])
            k = k+1
    workbook.save(reportFile)

def getCount(id):
    sql="SELECT ifnull(COUNT(ID), 0) FROM `DIGUA_PCWEB_DOWN_LOG` where datediff(%s, created_date)=1"
    if id > 0:
        sql=sql+" and CHANNEL_FLAG=%d"%(id)
    rs = dbUtil_168.queryRow(sql, (todaytime))
    return rs[0]

def getGameName(id):
    sql="select ifnull(name, '') from GAME where ID=%s"
    rs = dbUtil_10.queryRow(sql, (id))
    if rs:
        return rs[0]
    else:
        return ""

def getNetgameName(id):
    sql="select ifnull(name, '') from NETGAME_CHANNEL where ID=%s"
    rs = dbUtil_10.queryRow(sql, (id))
    if rs:
        return rs[0]
    else:
        return ""

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>android��Ƕҳ������ͳ���ձ���������<br>������������⣬�����������ϵ��"
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
    main_msg['Subject'] = "android��Ƕҳ������ͳ���ձ���_%s.xls" % today
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
        #print "????"
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
        if dbUtil_10: dbUtil_10.close()

    print "===over time %s" % datetime.datetime.now()

