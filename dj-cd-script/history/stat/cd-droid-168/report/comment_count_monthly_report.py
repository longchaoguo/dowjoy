#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2014/05/08 $"

################################################
#����������android��������ͳ�Ʊ���
################################################

import sys
import os
import datetime
import MySQLdb
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import pymongo
import xlwt
import smtplib
from djutil.OptsUtil import OptsUtil

# mongodb��������
mongoCon = pymongo.MongoClient("192.168.0.72", 27017)
mdb = mongoCon.comment

# ��ʶ��ͬ��������
CHANNEL_FLAG_WEB = 1    #WEB����
CHANNEL_FLAG_WAP = 2    #WAP����
CHANNEL_FLAG_DIGUA = 4  #DIGUA����

#��ʼ������
fileDir = "/usr/local/bin/cdroid/report/data/"
reportFile = None
startMonth = None
endMonth = None
mailToUsers = ['christina.gu@downjoy.com','qinmei.li@downjoy.com','guoqiang.sun@downjoy.com','zhou.wu@downjoy.com']
workbook = xlwt.Workbook(encoding='gbk')

#��ʼ��
def init():
    global reportFile, startMonth, endMonth
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m')
    else:
        fileDate = opts.get('--FILE_DATE')
    startMonth = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m'), "%Y-%m")
    endMonth = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m') + datetime.timedelta(days = 31), "%Y-%m")
    reportFile = fileDir + 'android��������ͳ��_%s.xls'%(startMonth)
    print reportFile
    
#����������ȡ��Դ������
def getCommentCntByChannelFlag(channleFlag):
    whereSql = "(this.channelFlag == %s) && (this.pubTime >= '%s') && (this.pubTime < '%s')" % (channleFlag, startMonth, endMonth)
    print whereSql
    count = mdb.resourceComment.find({ "$where" : whereSql}).count()
    return count
    
def writeFile():
    sheet = workbook.add_sheet('android��������ͳ��', cell_overwrite_ok=True)
    
    sheet.write(0, 0, 'ͳ���·�')
    sheet.write(0, 1, startMonth)
    
    sheet.write(1, 0, 'web������')
    sheet.write(1, 1, 'wap������')
    sheet.write(1, 2, 'digua������')
    sheet.write(1, 3, '��������')
    
    webCommentCnt = getCommentCntByChannelFlag(CHANNEL_FLAG_WEB)
    wapCommentCnt = getCommentCntByChannelFlag(CHANNEL_FLAG_WAP)
    diguaCommentCnt = getCommentCntByChannelFlag(CHANNEL_FLAG_DIGUA)
    sheet.write(2, 0, webCommentCnt)
    sheet.write(2, 1, wapCommentCnt)
    sheet.write(2, 2, diguaCommentCnt)
    sheet.write(2, 3, webCommentCnt + wapCommentCnt + diguaCommentCnt)

    workbook.save(reportFile)

#�����ʼ�
def sendmail(To):
    body = '���ã�<br>android��������ͳ�Ʊ���������<br>�������⣬�����ɺ��ϵ��'

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
    main_msg['Subject'] = 'android��������ͳ��_%s.xls' % startMonth
    main_msg['Date'] = email.Utils.formatdate( )
    main_msg["Accept-Language"]="zh-CN"
    main_msg["Accept-Charset"]="ISO-8859-1,utf-8"
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()
        
###############################################################
if __name__ == '__main__':
    try:
        init()
        writeFile()
        sendmail(mailToUsers)
    except Exception, ex:
        print ex
    finally:
        mongoCon.close()


