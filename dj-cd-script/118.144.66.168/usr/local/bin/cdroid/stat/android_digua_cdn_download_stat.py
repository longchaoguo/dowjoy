#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: lin.he $"
__version__ = "$Vision: 1.0 $"
__date__ = "$Date: 2013/5/29 13:00:00 $"

#########################################
#地瓜cdn统计(网宿CDN，通过ftp下载日志)
#########################################
import re
import os
import sys
import datetime
import urllib
import gzip
import StringIO
import traceback
from djutil.RemoveRepeatUtil import RemoveRepeatUtil
from djutil.MailUtil import MailUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.FtpUtil import FtpUtil
#############################################
day=None
pattern=re.compile("^(?P<IP>\S*) \S* \S* \[(?P<TIME>\S*) \S*\] \S* (http:\/\/.*\.com)?\/[^\/]*\/[^\/]*\/game1\/[^\/]*\/(?P<GID>[^\/]*)\/\S* \S* (?P<STATUS>\S*) .* (?P<VERSION>\S*)\"$")

dbUtil=DBUtil('traffic_stats_111')
dbUtil_10=DBUtil('droid_game_10')
dbUtil_168=DBUtil('download_stat_168')
DATA_DICT={}
ID_TYPE_DICT = {}
HISTORY_DICT = {}

cdn_ftp_username = "log"
cdn_ftp_password = "logdown123!"
cdn_ftp_file = "%s-0000-2330_g.androidgame-store.com.cn.log.gz"
localDir = "/opt/logs/addownlog/"

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"安卓地瓜下载量统计错误信息".encode("gbk")
mailTo=['qicheng.meng@downjoy.com']
mailContents=u'Hi: \n'
#############################################
def init():
    global day
    opts=OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'): #raise Exception, 'can not find the datetime params!'
        fileDate=datetime.datetime.strftime(datetime.datetime.today()-datetime.timedelta(days=2), "%Y-%m-%d")
    else:
        fileDate=opts.get('--FILE_DATE')
    print fileDate
    day = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    
#FTP下载日志文件
def getFile(dayStr):
    if not os.path.exists(localDir):
        os.makedirs(localDir)
    rs=1
    attempts=0
    while attempts<20 :
        rs=os.system("wget  'ftp://ftp.wslog.chinanetcenter.com/g.androidgame-store.com/%s' --ftp-user='%s' --ftp-password='%s' -q -t 20 -O %s"%(cdn_ftp_file%dayStr,cdn_ftp_username,cdn_ftp_password,localDir + cdn_ftp_file%dayStr))    
        if rs==0 :
            break;
        attempts =  attempts + 1
        print "attempt times : %s"%attempts    
    if rs != 0:
        raise Exception, "get cdn ftp log fail: %s" % (cdn_ftp_file%dayStr)

def handleFile():
    getFile(day)
    print "file over"
    readFile(day)
    print 'file read over'
    handleStat(day)
    print "handle over"
   
def getRecordTime(recordTimeStr):
    tempTime=datetime.datetime.strptime(recordTimeStr, '%d/%b/%Y:%H:%M:%S')
    return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')

def readFile(dayStr):
    destFile=localDir + cdn_ftp_file%dayStr
    localFile=destFile[:-3]
    if not os.path.exists(localFile) and os.path.exists(destFile):
        os.system('gzip -d -f %s'%destFile)
    f=open(localFile, "rb")
    removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60)
    while True:
        line=f.readline()
        if not line: break
        line=line.strip()
        m=pattern.match(line)
        if not m:
            continue
        status=m.group('STATUS')
        if status not in ['200']: 
            continue
        version=m.group('VERSION')
        version=version.replace('/', '')
        if version.lower().find('digua')==-1:
            version='other'
        recordTime=m.group('TIME')
        ip=m.group('IP')
        gid=int(m.group('GID'))^110111
        recordTime=getRecordTime(recordTime)
        if not removeUtil.isValidByTime( str(gid)+ip, recordTime):continue
        DATA_DICT[str(gid)+'|'+version] = DATA_DICT.get(str(gid)+'|'+version, 0) + 1
    f.close()

def handleStat(dayStr):
    errorNum=0
    sql="insert into DIGUA_DOWNLOAD_CDN_DAILY_STAT(GAME_ID, VERSION, CNT, CREATED_DATE) values(%s, %s, %s, %s)"
    for k, v in DATA_DICT.items():
        arrys = k.split('|')
        gid = int(arrys[0])
        version = arrys[1]
        if version:
            version=version.replace(',', '').replace('"','').replace("'","")
        try:
            dbUtil.insert(sql, (gid, version, v, dayStr))
        except:
            errorNum += 1
            if errorNum > 100:
                raise ex
    sql_log="insert into ANDROID_GAME_DOWNLOAD_LOG (GAME_ID, PKG_ID, CHANNEL_FLAG, RESOURCE_TYPE, CREATED_DATE, IP) values (%s, 0, %s, %s, %s, '')"
    sql_netgame_log="insert into ANDROID_NETGAME_DOWNLOAD_LOG (GAME_ID, PKG_ID, CHANNEL_FLAG, RESOURCE_TYPE, CREATED_DATE, IP) values (%s, 0, %s, %s, %s, '')"
    for k, v in DATA_DICT.items():
        arrys = k.split('|')
        gid = int(arrys[0])
        type = ID_TYPE_DICT.get(gid, 2)
        for i in range(v):
            if type == 5:#网游下载量
                dbUtil_168.insert(sql_netgame_log, (gid, 30, type, dayStr))
            if type != 5:
                dbUtil_168.insert(sql_log, (gid, 30, type, dayStr))
        HISTORY_DICT[type] = HISTORY_DICT.get(type, 0) + v

def getTypeForId():
    sql_type = "select g.ID, gc.RESOURCE_TYPE from GAME g inner join GAME_CATEGORY gc on g.GAME_CATEGORY_ID=gc.ID "
    rows = dbUtil_10.queryList(sql_type, ())
    for row in rows:
        ID_TYPE_DICT[int(row[0])] = int(row[1])

def deleteDBData():
    nextDate=datetime.datetime.strftime(datetime.datetime.strptime(day, '%Y-%m-%d')+datetime.timedelta(days=1), '%Y-%m-%d')
    sql1="delete from ANDROID_GAME_DOWNLOAD_LOG where CHANNEL_FLAG = 30 and CREATED_DATE >= %s and CREATED_DATE < %s"
    dbUtil_168.delete(sql1, (day, nextDate))
    sql2="delete from ANDROID_NETGAME_DOWNLOAD_LOG where CHANNEL_FLAG = 30 and CREATED_DATE >= %s and CREATED_DATE < %s"
    dbUtil_168.delete(sql2, (day, nextDate))

def sendMail():
    global mailContents
    mailContents=(mailContents+u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！'%(datetime.datetime.today(), day, ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
#################################################
if __name__=='__main__':
    print "====go %s=="%datetime.datetime.now()
    try:
        init()
        getTypeForId()
        deleteDBData()
        handleFile()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ex
    finally:
        if dbUtil: dbUtil.close()
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
            sendMail()
    print "===over %s==="%datetime.datetime.now()
