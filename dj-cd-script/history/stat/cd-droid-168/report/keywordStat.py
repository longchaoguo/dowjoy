#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#
###########################################
import os
import sys
import time
import datetime
import StringIO
import traceback
import xlwt
import xlrd
import email
import smtplib
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
handledate = None
mailToUsers = ["christina.gu@downjoy.com", "jacky@downjoy.com", "chengbao.yang@downjoy.com", "leepong@downjoy.com","guoqiang.sun@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
fileDir = "/usr/local/bin/cdroid/report/data/"

def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    date=time.strptime(fileDate, "%Y-%m-%d")
    reportFile = fileDir + "关键字TOP100_%s.xls"%(handledate)

def clearData():
    sql="truncate CACHE_KEYS_DIGUA"
    dbUtil_168.delete(sql,())
    sql="truncate CACHE_KEYS_WEB"
    dbUtil_168.delete(sql,())

def handleWeb():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in(157,158) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        if not os.path.exists(row[2]+localFile):
            continue
        print "%s%s"%(row[2], localFile)
        statWebKeyword(row[2] + localFile)
        print localFile, 'over'

def handleDigua():
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in(161,162,163,164,205) order by ID;"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%(handledate)
        localFile=row[3]%(handledate)
        time.sleep(1)
        if not os.path.exists(row[2]+localFile):
            continue
        print "%s%s"%(row[2],localFile)
        statDigauKeyword(row[2]+localFile)
        print localFile, 'over'

########################################################
def insertData(dbUtil, sql, dataList):
    #print "insertData start....."
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

#将日志入库
def statDigauKeyword(fileName):
    # 如果该文件不存在，抛出异常
    f = open(fileName, 'rb')
    sql = "insert into CACHE_KEYS_DIGUA(CACHE_KEY) values (%s)"
    dataList = []
    i=0
    while True:
        line = f.readline()
        if not line:
            break
        i=i+1
        #if i<=2305000:
        #    continue
        array = line.split('|')
        if len(array)<2:
            continue
        dataList.append((array[1]))

        if len(dataList) >= 1000 :
            #print i
            insertData(dbUtil_168, sql, dataList)
            dataList = []
    if len(dataList)>0:
        insertData(dbUtil_168, sql, dataList)
        dataList = []
    f.close()

def statWebKeyword(fileName):
    # 如果该文件不存在，抛出异常
    f = open(fileName, 'rb')
    sql = "insert into CACHE_KEYS_WEB(CACHE_KEY) values (%s)"
    dataList = []
    i=0
    while True:
        line = f.readline()
        if not line:
            break
        i=i+1
        #if i<=2305000:
        #    continue
        array = line.split('|')
        if len(array)<2:
            continue
        dataList.append((array[1]))

        if len(dataList) >= 1000 :
            #print i
            insertData(dbUtil_168, sql, dataList)
            dataList = []
    if len(dataList)>0:
        insertData(dbUtil_168, sql, dataList)
        dataList = []
    f.close()

def writeFile(reportFile):
    sheet1 = workbook.add_sheet(u'web关键字Top100', cell_overwrite_ok=True)
    sheet1.write(0,0, u'关键字')
    sheet1.write(0,1, u'数量')
    sheet2 = workbook.add_sheet(u'digua关键字Top100', cell_overwrite_ok=True)
    sheet2.write(0,0, u'关键字')
    sheet2.write(0,1, u'数量')
    i=1
    #print CLIENT_CHANNEL_IDS
    for web in getWebTop100():
        sheet1.write(i, 0, web[0])
        sheet1.write(i, 1, web[1])
        i = i+1
    i=1
    for digua in getDiguaTop100():
        sheet2.write(i, 0, digua[0])
        sheet2.write(i, 1, digua[1])
        i = i+1

    workbook.save(reportFile)

def getWebTop100():
    sql="select CACHE_KEY, COUNT(ID) AS CNT FROM CACHE_KEYS_WEB group BY CACHE_KEY ORDER BY CNT DESC LIMIT 100"
    return dbUtil_168.queryList(sql,())

def getDiguaTop100():
    sql="select CACHE_KEY, COUNT(ID) AS CNT FROM CACHE_KEYS_DIGUA group BY CACHE_KEY ORDER BY CNT DESC LIMIT 100"
    return dbUtil_168.queryList(sql,())


#发送邮件
def sendmail(reportFile):
    body = "您好：<br>搜索关键字top100统计报表，见附件<br>如有需求和问题，请和蒙启成联系。"

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
    main_msg['To'] = ', '.join(mailToUsers)
    main_msg['Subject'] = u"搜索关键字TOP100_%s.xls"%(handledate)
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", mailToUsers, fullText)
    finally:
        server.quit()

###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    init()
    #clearData()
    #handleWeb()
    #handleDigua()
    reportFile = fileDir + "关键字TOP100_%s.xls"%(handledate)
    writeFile(reportFile)
    sendmail(reportFile)
    if dbUtil_168: dbUtil_168.close()
    #if dbUtil_111: dbUtil_111.close()
    print "=================end   %s======" % datetime.datetime.now()


