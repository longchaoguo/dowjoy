#!/usr/bin/python
# -*- coding: cp936 -*-

__author__ = "$Author: guoqiang.sun$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2015��4��3��10:56:14 $"
###########################################
#�عϷ���urlͳ��
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
#��ȡ��־����ʱ��
HANDLE_DATE = None
CREATE_DATE=None
fileDir = "/usr/local/bin/cdroid/report/data/"
#fileDir = "e:/logs/"
reportFile = None
REQUEST_URL_MAP={'/newdiguaserver/game/index720':u'�µع���Ϸ��ѡ',
                 '/newdiguaserver/game/newest':u'�µع���Ϸ����',
                 '/newdiguaserver/game/star':u'�µع���Ϸ����',
                 '/newdiguaserver/game/rank':u'�µع���Ϸ����',
                 '/newdiguaserver/activity/list':u'�µع���Ϸר��',
                 '/newdiguaserver/game/category':u'�µع���Ϸ����',
                 '/newdiguaserver/netgame/recommend':u'�µع����ξ�ѡ',
                 '/newdiguaserver/netgame/rank':u'�µع���������',
                 '/newdiguaserver/netgame/new/list':u'�µع���������',
                 '/newdiguaserver/netgame/category/list':u'�µع����η���',
                 '/newdiguaserver/software/essential':u'�µع�����ر�',
                 '/newdiguaserver/software/newest':u'�µع��������',
                 '/newdiguaserver/software/rank':u'�µع��������',
                 '/newdiguaserver/software/category':u'�µع��������',
                 '/newdiguaserver/emulator/list':u'�µع�ģ����',
                 '/newdiguaserver/game/essential':u'�µعϱر���Ϸ',
                 '/newdiguaserver/game/large':u'�µعϴ�����Ϸ',
                 '/newdiguaserver/game/bt':u'�µع��޸��ƽ�',
                 '/newdiguaserver/res/detail':u'�µع���Ϸ����ӿ�',
                 '/newdiguaserver/comment/':u'�µع����۽ӿ�',
                 '/v64x/dir/recomment?pn=1&ps=30&editorId=1':u'�ϵع���Ϸ��ѡ',
                 '/dir/latest?pn=1&ps=10&rt=1':u'�ϵع���Ϸ����',
                 '/dir/5star?pn=1&ps=10&rt=1':u'�ϵع���Ϸ����',
                 '/dir/ranking/hot-game?pn=1&ps=10':u'�ϵع���Ϸ����',
                 '/dir/new_activity_latest?pn=1&ps=10':u'�ϵع���Ϸר��',
                 '/dir/category?rt=1':u'�ϵع���Ϸ����',
                 '/dir/ngchannel/recommand':u'�ϵع����ξ�ѡ',
                 '/dir/ngchannel/hotest?pn=1&ps=10':u'�ϵع���������',
                 '/dir/ngchannel/ngmemorabilia':u'�ϵع���������',
                 '/newdiguaserver/netgame/category/list':u'�ϵع����η���',
                 '/v64x/dir/essentialsoftwares':u'�ϵع�����ر�',
                 '/dir/ranking/hot-software?pn=1&ps=10':u'�ϵع��������',
                 '/dir/latest?pn=1&ps=10&rt=2':u'�ϵع��������',
                 '/dir/category?rt=2':u'�ϵع��������',
                 '/dir/emulator/arcade':u'�ϵع�ģ����',
                 '/v64x/dir/essentialgames':u'�ϵعϱر���Ϸ',
                 '/v64x/dir/largegames?rtype=1&pn=1&ps=10':u'�ϵعϴ�����Ϸ',
                 '/v64x/dir/btgames?pn=1&ps=10&rtype=GAME':u'�ϵع��޸��ƽ�',
                 '/item//':u'�ϵع���Ϸ����ӿ�',
                 '/v64x/comment/list':u'�ϵع����۽ӿ�'}
pattern = re.compile(r"""\[(?P<TIME>\S*) \S*\] \S* (?P<URL>(\S*( \?\S*)?))\s*(?P<IP>([\d\.]*(\,\s+[\d\.]*)?))\s*(?P<STATUS>\d+) - \S* \((?P<UA>.+)\) \S* {.*\\"imei\\":\\"(?P<IMEI>\w+)\\".*}""")
#####�ʼ���������
ERROR_MSG = None
MAIL_SERVER = "mail.downjoy.com"
MAIL_FROM_NAME = u"������������".encode("gbk")
MAIL_FROM_ADDRESS = "webmaster@downjoy.com"
MAIL_LOGIN_USER = "webmaster@downjoy.com"
MAIL_LOGIN_PASS = "htbp3dQ1sGcco!q"
MAIL_SUBJECT = "��Ϸ������Ϸ����ҳ������ҳ������ͳ�ƴ�����Ϣ"
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

#����־���
def statFile(dir,fileName,flag = 'False'):
    # ������ļ������ڣ��׳��쳣
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
            ERROR_MSG = u'��ѹ�ļ�%sbak/%s.tar.gzʧ��' %(dir,fileName)
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
    mailContents = 'ִ�����ڣ�%s\nͳ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), HANDLE_DATE, ERROR_MSG)
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
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()
