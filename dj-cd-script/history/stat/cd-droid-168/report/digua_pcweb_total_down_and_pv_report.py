#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/01 17:37:45 $"
################################################
#功能描述：每周一发送上周地瓜用户提交机型报表
################################################
import re
import os
import sys
import datetime
import urllib
import xlwt
import xlrd
import traceback
import smtplib
import email
from xlutils.copy import copy
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
#####################全局变量####################
#print lastWeekFirstDay
style1 = xlwt.XFStyle()
style2 = xlwt.XFStyle()
style3 = xlwt.XFStyle()
pattern1 = xlwt.Pattern()
pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
pattern1.pattern_fore_colour = 50  # 浅绿
style1.pattern = pattern1
pattern3 = xlwt.Pattern()
pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
pattern3.pattern_fore_colour = 34  # yellow
style3.pattern = pattern3
borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
style1.borders = borders
style2.borders = borders
style3.borders = borders
style2.num_format_str = '0'
style3.num_format_str = '0'

#数据库连接
dbUtil_168 = DBUtil('droid_stat_168')

fileDir = "/usr/local/bin/cdroid/report/data/"

mailToUsers = ["jacky@downjoy.com","dong.wei@downjoy.com","fan.zhang@downjoy.com","guoqiang.sun@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
handledate=None
monthStr=None
todaytime=None

#################################################
def init():
    global handledate, monthStr, todaytime, reportFile, rowIndex
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    monthStr = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), '%Y-%m')
    todaytime = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d') + datetime.timedelta(days = 1), '%Y-%m-%d 00:00:00')
    reportFile = fileDir + "android内嵌页数据总量统计报表_%s.xls"%(monthStr)
    rowIndex = int(datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%d"))
    print rowIndex

def createExcel(fileName):
    wb = xlwt.Workbook(encoding = "gbk", style_compression = True)
    sht0 = wb.add_sheet("android内嵌页各数据总量统计", cell_overwrite_ok = True)
    sht0.write(0, 0, '日期', style1)
    sht0.write(0, 1, 'pv总数', style1)
    sht0.write(0, 2, '下载量总数', style1)
    sht0.write(0, 3, '单机下载总数', style1)
    sht0.write(0, 4, '软件下载总数', style1)
    sht0.write(0, 5, '网游下载总数', style1)
    wb.save(fileName)


def writeFile():
    '''写sheet1工作表'''
    if rowIndex == 1:
        createExcel(reportFile)
    rb = xlrd.open_workbook(reportFile, on_demand = True, formatting_info = True)
    wb = copy(rb)
    # 写平台数据报表
    sheet = wb.get_sheet(0)
    sheet.write(rowIndex, 0, handledate, style2)
    sheet.write(rowIndex, 1, getPV(), style2)
    sheet.write(rowIndex, 2, getCount(0), style2)
    sheet.write(rowIndex, 3, getCount(1), style2)
    sheet.write(rowIndex, 4, getCount(2), style2)
    sheet.write(rowIndex, 5, getCount(5), style2)
    wb.save(reportFile)

def getPV():
    sql="select LOCAL_DIR, LOCAL_FILE from FTP_LOG_CONFIG where id in (149,150,151,152,203);"
    pv = 0
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        fileName = row[1]%(handledate)
        if not os.path.exists(row[0]+fileName):
            continue
        cmdstr="cd %s && grep -c @ %s"%(str(row[0]), fileName)
        result = os.popen(cmdstr)
        pv = pv+int(result.read())
    return pv

def getCount(id):
    sql="SELECT ifnull(COUNT(ID), 0) FROM `DIGUA_PCWEB_DOWN_LOG` where datediff(%s, created_date)=1"
    if id > 0:
        sql=sql+" and CHANNEL_FLAG=%d"%(id)
    rs = dbUtil_168.queryRow(sql, (todaytime))
    return rs[0]

#发送邮件
def sendmail(To):
    body = "您好：<br>android内嵌页数据总量统计报表，见附件<br>如有需求和问题，请和蒙启成联系。"

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
    main_msg['Subject'] = "android内嵌页下载总量统计报表_%s.xls" % handledate
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()

def main():
    print "===start time %s" % datetime.datetime.now()
    init()
    writeFile()
    sendmail(mailToUsers)

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtil_168: dbUtil_168.close()

    print "===over time %s" % datetime.datetime.now()

