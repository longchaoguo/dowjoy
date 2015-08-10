#!/usr/bin/python
# -*- coding: cp936 -*-
__author__ = 'sgq'
'''
 下载日志分析，分析开始日期前多少天的下载日志，并把分析的数据保存为文件导入数据库
'''
import os
import datetime
import re
import traceback
import logging
from djutil.RemoveRepeatUtil import *
from djutil.MailUtil import *
from djutil.DBUtil import *
mailServer_ = "mail.downjoy.com"
mailFromName_ = u"当乐数据中心".encode("cp936")
mailFromAddr_ = "guoqiang.sun@downjoy.com"
mailLoginUser_ = "guoqiang.sun@downjoy.com"
mailLoginPass_ = "Pa12345678"
mailSubject_ = u"地瓜统计日志统计错误信息".encode("cp936")
mailTo_ = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'
logDirCDN = "/opt/logs/addownlog/cdn/"
logTemp = "/home/guoqiang.sun/logs2/"
ftpUrl = 'ftp://ftp.wslog.chinanetcenter.com'
httpUrl = 'http://customer.dnion.com/DCC/logDownLoad.do?'
CARRIER_WANGSU="wangsu"#网宿
CARRIER_DNION="dnion"#帝联
tableName='ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG'
removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60)
fileds = [u'DATATYPE', u'GAMEID', u'GAMENAME', u'GAMEONLINETIME', u'IP', u'RESOURCECATERGORY', u'TIME']
delimiter='`'
logName="androidgame_isbt_isnewgame"
#游戏ID与游戏名称
GAME_ID_GAME_NAME = {}
#游戏id与游戏类型
GAME_ID_GAME_TYPE = {}
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
droid_stat_dbUtil = DBUtil("droid_stat_168")
DOMAIN_CDN_CARRIER = {
                  "g.androidgame-store.com.cn":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "g.androidgame-store.com.hk":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "g.androidgame-store.com.ov":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res5.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res5.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res5.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res5.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res8.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res8.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res8.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://)(?P<URL>res8.d.cn)?(:80)?(/[\w]+)*/(?P<GAMEID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "down.androidgame-store.com":{"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>down.androidgame-store.com)?(:80)?(/android)?[/\S]*/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "u.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[40,50,60,70,80,90,100,110,120,130],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>u.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "p.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[20],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>p.androidgame-store.com)?(:80)?(/(\w)+){0,2}(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "qr.androidgame-store.com":  {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>qr.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "res3.d.cn":                 {"carrier":CARRIER_DNION,"username":"res5push","password":"Res5!@#123","channel":[10,20,30,40,50,60,70,80,90,100,110,120,130],"pattern":     re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://)(?P<URL>res3.d.cn)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GAMEID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNELID>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                  "g5.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[40,50,60,70,80,90,100,110,120,130],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://g5.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")}
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
def initNetGame():
    sql_type = "SELECT A.ID,B.`NAME`,A.CREATED_DATE FROM NETGAME_GAME A LEFT JOIN NETGAME_CHANNEL B ON A.CHANNEL_ID=B.ID"
    rows = droid_game_dbUtil.queryList(sql_type, ())
    for row in rows:
        NET_GAME_ID_GAME_NAME[int(row[0])] = row[1]
        NET_GAME_ID_CREATE_DATE[int(row[0])] = row[2]
    sql_type = "SELECT A.ID,B.`NAME` FROM NETGAME_GAME A LEFT JOIN NETGAME_CHANNEL_TAG B ON A.CHANNEL_FLAG=B.ID"
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
      return "未知"
def getGameType(gameId=None):
  if GAME_ID_GAME_TYPE.has_key(int(gameId)):
      return GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "未知"
def getNetGameName(gameId=None):
  if NET_GAME_ID_GAME_NAME.has_key(int(gameId)):
      return NET_GAME_ID_GAME_NAME[int(gameId)]
  else:
      return "未知"
def getNetGameType(gameId=None):
  if NET_GAME_ID_GAME_TYPE.has_key(int(gameId)):
      return NET_GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "未知"
def getEmulatorGameName(gameId=None):
  if EMULATOR_GAME_ID_GAME_NAME.has_key(int(gameId)):
      return EMULATOR_GAME_ID_GAME_NAME[int(gameId)]
  else:
      return "未知"
def getEmulatorGameType(gameId=None):
  if EMULATOR_GAME_ID_GAME_TYPE.has_key(int(gameId)):
      return EMULATOR_GAME_ID_GAME_TYPE[int(gameId)]
  else:
      return "未知"
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
def cretateTable():
    sql = 'select count(TABLE_NAME) from INFORMATION_SCHEMA.TABLES where TABLE_NAME="' + tableName+'"'
    count = droid_stat_dbUtil.queryCount(sql)
    if(count==0):
        sql = '''CREATE TABLE `ANDROID_ANDROIDGAME_ISBT_ISNEWGAM_LOG` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `DATATYPE` varchar(200) DEFAULT NULL,
  `GAMEID` double DEFAULT NULL,
  `GAMENAME` varchar(200) DEFAULT NULL,
  `GAMEONLINETIME` varchar(200) DEFAULT NULL,
  `IP` varchar(200) DEFAULT NULL,
  `RESOURCECATERGORY` varchar(200) DEFAULT NULL,
  `TIME` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `GAMEID` (`GAMEID`,`TIME`),
  KEY `DATATYPE` (`DATATYPE`,`TIME`),
  KEY `GAMEID_2` (`GAMEID`,`GAMEONLINETIME`,`TIME`),
  KEY `TIME` (`TIME`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''
        if sql:
            droid_stat_dbUtil.update(sql)
    pass
def initConfig():
      initGame()
      initNetGame()
      initEmulatorGame()
def update(dbUtil, sql = None, params = None):
        cursor = None
        try:
            if (not sql): return False
            cursor = dbUtil.getCursor()
            if not cursor:
                dbUtil.initDB(dbUtil)
                cursor = dbUtil.conn.cursor()
            cursor.execute('set global local_infile=1;')
            dbUtil.conn.commit()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            dbUtil.conn.commit()
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
                if dbUtil.closeAuto:
                    dbUtil.close()
            except:
                print e
def statData():
   startDateStr="2015-03-10 00:00:00"
   startDate = datetime.datetime.strptime(startDateStr,"%Y-%m-%d %H:%M:%S")
   initConfig()
   cretateTable()
   for i in range(17):
       handleDate = startDate-datetime.timedelta(days=i)
       deleteLogFile(handleDate.strftime("%Y-%m-%d"))
       logging.root.handlers=[]
       logging.basicConfig(format='%(message)s',filename=logTemp+'/%s.%s' %(logName,handleDate.strftime("%Y-%m-%d")),level=logging.DEBUG)
       sql = "delete from %s where time<='%s' and time>='%s'" %(tableName,datetime.datetime.strftime(handleDate,"%Y-%m-%d 23:59:59"),datetime.datetime.strftime(handleDate,"%Y-%m-%d 00:00:00"))
       droid_stat_dbUtil.update(sql,())
       for key in DOMAIN_CDN_CARRIER:
            print "=================start %s  doMain %s fileDate %s ======" % (datetime.datetime.now(),key,handleDate)
            Main(key,handleDate)
       loadDataInMysql(handleDate.strftime("%Y-%m-%d"))
def Main(domain=None,fileDate=None):
        carrier = DOMAIN_CDN_CARRIER.get(domain)
        readSingleLogFile(carrier.get('pattern'),getCDNFilename(domain,fileDate))
def getCDNFilename(domain,fileDate):
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if CARRIER_WANGSU == carrier.get("carrier") :
        fileDateStr = fileDate.strftime( "%Y-%m-%d")
        return "%s-0000-2330_%s.log"%(fileDateStr,domain)
    elif CARRIER_DNION == carrier.get("carrier") :
        fileDateStr = fileDate.strftime( "%Y%m%d")
        return "%s_%s.log"%(domain,fileDateStr)
def readSingleLogFile(pattern,fileName=None):
    if not os.path.exists(logDirCDN+fileName):
        print '文件不存在，%s' %(fileName,)
        return
    f = None
    line = None
    dicts = None
    try:
        f=open(logDirCDN+fileName, "rb")
        while True:
            line=f.readline()
            if not line: break
            line=line.strip()
            m=pattern.match(line)
            if not m:
                continue
            dicts = m.groupdict()
            handleLogFiled(fileds,dicts)
    except Exception,e:
        traceback.print_exc()
    f.close()
def loadDataInMysql(logDate):
    try:
        if not os.path.exists(logTemp+"/"+logName+"."+logDate):
            return
        fieldStr = '(DATATYPE,GAMEID,GAMENAME,GAMEONLINETIME,IP,RESOURCECATERGORY,TIME)'
        sql = 'LOAD DATA LOCAL INFILE \'%s\' INTO TABLE %s fields TERMINATED by \'%s\' %s;' %(logTemp+"/"+logName+"."+logDate,tableName,delimiter,str(fieldStr))
        print sql
        update(droid_stat_dbUtil,sql,())
    except Exception, e:
        traceback.print_exc()
        sendMail('向mysql导入日志文件出错，表名：%s，异常信息:%s' %(tableName,e.message))
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
                   # print values
                    return
                msg = msg+values[filed]
        loadDataInLog(msg)
    except Exception,e:
        traceback.print_exc()
def handleFiled(removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60),values={}):
      status=values['STATUS']
      if status not in ['200','206']:
          return False
      recordTime=values['TIME']
      ip=values['IP']
      grid = None
      domain = values['URL']
      if values.has_key('GAMEID'):
          gid = values['GAMEID']
          if not str(gid).isdigit():
              return False
          grid = int(gid)
          if domain in ["res5.d.cn","res8.d.cn"]: ##网游
              values['RESOURCECATERGORY']='网游'
              values['GAMENAME']=getNetGameName(grid)
              values['GAMEONLINETIME']=getGameCreateDate(grid,1)
          else: ##软件 单机游戏 虚拟机游戏
              if values.has_key('GAME'):
                  if(values['GAME']=='game1'):
                     grid=grid^110111
                  elif(values['GAME']=='emulatorgame'):
                     grid=grid^110111
              values['RESOURCECATERGORY']='单机'
              if(values['GAME']=='emulatorgame'):
                  values['GAMENAME']=getEmulatorGameName(grid)
                  values['GAMETYPE']=getEmulatorGameType(grid)
                  values['GAMEONLINETIME']=getGameCreateDate(grid,2)
              else:
                  values['GAMENAME']=getGameName(grid)
                  values['GAMETYPE']=getGameType(grid)
                  values['GAMEONLINETIME']=getGameCreateDate(grid,0)
          values['DATATYPE']=getGameDataType(grid)
      else:
          return False
      values['GAMEID']=str(grid)
      recordTime=getRecordTime(recordTime)
      values['TIME']=recordTime
      if not removeUtil.isValidByTime( str(grid)+ip, recordTime):
           return False
      return True
def getRecordTime(recordTimeStr):
       tempTime=datetime.datetime.strptime(recordTimeStr, '%d/%b/%Y:%H:%M:%S')
       return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')
#把数据写入到日志文件中
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
       sendMail('下载日志分析，分析开始日期前多少天的下载日志出错，异常信息' %(e.message))

