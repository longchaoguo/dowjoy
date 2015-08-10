#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#����������WEbÿ��������top100
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
yesterday=datetime.datetime.strftime(datetime.datetime.today()-datetime.timedelta(days=2),'%Y-%m-%d')
#print 

#���ݿ�����
dbUtil_168 = DBUtil('download_stat_168')
dbUtil_10=DBUtil('droid_game_10')

fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "Webÿ��������TOP50_%s.xls"%(yesterday)
mailToUsers = ["christina.gu@downjoy.com","chengbao.yang@downjoy.com","dong.wei@downjoy.com","siming.yang@downjoy.com","leepong@downjoy.com","kehong.li@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
GAME_DICT={}

#################################################


def writeFile():
    sql = "select id, name from GAME"
    games=dbUtil_10.queryList(sql, ())
    for game in games:
        GAME_DICT[game[0]]=game[1]
    sheet1 = workbook.add_sheet(u'����TOP50', cell_overwrite_ok=True)
    sheet1.write(0,0, u'��ϷID')
    sheet1.write(0,1, u'��Ϸ��')
    sheet1.write(0,2, u'������')
    sheet2 = workbook.add_sheet(u'���TOP50', cell_overwrite_ok=True)
    sheet2.write(0,0, u'���ID')
    sheet2.write(0,1, u'�����')
    sheet2.write(0,2, u'������')
    i=1
    #print CLIENT_CHANNEL_IDS
    for game in getGameTop50():
        sheet1.write(i, 0, game[0])
        sheet1.write(i, 1, GAME_DICT[game[0]])
        sheet1.write(i, 2, game[1])
        i = i+1
    i=1
    for soft in getSoftwareTop50():
        sheet2.write(i, 0, soft[0])
        sheet2.write(i, 1, GAME_DICT[soft[0]])
        sheet2.write(i, 2, soft[1])
        i = i+1

    workbook.save(reportFile)

def getGameTop50():
    sql="SELECT game_id, downs FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE resource_type=1 AND channel_flag=10 AND DATE_FORMAT(created_date, '%Y-%m-%d')='"+yesterday+"' ORDER BY downs DESC LIMIT 50"
    return dbUtil_168.queryList(sql, ())

def getSoftwareTop50():
    sql="SELECT game_id, downs FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE resource_type=2 AND channel_flag=10 AND DATE_FORMAT(created_date, '%Y-%m-%d')='"+yesterday+"' ORDER BY downs DESC LIMIT 50"
    print sql
    return dbUtil_168.queryList(sql, ())

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>web��������top50��������<br>������������⣬�����������ϵ��"

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
    main_msg['Subject'] = "Webÿ��������TOP50_%s.xls" % yesterday
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

