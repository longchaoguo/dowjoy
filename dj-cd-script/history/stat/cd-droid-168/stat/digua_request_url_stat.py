#!/usr/bin/python
# -*- coding: cp936 -*-

__author__ = "$Author: guoqiang.sun$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015年4月3日10:56:14 $"
###########################################
#地瓜访问url统计
###########################################
import os
import sys
import time
import datetime
import ftplib
import StringIO
import traceback
import re
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
import csv
import codecs
###########################################
dataBase_droid_stat_id = 'droid_stat_168'
dbUtil_168 = DBUtil(dataBase_droid_stat_id)
TABLE_NAME='DIGUA_REQUEST_URL_PV_STAT'
URL_STAT_PV={}
URL_STAT_UV={}
#获取日志产生时间
HANDLE_DATE = None
CREATE_DATE=None
fileDir = "/usr/local/bin/cdroid/report/data/"
#fileDir = "e:/logs/"
reportFile = None
REQUEST_URL_MAP={'/newdiguaserver/game/index720':u'新地瓜游戏精选',
                 '/newdiguaserver/game/newest':u'新地瓜游戏最新',
                 '/newdiguaserver/game/star':u'新地瓜游戏五星',
                 '/newdiguaserver/game/rank':u'新地瓜游戏排行',
                 '/newdiguaserver/activity/list':u'新地瓜游戏专题',
                 '/newdiguaserver/game/category':u'新地瓜游戏分类',
                 '/newdiguaserver/netgame/recommend':u'新地瓜网游精选',
                 '/newdiguaserver/netgame/rank':u'新地瓜网游排行',
                 '/newdiguaserver/netgame/new/list':u'新地瓜网游最新',
                 '/newdiguaserver/netgame/category/list':u'新地瓜网游分类',
                 '/newdiguaserver/software/essential':u'新地瓜软件必备',
                 '/newdiguaserver/software/newest':u'新地瓜软件排行',
                 '/newdiguaserver/software/rank':u'新地瓜软件最新',
                 '/newdiguaserver/software/category':u'新地瓜软件分类',
                 '/newdiguaserver/emulator/list':u'新地瓜模拟器',
                 '/newdiguaserver/game/essential':u'新地瓜必备游戏',
                 '/newdiguaserver/game/large':u'新地瓜大型游戏',
                 '/newdiguaserver/game/bt':u'新地瓜修改破解',
                 '/newdiguaserver/res/detail':u'新地瓜游戏详情接口',
                 '/newdiguaserver/comment/':u'新地瓜评论接口',
                 '/v64x/dir/recomment?pn=1&ps=30&editorId=1':u'老地瓜游戏精选',
                 '/dir/latest?pn=1&ps=10&rt=1':u'老地瓜游戏最新',
                 '/dir/5star?pn=1&ps=10&rt=1':u'老地瓜游戏五星',
                 '/dir/ranking/hot-game?pn=1&ps=10':u'老地瓜游戏排行',
                 '/dir/new_activity_latest?pn=1&ps=10':u'老地瓜游戏专题',
                 '/dir/category?rt=1':u'老地瓜游戏分类',
                 '/dir/ngchannel/recommand':u'老地瓜网游精选',
                 '/dir/ngchannel/hotest?pn=1&ps=10':u'老地瓜网游排行',
                 '/dir/ngchannel/ngmemorabilia':u'老地瓜网游最新',
                 '/newdiguaserver/netgame/category/list':u'老地瓜网游分类',
                 '/v64x/dir/essentialsoftwares':u'老地瓜软件必备',
                 '/dir/ranking/hot-software?pn=1&ps=10':u'老地瓜软件排行',
                 '/dir/latest?pn=1&ps=10&rt=2':u'老地瓜软件最新',
                 '/dir/category?rt=2':u'老地瓜软件分类',
                 '/dir/emulator/arcade':u'老地瓜模拟器',
                 '/v64x/dir/essentialgames':u'老地瓜必备游戏',
                 '/v64x/dir/largegames?rtype=1&pn=1&ps=10':u'老地瓜大型游戏',
                 '/v64x/dir/btgames?pn=1&ps=10&rtype=GAME':u'老地瓜修改破解',
                 '/item//':u'老地瓜游戏详情接口',
                 '/v64x/comment/list':u'老地瓜评论接口'}
pattern = re.compile(r"""\[(?P<TIME>\S*) \S*\] \S* (?P<URL>(\S*( \?\S*)?))\s*(?P<IP>([\d\.]*(\,\s+[\d\.]*)?))\s*(?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {.*\\"imei\\":\\"(?P<IMEI>\w+)\\".*}""")
#####邮件报错提醒
ERROR_MSG = None
MAIL_SERVER = "mail.downjoy.com"
MAIL_FROM_NAME = u"当乐数据中心".encode("gbk")
MAIL_FROM_ADDRESS = "webmaster@downjoy.com"
MAIL_LOGIN_USER = "webmaster@downjoy.com"
MAIL_LOGIN_PASS = "htbp3dQ1sGcco!q"
MAIL_SUBJECT = "游戏中心游戏详情页和评论页访问量统计错误信息"
MAIL_TO = ['guoqiang.sun@downjoy.com']
MAIL_CONTENS = u'Hi: \n'
reportName = None
csvfile = None
########################################################
def  init(fileDate=None):
    global HANDLE_DATE,CREATE_DATE
    HANDLE_DATE = datetime.datetime.strftime(fileDate, "%y%m%d")
    CREATE_DATE = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
def  insertData(dbUtil, sql, dataList):
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
def statFile(dir,fileName,flag = 'False'):
    # 如果该文件不存在，抛出异常
    if os.path.exists(dir+fileName):
        f = open(dir+fileName, 'rb')
        print 'process file %s' %(fileName,)
        i = 0
        while 1:
            lines = f.readlines(512*1024*1024)
            i = i+1
            print i
            if not lines:
                break
            line_count = len(lines)
            URL = None
            for a in xrange(line_count):
                match = pattern.match(lines[a])
                if not match:
                    #print line
                    continue
                dicts = match.groupdict()
                status = dicts['STATUS']
                if not status in ['200']:
                    continue
                try:
                     URL = dicts["URL"]
                     URL = getRealUrl(URL)
                     if URL:
                        if(URL_STAT_PV.has_key(URL)):
                             URL_STAT_PV[URL]= URL_STAT_PV[URL]+1
                        else:
                             URL_STAT_PV[URL]=1
                        ip = dicts["IP"]
                        if(URL_STAT_UV.has_key(URL)):
                            URL_STAT_UV[URL].add(ip)
                        else:
                             URL_STAT_UV[URL]=set(ip)
                except:
                    pass
            lines = []
        f.close()
        if(str(flag) == 'True'):
            os.remove(dir+fileName)
    else:
        if(str(flag) == 'True'):
            ERROR_MSG = u'解压文件%sbak/%s.tar.gz失败' %(dir,fileName)
            sendMail()
            return
        #os.system("tar -xzvf  %sbak/%s.tar.gz -C %s" %(dir,fileName,dir))
        #cmd = "xcopy  %sbak\\%s %s" %(dir,fileName,dir)
        cmd = "tar -xzvf  %sbak/%s.tar.gz -C %s" %(dir,fileName,dir)
        print cmd
        os.system(cmd)
        flag = 'True'
        statFile(dir,fileName,flag)
def getRealUrl(url=None):
    if not url:
        return None
    url = str(url).replace(' ','');
    keys = REQUEST_URL_MAP.keys();
    for key in keys:
        if url.startswith(key):
            return key
    return None
def handleFtpFile():
    # statFile('E:\\logs\\','djdiguanewserverdcn_ex150303.log')
    # statFile('E:\\logs\\','djdiguaserverdcn_ex150303.log')
    sql="select SRC_DIR, SRC_FILE, LOCAL_DIR, LOCAL_FILE, IP, PORT, IS_DELETE_SRC_FILE, IS_DELETE_LOCAL_FILE, CREATED_DATE from FTP_LOG_CONFIG where id in (73,74,75,118,173,174,175,176,197,208) order by ID;"
    rows =  dbUtil_168.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        srcFile=row[1]%( HANDLE_DATE)
        localFile=row[3]%( HANDLE_DATE)
        time.sleep(1)
        print "%s%s"%(row[2], localFile)
        statFile(row[2] , localFile)
        print localFile, 'over'


def clearData():
    cretateTable()
    sql1 = "delete from DIGUA_REQUEST_URL_PV_STAT  where STAT_DATE=%s"
    dbUtil_168.delete(sql1,  ( CREATE_DATE,))
def cretateTable():
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="%s"' %(TABLE_NAME,)
    count =  dbUtil_168.queryCount(sql)
    if(count==0):
        sql = '''create table %s
                (`ID` int(11) NOT NULL AUTO_INCREMENT,
                      `URL` varchar(200) default null,
                      `REMARK`  varchar(200) default null,
                      `PV` int(11) DEFAULT '0',
                      `UV` int(11) DEFAULT '0',
                      `STAT_DATE` datetime DEFAULT NULL,
                       PRIMARY KEY (`ID`),
                      KEY `IX_DIGUA_STAT_DATE` (`STAT_DATE`)
                ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''' %(TABLE_NAME,)
        dbUtil_168.update(sql)
def statDataUrlPv():
    sql = "insert into "+TABLE_NAME+"(URL,REMARK,PV,UV,STAT_DATE) values (%s,%s,%s,%s,%s)"
    print sql
    dataList = []
    sorted( URL_STAT_PV.items(),key=lambda dsc:dsc[1],reverse=True)
    for row in  URL_STAT_PV.items():
        if not row:
            continue
        url = row[0]
        REMARK = getRemark(url)
        dataList.append((row[0],REMARK,row[1],len(URL_STAT_UV[row[0]]),CREATE_DATE))
    if dataList:
        global dbUtil_168
        dbUtil_168 = DBUtil(dataBase_droid_stat_id)
        insertData( dbUtil_168, sql, dataList)
        dataList = []
def getRemark(url=None):
  REMARK = REQUEST_URL_MAP[url]
  return REMARK
def sendMail():
    global mailContents
    mailContents = '执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), HANDLE_DATE, ERROR_MSG)
    mail = MailUtil(None, MAIL_SERVER,  MAIL_FROM_NAME,  MAIL_FROM_ADDRESS,  MAIL_TO,  MAIL_LOGIN_USER,  MAIL_LOGIN_PASS,  MAIL_SUBJECT)
    mail.sendMailMessage(mailContents)
###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    opts = OptsUtil.getOpts(sys.argv)
    fileDate = None
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
    else:
        fileDate = opts.get('--FILE_DATE')
    handleDate = datetime.datetime.strptime(fileDate, '%Y-%m-%d')
    print handleDate
    try:
        init(handleDate)
        clearData()
        handleFtpFile()
        statDataUrlPv()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()
