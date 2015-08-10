#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#�����������շ���Ϸ(���к�����Ϸ)���������鱨��
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
#today=datetime.date(2012,11,15)
yesterday = datetime.datetime.strftime(today - datetime.timedelta(days = 2), '%Y-%m-%d')
todaytime = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m-%d 00:00:00')
today = datetime.datetime.strftime(today, '%Y-%m-%d')
#print lastWeekFirstDay

#���ݿ�����
dbUtil_168 = DBUtil('download_stat_168')
dbUtil_10=DBUtil('droid_game_10')


fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "android�շ���Ϸ�����������ձ���_%s.xls"%(today)
mailToUsers = ["eric@downjoy.com", "lu.gan@downjoy.com", "jacky@downjoy.com", "xinjie.wang@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################


def writeFile():
    '''дsheet1������'''
    sheet = workbook.add_sheet(u'android�շ���Ϸ����������', cell_overwrite_ok=True)
    sheet.write(0, 0, 'ͳ������')
    sheet.write(0, 1, yesterday)
    sheet.write(0, 2, '��������')
    sheet.write(1, 0, '����ID')
    sheet.write(1, 1, '����')
    sheet.write(1, 2, '������')
    sheet.write(1, 5, '���ID')
    sheet.write(1, 6, '����')
    sheet.write(1, 7, '������')

    i = 2
    j = 2
    gameIds = getGameIds()
    sql="SELECT RESOURCE_TYPE, GAME_ID, SUM(DOWNS) FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE GAME_ID IN (%s) AND datediff('%s', created_date)=1 GROUP BY GAME_ID, RESOURCE_TYPE ORDER BY SUM(DOWNS) DESC"%(gameIds, todaytime)
    #print sql
    rows = dbUtil_168.queryList(sql, ())
    downs = 0
    for row in rows:
        downs = downs + row[2]
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
    sheet.write(0, 3, downs)
    workbook.save(reportFile)

def getGameIds():
    sql="SELECT ID FROM GAME WHERE DATA_TYPE&4=4 "
    rows = dbUtil_10.queryList(sql, ())
    gameIds=""
    for row in rows:
        if len(gameIds) != 0:
            gameIds = gameIds + ',' + str(row[0])
        else:
            gameIds = str(row[0])
    return gameIds 

def getGameName(id):
    sql="select ifnull(name, '') from GAME where ID=%s"
    rs = dbUtil_10.queryRow(sql, (id))
    if rs:
        return rs[0]
    else:
        return ""

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>androidandroid�շ���Ϸ(����������Ϸ)�����������ձ���������<br>������������⣬���������ϵ��"

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
    main_msg['Subject'] = "android�շ���Ϸ�����������ձ���_%s.xls" % today
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
        if dbUtil_10: dbUtil_10.close()

    print "===over time %s" % datetime.datetime.now()

