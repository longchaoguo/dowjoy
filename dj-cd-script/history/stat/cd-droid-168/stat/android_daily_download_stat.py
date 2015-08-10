#!/usr/bin/python
# -*- coding: cp936 -*-
__author__ = 'sgq'
'''
 每日下载日志分析
'''
import os
import datetime
import re
import traceback
import logging
from djutil.RemoveRepeatUtil import *
from djutil.MailUtil import *
from djutil.DBUtil import *
from djutil.OptsUtil import OptsUtil
import MySQLdb
mailServer_ = "mail.downjoy.com"
mailFromName_ = u"当乐数据中心".encode("cp936")
mailFromAddr_ = "webmaster@downjoy.com"
mailLoginUser_ = "webmaster@downjoy.com"
mailLoginPass_ = "htbp3dQ1sGcco!q"
mailSubject_ = u"地瓜统计日志统计错误信息".encode("cp936")
mailTo_ = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
logDirCDN = "/opt/logs/addownlog/cdn/"
#logDirCDN = "e:/logs/"
logTemp = "/home/yunying/log_data/"
#logTemp = "e:/logs/"
CARRIER_WANGSU="wangsu"#网宿
CARRIER_DNION="dnion"#帝联
CARRIER_GAOSHENG="gaosheng"
TABLE_NAME_LOG='ANDROID_DAILY_DOWNLOAD_LOG'
TABLE_NAME_STAT='ANDROID_DAILY_DOWNLOAD_STAT'
removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60)
FIELDS = [u'CHANNELID',U'DATATYPE', u'GAMEID', u'GAMENAME', u'GAMEONLINETIME',u'GAMETYPE', u'IP', u'RESOURCECATERGORY', u'TIME']
FIELDS_STR = '(CHANNELID,DATATYPE,GAMEID,GAMENAME,GAMEONLINETIME,GAMETYPE,IP,RESOURCECATERGORY,TIME)'
delimiter='`'
logName="android_daily_download"
#每日下载数据统计结果
DAILY_DOWNLOAD_STAT_RESULT={}
#游戏ID与游戏名称
GAME_ID_GAME_NAME = {}
#游戏id与游戏类型
GAME_ID_GAME_TYPE = {}
#游戏id与资源类型
GAME_ID_RESOURCE_TYPE={}
#网游游戏ID与游戏名称
NET_GAME_ID_GAME_NAME = {}
#网游游戏id与游戏类型
NET_GAME_ID_GAME_TYPE = {}
#虚拟机游戏ID与游戏名称
EMULATOR_GAME_ID_GAME_NAME = {}
#虚拟机游戏id与游戏类型
EMULATOR_GAME_ID_GAME_TYPE = {}
#游戏ID与游戏上线时间
GAME_ID_CREATE_DATE = {}
#网游游戏ID与游戏上线时间
NET_GAME_ID_CREATE_DATE = {}
#虚拟机游戏ID与游戏上线时间
EMULATOR_GAME_ID_CREATE_DATE = {}
#游戏ID与游戏数据类型BT
GAME_ID_DATA_TYPE = {}
droid_game_dbUtil = DBUtil("droid_game_10")
stat_data_id = 'droid_stat_168'
droid_stat_dbUtil = DBUtil(stat_data_id)
web = 'web_1'
setup_digua_pc = 'web_2'
wap = 'wap_1'
cooperation_360 = '360_1'
setup_360 = '360_2'
juhe_360 = '360_3'
wdj = 'wandoujia_1'
setup_wdj = 'wandoujia_2'
baidu = 'baidu_1'
tengxun_soso = 'tencent_1'
setup_tengxun = 'tencent_2'
tengxun_channel = 'tencent_3'
duote = 'duote_1'
digua = 'digua_1'
newdigua = 'digua'
digua_pc = 'digua_2'
ngcenter = 'ngcenter_1'
thunder = 'thunder_1'#该渠道已撤销，下载量计入web

CHAN_FLAG_DICT = {
                  web: 10,
                  wap: 20,
                  digua: 30,
                  newdigua: 30,
                  cooperation_360: 40,
                  setup_360: 50,
                  wdj: 60,
                  setup_wdj: 70,
                  baidu: 80,
                  tengxun_soso: 90,
                  setup_tengxun: 100,
                  tengxun_channel: 110,
                  duote: 120,
                  juhe_360: 130,
                  digua_pc: 140,
                  setup_digua_pc: 150,
                  ngcenter: 30,
                  thunder: 10,
                 }
DOMAIN_CDN_CARRIER = {
                  "g.androidgame-store.com.cn":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "g.androidgame-store.com.hk":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "g.androidgame-store.com.ov":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "g2.androidgame-store.com":   {"carrier":CARRIER_GAOSHENG,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*)\]\s+\"\w+\s\/(?P<URL>g2.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?\s{1,2}\S*\s{1,2}\"\s{1,2}(?P<STATUS>\d+)\s{1,2}\d+\s{1,2}\S+\s{1,2}\S+\s{1,2}\S(?P<UA>[^\;]*).*$")},
                  "res5.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "res5.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "res5.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res8.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "res8.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  # "res8.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "down.androidgame-store.com":{"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>down.androidgame-store.com)?(:80)?(/android)?[/\S]*/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "u.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[40,50,60,70,80,90,100,110,120,130],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>u.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "p.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[20],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>p.androidgame-store.com)?(:80)?(/(\w)+){0,2}(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "qr.androidgame-store.com":  {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>qr.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res3.d.cn":                 {"carrier":CARRIER_DNION,"username":"res5push","password":"Res5!@#123","channel":[10,20,30,40,50,60,70,80,90,100,110,120,130],"pattern":     re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>res3.d.cn)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")}
                  }
def initGame():
    sql_type = "select ID,`NAME`,CREATED_DATE,DATA_TYPE from GAME"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        GAME_ID_GAME_NAME[int(row[0])] = row[1]
        GAME_ID_CREATE_DATE[int(row[0])] = row[2]
        GAME_ID_DATA_TYPE[int(row[0])] = row[3]
    sql_type = "select a.ID,b.`NAME` from GAME a LEFT JOIN GAME_CATEGORY b on a.GAME_CATEGORY_ID = b.ID"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        GAME_ID_GAME_TYPE[int(row[0])] = row[1]
    sql = 'select ID, RESOURCE_TYPE from GAME'
    rows = droid_game_dbUtil.queryList(sql)
    if not rows:
        return False
    for row in rows:
        GAME_ID_RESOURCE_TYPE[int(row[0])] = int(row[1])
    return True
def initNetGame():
    sql_type = "SELECT A.ID,B.`NAME`,A.CREATED_DATE FROM NETGAME_GAME A LEFT JOIN NETGAME_CHANNEL B ON A.CHANNEL_ID=B.ID"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        NET_GAME_ID_GAME_NAME[int(row[0])] = row[1]
        NET_GAME_ID_CREATE_DATE[int(row[0])] = row[2]
    sql_type = "SELECT A.ID,B.TAG_NAMES FROM NETGAME_GAME A LEFT JOIN NETGAME_CHANNEL B ON A.CHANNEL_ID=B.ID"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        NET_GAME_ID_GAME_TYPE[int(row[0])] = row[1]
def initEmulatorGame():
    sql_type = "select ID,`NAME`,CREATED_DATE from EMULATOR_GAME"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        EMULATOR_GAME_ID_GAME_NAME[int(row[0])] = row[1]
        EMULATOR_GAME_ID_CREATE_DATE[int(row[0])] = row[2]
    sql_type = "select a.ID,b.`NAME` from EMULATOR_GAME a LEFT JOIN GAME_CATEGORY b on a.GAME_CATEGORY_ID = b.ID"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        EMULATOR_GAME_ID_GAME_TYPE[int(row[0])] = row[1]
'''
获取游戏的上线时间
0:单机
1：网游
2：模拟器
'''
def getGameCreateDate(gameId=None,gameType=None):
   if gameType==0: ##单机
       if GAME_ID_CREATE_DATE.has_key(gameId):
           return  str(GAME_ID_CREATE_DATE[int(gameId)])
   elif gameType==1:##网游
       if NET_GAME_ID_CREATE_DATE.has_key(gameId):
           return  str(NET_GAME_ID_CREATE_DATE[int(gameId)])
   elif gameType==2:##模拟器
       if EMULATOR_GAME_ID_CREATE_DATE.has_key(gameId):
           return  str(EMULATOR_GAME_ID_CREATE_DATE[int(gameId)])
   return datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H:%M:%S')
def getGameDataType(gameId=None):
   if GAME_ID_DATA_TYPE.has_key(gameId):
       return  bytes(GAME_ID_DATA_TYPE[int(gameId)])
   return '0'
def getGameName(gameId=None):
  if GAME_ID_GAME_NAME.has_key(int(gameId)):
      return GAME_ID_GAME_NAME[int(gameId)]
  else:
      return "unknown"
def getGameType(gameId=None):
  if GAME_ID_GAME_TYPE.has_key(int(gameId)):
      return GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "unknown"
def getGameResourceType(gameId=None):
  if GAME_ID_RESOURCE_TYPE.has_key(int(gameId)):
      return GAME_ID_RESOURCE_TYPE[int(gameId)]
  else:
      return 1
def getNetGameName(gameId=None):
  if NET_GAME_ID_GAME_NAME.has_key(int(gameId)):
      return NET_GAME_ID_GAME_NAME[int(gameId)]
  else:
      return "unknown"
def getNetGameType(gameId=None):
  if NET_GAME_ID_GAME_TYPE.has_key(int(gameId)):
      if not NET_GAME_ID_GAME_TYPE[int(gameId)]:
          return 'unknown'
      return NET_GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "unknown"
def getEmulatorGameName(gameId=None):
  if EMULATOR_GAME_ID_GAME_NAME.has_key(int(gameId)):
      return EMULATOR_GAME_ID_GAME_NAME[int(gameId)]
  else:
      return "unknown"
def getEmulatorGameType(gameId=None):
  if EMULATOR_GAME_ID_GAME_TYPE.has_key(int(gameId)):
      return EMULATOR_GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "unknown"
def sendMail(mailContents=None):
    try:
        mail = MailUtil(None, mailServer_,mailFromName_, mailFromAddr_,['guoqiang.sun@downjoy.com'],mailLoginUser_,mailLoginPass_,mailSubject_)
        mail.sendMailMessage(mailContents)
    except Exception, e:
        traceback.print_exc()
        print e.message
def deleteLogFile(logDate):
    filePath = logTemp+"/"+logName+"."+logDate
    if os.path.exists(filePath):
       os.remove(filePath)
'''
  创建表结构
'''
def cretateTable():
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="' + TABLE_NAME_STAT+'"'
    count = droid_stat_dbUtil.queryCount(sql)
    if(count==0):
        sql = '''CREATE TABLE `%s` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `CHANNELID` varchar(50) DEFAULT NULL,
              `DATATYPE` varchar(200) DEFAULT NULL,
              `GAMEID` double DEFAULT NULL,
              `GAMENAME` varchar(200) DEFAULT NULL,
              `COUNT` int(11) DEFAULT 0,
              `RESOURCECATERGORY` varchar(200) DEFAULT NULL,
              `GAMETYPE` varchar(200) DEFAULT NULL,
              `STAT_DATE` datetime DEFAULT NULL,
              PRIMARY KEY (`id`),
              KEY `GAMEID` (`GAMEID`,`STAT_DATE`),
              KEY `DATATYPE` (`DATATYPE`,`STAT_DATE`),
              KEY `STAT_DATE` (`STAT_DATE`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''' %(TABLE_NAME_STAT,)
        if sql:
            droid_stat_dbUtil.update(sql)
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="' + TABLE_NAME_LOG+'"'
    count = droid_stat_dbUtil.queryCount(sql)
    if(count==0):
        sql = '''CREATE TABLE `%s` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `CHANNELID` varchar(50) DEFAULT NULL,
              `DATATYPE` varchar(200) DEFAULT NULL,
              `GAMEID` double DEFAULT NULL,
              `GAMENAME` varchar(200) DEFAULT NULL,
              `GAMEONLINETIME` varchar(200) DEFAULT NULL,
              `GAMETYPE` varchar(200) DEFAULT NULL,
              `IP` varchar(50) DEFAULT NULL,
              `RESOURCECATERGORY` varchar(200) DEFAULT NULL,
              `TIME` datetime DEFAULT NULL,
              PRIMARY KEY (`id`),
              KEY `GAMEID` (`GAMEID`,`TIME`),
              KEY `DATATYPE` (`DATATYPE`,`TIME`),
              KEY `TIME` (`TIME`)
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''' %(TABLE_NAME_LOG,)
        if sql:
            droid_stat_dbUtil.update(sql)
    pass
def initConfig():
      initGame()
      initNetGame()
      initEmulatorGame()
def clearData(handleDate=None):
    sql = "truncate table %s ;"%(TABLE_NAME_LOG,)
    droid_stat_dbUtil.update(sql,())
    sql = "delete from %s where STAT_DATE<='%s' and STAT_DATE>='%s'" %(TABLE_NAME_STAT,datetime.datetime.strftime(handleDate,"%Y-%m-%d 23:59:59"),datetime.datetime.strftime(handleDate,"%Y-%m-%d 00:00:00"))
    droid_stat_dbUtil.update(sql,())
'''
统计数据
'''
def statData():
    opts = OptsUtil.getOpts(sys.argv)
    fileDate = None
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 2), '%Y-%m-%d')
    else:
        fileDate = opts.get('--FILE_DATE')
    handleDate = datetime.datetime.strptime(fileDate, '%Y-%m-%d')
    print handleDate
    initConfig()
    cretateTable()
    clearData(handleDate)
    deleteLogFile(fileDate)
    logging.root.handlers=[]
    logging.basicConfig(format='%(message)s',filename=logTemp+'/%s.%s' %(logName,fileDate),level=logging.DEBUG)
    for key in DOMAIN_CDN_CARRIER:
        print "=================start %s  doMain %s fileDate %s ======" % (datetime.datetime.now(),key,handleDate)
        Main(key,handleDate)
    loadDataInMysql(handleDate.strftime("%Y-%m-%d"))
    stat_daily_download(fileDate)


def Main(domain=None,fileDate=None):
        carrier = DOMAIN_CDN_CARRIER.get(domain)
        readSingleLogFile(carrier.get('pattern'),getCDNFilename(domain,fileDate))
'''
 获取下载日志文件名
'''
def getCDNFilename(domain,fileDate):
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if CARRIER_WANGSU == carrier.get("carrier") :
        fileDateStr = fileDate.strftime( "%Y-%m-%d")
        return "%s-0000-2330_%s.log"%(fileDateStr,domain)
    elif CARRIER_DNION == carrier.get("carrier") :
        fileDateStr = fileDate.strftime( "%Y%m%d")
        return "%s_%s.log"%(domain,fileDateStr)
    elif CARRIER_GAOSHENG == carrier.get("carrier") :
        fileDateStr = datetime.datetime.strftime(fileDate, "%Y%m%d")
        return "%s-%s.log"%(domain,fileDateStr)
'''
 读取文件
'''
def readSingleLogFile(pattern,fileName=None):
    if not os.path.exists(logDirCDN+fileName):
        print '文件不存在，%s' %(fileName,)
        return
    f = None
    line = None
    dicts = None
    try:
        f=open(logDirCDN+fileName, "rb")
        while 1:
            lines = f.readlines(512*1024*1024)
            if not lines:
                break
            line_count = len(lines)
            URL = None
            for a in xrange(line_count):
                line=lines[a]
                if not line: break
                line=line.strip()
                m=pattern.match(line)
                if not m:
                    continue
                dicts = m.groupdict()
                handleLogFiled(FIELDS,dicts)
            lines = []
    except Exception,e:
        traceback.print_exc()
    f.close()
def excuteSql(connName=droid_stat_dbUtil, sql = None, params = None):
        connDict = getConnection(connName)
        cursor = None
        conn =  None
        try:
            if (not sql): return False
            conn =  connDict.get('CONN')
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return True
        except Exception, e:
            traceback.print_exc()
            raise e
        finally:
            try:
                if cursor: cursor.close();
            except Exception, e:
                print e
            try:
                if conn:
                    conn.close()
            except:
                print e

def getConnection(connName):
    dbItem = DBConnCreater.getDBConfig(connName)
    if not dbItem: raise 'no db config info:' + connName
    rs = {}
    conn = None
    if dbItem.get('type') == 'MYSQL':
        rs['TYPE'] = 'MYSQL'
        conn = MySQLdb.connect(host = dbItem.get('host'), port = dbItem.get('port', 3306), user = dbItem.get('user'), passwd = dbItem.get('password'), db = dbItem.get('database'), charset = dbItem.get('charset'), use_unicode = dbItem.get('use_unicode'),local_infile = 1 )
    if not conn: raise 'get conn error:' + connName
    rs['CONN'] = conn
    return rs
'''
 把文件插入数据库
'''
def loadDataInMysql(logDate):
    try:
        if not os.path.exists(logTemp+logName+"."+logDate):
            return
        sql = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s fields TERMINATED by '%s' %s;"  %(logTemp+logName+"."+logDate,TABLE_NAME_LOG,delimiter,str(FIELDS_STR))
        print sql
        excuteSql(stat_data_id,sql,())
    except Exception, e:
        traceback.print_exc()
        sendMail('向mysql导入日志文件出错，表名：%s，异常信息:%s' %(TABLE_NAME_LOG,e.message))

def stat_daily_download(statDate):
    try:
        sql = "insert into %s(CHANNELID,DATATYPE,GAMEID,GAMENAME,GAMETYPE,COUNT,RESOURCECATERGORY,STAT_DATE) select CHANNELID,DATATYPE,GAMEID,GAMENAME,GAMETYPE,COUNT(ID) AS C,RESOURCECATERGORY,'%s' FROM %s " \
          " GROUP BY CHANNELID,GAMEID " %(TABLE_NAME_STAT,(statDate+" 00:00:00"),TABLE_NAME_LOG)
        print sql
        droid_stat_dbUtil.update(sql,())
    except Exception, e:
        traceback.print_exc()
        sendMail('向mysql导入日志文件出错，表名：%s，异常信息:%s' %(TABLE_NAME_LOG,e.message))
'''
解析正则表达式匹配出来的字段并写入文件
'''
def handleLogFiled(fileds=None,dicts=None):
    flag = handleFiled(removeUtil,dicts)
    if flag == False:
        return
    values = {}
    for filed in fileds:
        if dicts.has_key(filed):
           values[filed] = dicts[filed]
        else:
            values[filed] = ''
    msg = ''
    try:
        for filed in fileds:
            if len(str(msg))>0:
                msg = msg+delimiter
            if values.has_key(filed):
                if not values[filed]:
                    print 'not content %s' %(filed,)
                    return
                msg = msg+values[filed]
        loadDataInLog(msg)
    except Exception,e:
        traceback.print_exc()

'''
 解析正则表达式匹配出来的字段
'''
def handleFiled(removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60),values={}):
    status = values['STATUS']
    if status not in ['200','206']:
        return False
    recordTime = values['TIME']
    ip = values['IP']
    grid = None
    domain = values['URL']
    source = '';
    if(values.has_key('SOURCE')):
        source = values['SOURCE']
    fileName = values['FILE_NAME']
    ua = values['UA']
    if values.has_key('GAMEID'):
          gid = values['GAMEID']
          if not str(gid).isdigit():
              return False
          grid = int(gid)
          flag =  values['CHANNELID']
          if domain in ["res5.d.cn","res8.d.cn"]: ##网游
              values['RESOURCECATERGORY']=u'网游'
              values['GAMENAME']=getNetGameName(grid)
              values['GAMEONLINETIME']=getGameCreateDate(grid,1)
              if (flag) and (CHAN_FLAG_DICT.has_key(flag)):
                 values['CHANNELID'] = str(CHAN_FLAG_DICT[flag])
              elif source.find("android.d.cn", 0) > 0:
                 values['CHANNELID'] = '10'
              elif ua.find("Digua/", 0) > 0:
                ua=ua[0:ua.find("Digua/", 0)]#ua中，包含了cdn下载相关的调试信息
                values['CHANNELID'] = '30'
              values['GAMETYPE']=getNetGameType(grid)
              values['DATATYPE']=getGameDataType(grid)
          else: ##软件 单机游戏 虚拟机游戏
              if values.has_key('GAME'):
                if(values['GAME']=='game1'):
                  grid=grid^110111
                elif(values['GAME']=='emulatorgame'):
                  grid=grid^110111
              values['RESOURCECATERGORY']=u'单机'
              if(values['GAME']=='emulatorgame'):
                  values['GAMENAME']=getEmulatorGameName(grid)
                  values['GAMETYPE']=getEmulatorGameType(grid)
                  values['GAMEONLINETIME']=getGameCreateDate(grid,2)
                  values['RESOURCECATERGORY']=u'虚拟机'
              else:
                  if str(getGameResourceType(grid)) == '2':
                      values['RESOURCECATERGORY']=u'软件'
                  values['GAMENAME']=getGameName(grid)
                  values['GAMETYPE']=getGameType(grid)
                  values['GAMEONLINETIME']=getGameCreateDate(grid,0)
              if grid == 374 and domain.find("g.androidgame-store.com") > -1 :#地瓜升级接口
                   return False
              if ua.find("Digua/", 0) > 0:
                  ua=ua[0:ua.find("Digua/", 0)]#ua中，包含了cdn下载相关的调试信息
              else :
                  ua="-"
              channel = 0
              if flag and CHAN_FLAG_DICT.has_key(flag):
                    channel = CHAN_FLAG_DICT[flag]
              if channel == 0:
                if domain.find("g.androidgame-store.com") > -1 :
                    if values['FILE_NAME'].find(".apk?", 0) > 0 or values['FILE_NAME'].find(".dpk?", 0) > 0:
                        channel = 140
                    else:
                        channel = 30 #默认是地瓜
                elif "down.androidgame-store.com" == domain :
                    channel = 10 #默认是android.d.cn网站
                elif "u.androidgame-store.com" == domain :
                    channel = 80 #默认是百度
                elif "p.androidgame-store.com" == domain :
                    channel = 20 #默认是a.d.cn网站
                elif "qr.androidgame-store.com" == domain :
                    channel = 10 #默认是android.d.cn网站
                elif "res3.d.cn" == domain :
                    channel = 30 #默认是地瓜
                elif "g2.androidgame-store.com" == domain :
                    channel = 30 #默认是地瓜
              values['DATATYPE']=getGameDataType(grid)
              values['CHANNELID'] = str(channel)
    else:
          return False
    if not values['CHANNELID']:
       values['CHANNELID']='unknown'
    values['GAMEID']=str(grid)
    recordTime=getRecordTime(recordTime)
    values['TIME']=recordTime
    if not removeUtil.isValidByTime(fileName+ip+ua, recordTime):
        return False
    return True
def getRecordTime(recordTimeStr):
     if(recordTimeStr.find('T')>-1):
         tempTime=datetime.datetime.strptime(recordTimeStr, '%Y-%m-%dT%H:%M:%S.%f+08:00')
         return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')
     tempTime=datetime.datetime.strptime(recordTimeStr, '%d/%b/%Y:%H:%M:%S')
     return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')
'''
把数据写入到日志文件中
'''
def loadDataInLog(msg=None):
    try:
        logging.debug(msg)
    except Exception, e:
        traceback.print_exc()
        sendMail('数据写入文件出错，文件名为：%s，异常信息:%s' %(logging._srcfile,e.message))
if __name__== '__main__':
    try:
       statData()
    except Exception, e:
       traceback.print_exc()
       sendMail('分析每日下载日志文件出错，异常信息' %(e.message))