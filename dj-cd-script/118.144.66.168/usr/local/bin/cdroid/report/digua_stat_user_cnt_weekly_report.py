#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#�����������������������û��Ͷ����û����ܱ���
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
today = datetime.datetime.today()-datetime.timedelta(days = 1)
#today = datetime.date(2014,8,25)
startTime = today - datetime.timedelta(days = 8)
today = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m-%d')
#print 

#���ݿ�����
dbUtil_168 = DBUtil('droid_stat_168')
CLIENT_CHANNEL_DICT={100451:'wapһ������',100463:'webһ������',100496:'web��ҳһ������',100001:'�عϹ���',100002:'Android�Ż�',100003:'�ٷ��г�',100400:'������Ϸ���Ĺ���',100482:'wap����ҳ',100483:'�㶹������ҳ',100484:'��Ѷ����ҳ',100485:'360����ҳ',100498:'����PC��'}
CLIENT_CHANNEL_IDS=[100451,100463,100496,100001,100002,100003,100400,100482,100483,100484,100485,100498]

fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = fileDir + "�ع����������û������ܱ���_%s.xls"%(today)
#mailToUsers = ["zi.li@downjoy.com", "eric@downjoy.com", "lu.gan@downjoy.com", "jacky@downjoy.com", "xinjie.wang@downjoy.com"]
mailToUsers = ["dong.wei@downjoy.com", "jacky@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
pattern = xlwt.Pattern() # Create the Pattern
pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
pattern.pattern_fore_colour = 17 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
style = xlwt.XFStyle() # Create the Pattern
style.pattern = pattern # Add Pattern to Style

#################################################


def writeFile():
    sheet1 = workbook.add_sheet(u'�����û�', cell_overwrite_ok=True)
    sheet1.write_merge(0,1,0,0, u'ͳ������')
    sheet2 = workbook.add_sheet(u'�����û�', cell_overwrite_ok=True)
    sheet2.write_merge(0,1,0,0, u'ͳ������')
    for i in range(0, 7):
        sheet1.write(i+2, 0, datetime.datetime.strftime(startTime + datetime.timedelta(days = i), '%Y-%m-%d'))
        sheet2.write(i+2, 0, datetime.datetime.strftime(startTime + datetime.timedelta(days = i), '%Y-%m-%d'))
    i=1
    #print CLIENT_CHANNEL_IDS
    for clientChannelId in CLIENT_CHANNEL_IDS:
        sheet1.write(0, i, CLIENT_CHANNEL_DICT[clientChannelId], style)
        sheet1.write(1, i, clientChannelId, style)

        sheet2.write(0, i, CLIENT_CHANNEL_DICT[clientChannelId], style)
        sheet2.write(1, i, clientChannelId, style)

        for j in range(0, 7):
            statDate=datetime.datetime.strftime(startTime + datetime.timedelta(days = j), '%Y-%m-%d')
            sheet1.write(j+2, i, getAddedUserCnt(clientChannelId, statDate))
            sheet2.write(j+2, i, getLoginUserCnt(clientChannelId, statDate))


        i = i+1
    
    for i in range(0, 7):
        datetime.datetime.strftime(startTime + datetime.timedelta(days = i), '%Y-%m-%d')
        #print i

    workbook.save(reportFile)

def getAddedUserCnt(clientChannelId, statDate):
    sql='SELECT SUM(cnt) FROM DIGUA_STAT_UNIQUE_ADDED_USER_FOR_CLIENT_CHANNEL WHERE client_channel_id ='+str(clientChannelId)+' and DATE_FORMAT(stat_date, "%Y-%m-%d")="'+statDate+'"'
    return dbUtil_168.queryCount(sql, ())

def getLoginUserCnt(clientChannelId, statDate):
    sql='SELECT SUM(cnt) FROM DIGUA_STAT_DAILY_CLIENT_CHANNEL_CNT WHERE client_channel_id ='+str(clientChannelId)+' and DATE_FORMAT(stat_date, "%Y-%m-%d")="'+statDate+'"'
    return dbUtil_168.queryCount(sql, ())

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>�ع����������û������ܱ���������<br>������������⣬�����������ϵ��"

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
    main_msg['Subject'] = "�ع����������û������ܱ���_%s.xls" % today
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

