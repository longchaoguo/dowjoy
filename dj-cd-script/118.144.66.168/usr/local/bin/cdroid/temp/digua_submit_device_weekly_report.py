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
import re
from djutil.DBUtil import DBUtil
#####################ȫ�ֱ���####################
#today = datetime.datetime.today()
today=datetime.date(2014,01,06)
#lastWeekFirstDay = datetime.datetime.strftime(today - datetime.timedelta(days = 1), '%Y-%m-%d 00:00:00')
todaytime = datetime.datetime.strftime(today, '%Y-%m-%d 00:00:00')
today = datetime.datetime.strftime(today, '%Y-%m-%d')
#print lastWeekFirstDay

#���ݿ�����
dbUtil_droid = DBUtil('droid_game_10')
GPU_LIST = {}
fileDir = "/usr/local/bin/dj_script/report/data/"
reportFile = fileDir + "�ع��û��ύ���ͣ���ӦUA������ͳ��%s.xls"%(today)
numPattern = re.compile(".+num\":\"(?P<NUM>15555215554)\"")
#mailToUsers = ["chengbao.yang@downjoy.com", "jin.hu@downjoy.com", "jacky@downjoy.com", "yiqiang.duan@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

#################################################

def getGpuList():
    f = open("/opt/logs/gpu1230-1.5.txt", 'rb')
    #fw = open("/opt/logs/imei_gpu.txt", 'wb')
    while True:
        line = f.readline()
        if not line:
            break
        array = line.split('@!@')
        if len(array) != 4:
            continue
        headStr = array[3].strip()
        if headStr == 'null':
            continue
        createdDate = array[0]
        numMatch = numPattern.match(headStr)
        if numMatch:
            continue
        clientChannelId = ''
        imei = ''
        versionStr = ''
        num = ''
        try:
            headDict = eval(headStr)
            imei = headDict['imei']
            gpu = headDict['gpu']
            if GPU_LIST.has_key(str(imei)):
                continue
            #print gpu
            GPU_LIST[str(imei)] = gpu
            #fw.write(str(imei)+"="+str(gpu)+"\n")
            headDict.clear()
        except:
            continue
    #fw.close()
    f.close()

def writeFile():
    '''дsheet1������'''
    sheet = workbook.add_sheet('data_stat', cell_overwrite_ok=True)
    sheet.write(0, 0, 'ID')
    sheet.write(0, 1, 'androidϵͳ�汾')
    sheet.write(0, 2, '�عϰ汾')
    sheet.write(0, 3, '�Զ�ʶ�����')
    sheet.write(0, 4, '�û��ύ����')
    sheet.write(0, 5, 'imei')
    sheet.write(0, 6, 'gpu')
    sheet.write(0, 7, 'ʱ��')
    i = 1
    getGpuList()
    sql="SELECT id,osName,digua_version,device_auto_gain,device_by_custom,imei,create_time FROM DIGUA_CUSTOM_SUBMIT_DEVICE WHERE DATE_SUB(%s, INTERVAL 7 DAY ) <create_time AND create_time<%s"
    rows = dbUtil_droid.queryList(sql, (todaytime, todaytime))
    print sql
    for row in rows:
        sheet.write(i, 0, str(row[0]))
        sheet.write(i, 1, str(row[1]))
        sheet.write(i, 2, str(row[2]))
        sheet.write(i, 3, str(row[3]))
        sheet.write(i, 4, str(row[4]))
        sheet.write(i, 5, str(row[5]))
        sheet.write(i, 6, GPU_LIST.get(str(row[5]),""))
        sheet.write(i, 7, str(row[6]))
        i = i+1
    workbook.save(reportFile)

#�����ʼ�
def sendmail(To):
    body = "���ã�<br>���ܵع��û��ύ���ͣ���ӦUA������ͳ�ƣ�������"

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
    main_msg['Subject'] = "�ع��û��ύ���ͣ���ӦUA������ͳ��%s.xls" % today
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()

def main():
    print "===start time %s" % datetime.datetime.now()
    writeFile()
    #sendmail(mailToUsers)

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtil_droid: dbUtil_droid.close()

    print "===over time %s" % datetime.datetime.now()

