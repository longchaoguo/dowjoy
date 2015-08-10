#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#功能描述：收费游戏(即合作游戏)下载量详情报表
################################################
import re
import os
import datetime
import urllib
import sys
import xlwt
import xlrd
import StringIO
import traceback
import base64
import smtplib
import email
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"安卓业务报表".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"收费游戏(即合作游戏)统计错误信息".encode("gbk")
mailTo=['zhou.wu@downjoy.com','guoqiang.sun@downjoy.com']
mailContents=u'Hi: \n'
#############################################

#####################全局变量####################

#数据库连接
download_stat_168 = DBUtil('download_stat_168')
droid_game_10=DBUtil('droid_game_10')


fileDir = "/usr/local/bin/cdroid/report/data/"

mailToUsers = ["eric@downjoy.com", "jacky@downjoy.com", "xinjie.wang@downjoy.com","lin.he@downjoy.com"]
#mailToUsers = ["lin.he@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')

GAME_NAME_LIST = {}

#################################################

'''
@param handledate: yyyy-MM-dd形式的日期字符串
'''
def writeFile(handledate):
    '''写sheet1工作表'''
    global reportFile
    reportFile = fileDir + "android收费游戏下载量详情日报表_%s.xls"%(handledate)
    sheet = workbook.add_sheet(u'android收费游戏下载量详情', cell_overwrite_ok=True)
    sheet.write(0, 0, '统计日期')
    sheet.write(0, 1, handledate)
    sheet.write(0, 2, '总下载量')
    sheet.write(1, 0, '单机ID')
    sheet.write(1, 1, '名称')
    sheet.write(1, 2, '下载量')
    sheet.write(1, 5, '软件ID')
    sheet.write(1, 6, '名称')
    sheet.write(1, 7, '下载量')

    i = 2
    j = 2
    downs = 0
    dataList = []
    for gameId in GAME_NAME_LIST.keys():
        try:
            sql = """SELECT RESOURCE_TYPE, GAME_ID, SUM(DOWNS) FROM ANDROID_GAME_DOWNLOAD_DAILY 
                     WHERE created_date = '%s' and GAME_ID = %s"""%(handledate,gameId)
            rows = download_stat_168.queryList(sql)
            if not rows:
                continue
            row = rows[0]
            if not row or not row[0] or not row[1] or not row[2] :
                continue
            downs = downs + row[2]
            gameName=GAME_NAME_LIST[str(row[1])]
            dataList.append((row[0], row[1], row[2]))
        except Exception, ex:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file=fp)
            error = str(fp.getvalue())
            print error
            continue
    
    dataList = sorted(dataList, key = lambda x:x[2], reverse = True)
    
    for item in dataList:
        try:
            resourceType = item[0]
            gameId = item[1]
            sum = item[2]
            gameName=GAME_NAME_LIST[str(gameId)]
            if resourceType == 1: 
                sheet.write(i, 0, gameId)
                sheet.write(i, 1, gameName)
                sheet.write(i, 2, sum)
                i = i+1
            if resourceType == 2:
                sheet.write(j, 5, gameId)
                sheet.write(j, 6, gameName)
                sheet.write(j, 7, sum)
                j = j+1
        except Exception, ex:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file=fp)
            error = str(fp.getvalue())
            print error
            continue
    sheet.write(0, 3, downs)
    workbook.save(reportFile)

def initGameData():
    sql="SELECT ID, ifnull(name, '') FROM GAME WHERE DATA_TYPE&4=4"
    rows = droid_game_10.queryList(sql)
    for row in rows:
        GAME_NAME_LIST[str(row[0])] = row[1]


#发送邮件
def sendmail(To,handledate):
    body = "您好：<br>androidandroid收费游戏(即：合作游戏)下载量详情日报表，见附件<br>如有需求和问题，请和蒙启成联系。"

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

    mailFrom = "\"=?gb2312?B?" + base64.encodestring(mailFromName).replace("\n", "") + "?=\""+" <webmaster@downjoy.com>"
    main_msg['From'] = mailFrom
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = u"android收费游戏下载量详情日报表_%s.xls" % handledate
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()


def sendMail():
    global mailContents
    mailContents=(mailContents+u'下载量统计脚本执行出错，\n错误信息：%s\n谢谢'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
#############################################
if __name__ == '__main__':
    try:
        print "===start time %s" % datetime.datetime.now()
        opts = OptsUtil.getOpts(sys.argv)
        if not opts or not opts.get('--FILE_DATE'):
            fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 2), '%Y-%m-%d')
            print fileDate
        else:
            fileDate = opts.get('--FILE_DATE')
        handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
        initGameData()
        writeFile(handledate)
        sendmail(mailToUsers,handledate)
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: 
            download_stat_168.close()
        if droid_game_10: 
            droid_game_10.close()
        if ERROR_MSG:
            sendMail()
        print "===over time %s" % datetime.datetime.now()

