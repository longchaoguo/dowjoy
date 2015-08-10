#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#每日存档下载量前100统计日报表
###########################################
import re
import os
import sys
import time
import datetime
import StringIO
import traceback
import xlwt
import xlrd
import smtplib
import email
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
###########################################
dbUtil_168 = DBUtil('droid_stat_168')
dbUtil_10 = DBUtil('droid_game_10')
#获取日志产生时间
handledate = None#str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), "%Y-%m-%d"))
mailToUsers = ["chao.nie@downjoy.com","guoqiang.sun@downjoy.com"]
#mailToUsers = ["qicheng.meng@downjoy.com"]
workbook = xlwt.Workbook(encoding='gbk')
pattern = re.compile("(?P<TIME>\S+ \S+) \S+ \/android\/new\/gamesave\/(?P<ID>\d+)\/(?P<PACKAGE>\d+_\d+)\.(?P<SUFFIX>\S+) - (?P<IP>\S+) \S* \S* (?P<STATUS>\d+)")
GAME_SAVE_DOWNS = {}
GAME_SAVE_NAME = {}
GAME_SAVE_DOWN_DATE = {}

#日志存放目录
localDir="/usr/local/bin/cdroid/report/data/"

style1 = xlwt.XFStyle()
style2 = xlwt.XFStyle()
pattern1 = xlwt.Pattern()
pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
pattern1.pattern_fore_colour = 50  # 浅绿
style1.pattern = pattern1
borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
style1.borders = borders
style2.borders = borders
style2.num_format_str = '0'

########################################################
def init():
    global handledate, fileName, localdate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    localdate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%y%m%d")
    fileName = "存档下载量前100统计日报表_%s.xls" % handledate

def initGameSaveName():
    sql = "select ID, NAME from GAME_SAVE"
    rows = dbUtil_10.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        GAME_SAVE_NAME[str(row[0])] = row[1]

#解析日志
def statFile(logName):
    # 如果该文件不存在，抛出异常
    if not os.path.exists(logName):
        raise Exception, 'can not find file: %s' % logName
    f = open(logName, 'rb')
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        m = pattern.match(line)
        if not m:
            continue
        if not m.group('STATUS') in ['200', '206']:
            continue
        if m.group('SUFFIX') != 'dar':
            continue
        gameSaveId = m.group('ID')
        if isRepeatingData(m.group('IP'), gameSaveId, m.group('TIME')):
            continue
        if not GAME_SAVE_DOWNS.has_key(gameSaveId):
            GAME_SAVE_DOWNS[gameSaveId] = 1
        else:
            GAME_SAVE_DOWNS[gameSaveId] = int(GAME_SAVE_DOWNS[gameSaveId])+1
    f.close()


def isRepeatingData(ip, packageId, createdDate):
    key = str(ip)+"|"+str(packageId)
    if not GAME_SAVE_DOWN_DATE.has_key(key):
        GAME_SAVE_DOWN_DATE[key] = createdDate
        return False
    if repeatingDataOutTime(key, createdDate):
        GAME_SAVE_DOWN_DATE[key] = createdDate
        return False
    return True
def repeatingDataOutTime(key, createdDate):
    diffTime = (datetime.datetime.strptime(createdDate, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(GAME_SAVE_DOWN_DATE[key], '%Y-%m-%d %H:%M:%S')).seconds
    if diffTime > 600 :
        return True
    else :
        return False

def writeExcel():
    wb = xlwt.Workbook(encoding = "gbk", style_compression = True)
    sht0 = wb.add_sheet("存档下载量前100统计日报表", cell_overwrite_ok = True)
    sht0.write(0, 0, '统计日期', style1)
    sht0.write(0, 1, handledate)
    sht0.write(1, 0, 'ID', style1)
    sht0.write(1, 1, '名称', style1)
    sht0.write(1, 2, '下载量', style1)
    rowIndex = 2
    for k, v in sorted(GAME_SAVE_DOWNS.iteritems(), key=lambda d:d[1], reverse=True):
        gameSaveName = ''
        if rowIndex == 102:
            break
        if GAME_SAVE_NAME.has_key(k):
            gameSaveName = GAME_SAVE_NAME[k]
        sht0.write(rowIndex, 0, k, style2)
        sht0.write(rowIndex, 1, gameSaveName, style2)
        sht0.write(rowIndex, 2, GAME_SAVE_DOWNS[k], style2)
        rowIndex = rowIndex+1
    wb.save(localDir+fileName)

def handleFtpFile():
    sql="select LOCAL_DIR, LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in ( 144);"
    rows = dbUtil_168.queryList(sql, ())
    for row in rows:
        localFile=row[1]%(localdate)
        time.sleep(1)
        print "%s%s"%(row[0], localFile)
        statFile(row[0] + localFile)
        print localFile, 'over'

def sendMail(To):
    body = "您好：<br>存档下载量前100统计日报表，见附件<br>如有需求和问题，请和蒙启成联系。"

    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(body, 'html', 'gbk')
    main_msg.attach(text_msg)

    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)
    data = open(localDir+fileName, 'rb')
    file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
    file_msg.set_payload(data.read( ))
    data.close( )
    email.Encoders.encode_base64(file_msg)

    basename = os.path.basename(localDir+fileName)
    file_msg.add_header('Content-Disposition','attachment', filename = basename)
    main_msg.attach(file_msg)

    main_msg['From'] = "webmaster@downjoy.com"
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = fileName
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail("webmaster@downjoy.com", To, fullText)
    finally:
        server.quit()

###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        init()
        initGameSaveName()
        handleFtpFile()
        writeExcel()
        sendMail(mailToUsers)

    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_10: dbUtil_10.close()
        if dbUtil_168: dbUtil_168.close()

    print "=================end   %s======" % datetime.datetime.now()


