#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: helin $"

import re
import os
import sys
import time
import datetime
import StringIO
import traceback
import urllib
import smtplib
import email
from djutil.DBUtil import DBUtil
from djutil.RemoveRepeatUtil import RemoveRepeatUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil

logDirCDN = "/opt/logs/addownlog/cdn/"
#下载量排行前10的详情
reportFile = "/opt/logs/addownlog/mail/download_ip_top_10_%s.txt"

reportReceivers = ["dong.wei@downjoy.com","lin.he@downjoy.com"]
#reportReceivers = ["lin.he@downjoy.com"]

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

CARRIER_WANGSU="wangsu"#网宿
CARRIER_DNION="dnion"#帝联
CARRIER_GAOSHENG="gaosheng"
#域名和cdn提供商的对应关系
DOMAIN_CDN_CARRIER = {
                      "g.androidgame-store.com.cn":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "g3.androidgame-store.com.cn":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://g3.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "g.androidgame-store.com.hk":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "g.androidgame-store.com.ov":   {"carrier":CARRIER_WANGSU,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://g.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "g2.androidgame-store.com":   {"carrier":CARRIER_GAOSHENG,"username":"log","password":"logdown123!","channel":[30],"pattern":        re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*)\]\s+\"\w+\s\/(?P<URL>g2.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/+(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?\s{1,2}\S*\s{1,2}\"\s{1,2}(?P<STATUS>\d+)\s{1,2}\d+\s{1,2}\S+\s{1,2}\S+\s{1,2}\S(?P<UA>[^\;]*).*$")},
                      "res5.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res5.d.cn)?(:80)?/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "res5.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res5.d.cn)?(:80)?/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "res5.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res5.d.cn)?(:80)?/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "res8.d.cn.cn":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res8.d.cn)?(:80)?(/[\w]+)*/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "res8.d.cn.hk":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res8.d.cn)?(:80)?(/[\w]+)*/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      # "res8.d.cn.ov":                 {"carrier":CARRIER_WANGSU,"username":"log_downjoy","password":"logdown123!","channel":[10,30],"pattern":re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S*) +\S*\] +\S+ +(http://res8.d.cn)?(:80)?(/[\w]+)*/(?P<GID>.*)/(?P<FILE_NAME>\S+\.(apk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "down.androidgame-store.com":{"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://down.androidgame-store.com)?(:80)?(/android)?/+\S*/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "u.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[40,50,60,70,80,90,100,110,120,130],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://u.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "p.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[20],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://p.androidgame-store.com)?(:80)?(/(\w)+){0,2}(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "qr.androidgame-store.com":  {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[10],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://qr.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "res3.d.cn":                 {"carrier":CARRIER_DNION,"username":"res5push","password":"Res5!@#123","channel":[10,20,30,40,50,60,70,80,90,100,110,120,130],"pattern":     re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://res3.d.cn)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")},
                      "g5.androidgame-store.com":   {"carrier":CARRIER_DNION,"username":"cdnpush","password":"cdn123!@#push","channel":[40,50,60,70,80,90,100,110,120,130],"pattern":   re.compile("^(?P<IP>\S*) +\S* +\S* +\[(?P<TIME>\S+) +\S+\] +\S+ +(http://g5.androidgame-store.com)?(:80)?(/android)?/+new/+(?P<GAME>\w+)/+\d+/(?P<GID>\d+)/(?P<FILE_NAME>\S+\.(apk|dpk|zip))(\?(f=(?P<CHANNEL_FLAG>\w*))?)?.* +\S+\" +(?P<STATUS>\d+) +\S* +\"(?P<SOURCE>[^\"]*)\" +\"(?P<UA>[^\"]*)\".*$")}
                     
                      }
'''
#cdn日志文件名中的日期格式
CDN_LOG_DATE_FORMAT = {
                      "%s"%(CARRIER_WANGSU):"%Y-%m-%d",
                      "%s"%(CARRIER_DNION):"%Y%m%d"
                      }

CDN_LOG_FILENAME_FORMAT = {
                      "%s"%(CARRIER_WANGSU):"%s-0000-2330_%s.cn.log"%(dateStr,domain),
                      "%s"%(CARRIER_DNION):"%s_%s.log.gz"%(domain,dateStr)
                      }
'''
#游戏game_id和资源类型的对应关系字典
GAME_ID_RESOURCETYPE_DICT = {}

#统计下载量排名前十的下载情况
robot_count_dict ={}
robot_detail_dict ={}




droid_game = DBUtil('droid_game_10')
download_stat_168 = DBUtil('download_stat_168')


#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
now = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
mailSubject = u"安卓CDN下载量日志分析出错%s"%(now).encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: <br/>'
###########################################################
'''
获取cdn日志的文件名
@author: helin
@param param: domain 域名
@param param: date 日期对象
'''
def getCDNFilename(domain,fileDate):
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if CARRIER_WANGSU == carrier.get("carrier") :
        fileDateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
        return "%s-0000-2330_%s.log"%(fileDateStr,domain)
    elif CARRIER_DNION == carrier.get("carrier") :
        fileDateStr = datetime.datetime.strftime(fileDate, "%Y%m%d")
        return "%s_%s.log"%(domain,fileDateStr)
    elif CARRIER_GAOSHENG == carrier.get("carrier") :
        fileDateStr = datetime.datetime.strftime(fileDate, "%Y%m%d")
        return "%s-%s.log"%(domain,fileDateStr)

########################################下载日志功能开始#######################################################
'''
日志文件下载
@author: helin
@param domain:  cdn域名
@param fileDate:   日期对象
'''
def downloadLogFile(domain,fileDate):
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if CARRIER_WANGSU == carrier.get("carrier") : 
        downloadWangsuLogFile(domain,fileDate)
    elif CARRIER_DNION == carrier.get("carrier") : 
        downloadDnionLogFile(domain,fileDate)
    elif CARRIER_GAOSHENG == carrier.get("carrier") :
        downloadGaoshengFile(domain,fileDate)

'''
网宿cdn日志文件下载,日志必须是.gz结尾并且是gz压缩的，否则可能会出错
@author: helin
@param domain:  cdn域名
@param fileDate:   日期对象
'''
def downloadWangsuLogFile(domain,fileDate):
    #2014-04-27-0000-2330_g.androidgame-store.com.cn.log.gz
    global mailContents
    if not DOMAIN_CDN_CARRIER.has_key(domain):
        mailContents = mailContents + u"域名%s不存在，下载日志文件失败<br/>"%(domain)
        return
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if not os.path.exists(logDirCDN):
        os.makedirs(logDirCDN)
    gzFileName = "%s%s"%(getCDNFilename(domain,fileDate),".gz")
    destFilePath = logDirCDN + gzFileName
    mailContents = mailContents + u"开始下载日志文件：%s<br/>"%(gzFileName)
    rs=1
    attempts=0
    while attempts<20 :
        try:
            if os.path.exists(destFilePath) :
                os.remove(destFilePath)
            dir=domain[:-3]
            cmd = "wget  'ftp://ftp.wslog.chinanetcenter.com/%s/%s' --ftp-user='%s' --ftp-password='%s' -q -t 20 -O %s"%(dir,gzFileName,carrier["username"],carrier["password"],destFilePath)
            print cmd
            rs=os.system(cmd)    
            if rs!=0 or (os.path.exists(destFilePath) ==False) or (os.path.getsize(destFilePath)<1):
                attempts =  attempts + 1
                continue
            else :
                os.system('gzip -d -f %s'%destFilePath)
                localFile=destFilePath[:-3]
                if (os.path.exists(localFile) ==False) or (os.path.getsize(localFile)<1):
                    attempts =  attempts + 1
                    continue
                size = os.path.getsize(localFile)
                size = size/1024/1024
                mailContents = mailContents + u"重试次数：%s,下载文件%s成功,解压后文件大小为：%sM <br/>"%(attempts,localFile,size)
                break;
            
        except Exception, e:
            print e
            attempts =  attempts + 1
            continue
            
'''
高升cdn日志文件下载,日志必须是.tgz结尾，否则可能会出错
@author: sungq
@param domain:  cdn域名
@param fileDate:   日期对象
'''
def downloadGaoshengFile(domain,fileDate):
    #2014-04-27-0000-2330_g.androidgame-store.com.cn.log.gz
    global mailContents
    if not DOMAIN_CDN_CARRIER.has_key(domain):
        mailContents = mailContents + u"域名%s不存在，下载日志文件失败<br/>"%(domain)
        return
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    if not os.path.exists(logDirCDN):
        os.makedirs(logDirCDN)
    gzFileName = "%s%s"%(getCDNFilename(domain,fileDate),".tgz")
    destFilePath = logDirCDN + gzFileName
    mailContents = mailContents + u"开始下载日志文件：%s<br/>"%(gzFileName)
    rs=1
    attempts=0
    while attempts<20 :
        try:
            if os.path.exists(destFilePath) :
                os.remove(destFilePath)
            cmd = "wget  'http://logdownload.c4hcdn.cn/dangle/%s' -P %s"%(gzFileName,logDirCDN)
            print cmd
            rs=os.system(cmd)
            if rs!=0 or (os.path.exists(destFilePath) ==False) or (os.path.getsize(destFilePath)<1):
                attempts =  attempts + 1
                print 'retry'
                continue
            else :
                cmd = 'tar xzvf %s -C %s' %(destFilePath,logDirCDN)
                os.system(cmd)
                print cmd
                cmd = 'rm -rf %s'%destFilePath
                os.system(cmd)
                print cmd
                localFile=destFilePath[:-4]
                if (os.path.exists(localFile) ==False) or (os.path.getsize(localFile)<1):
                    attempts =  attempts + 1
                    print localFile
                    continue
                size = os.path.getsize(localFile)
                size = size/1024/1024
                mailContents = mailContents + u"重试次数：%s,下载文件%s成功,解压后文件大小为：%sM <br/>"%(attempts,localFile,size)
                break;
        except Exception, e:
            print e
            attempts =  attempts + 1
            continue


'''
帝联cdn日志文件下载,日志必须是.gz结尾并且是gz压缩的，否则可能会出错
@author: helin
@param domain:  cdn域名
@param fileDate:   日期对象
'''
def downloadDnionLogFile(domain,fileDate):
    #u.androidgame-store.com_20140427.log
    global mailContents
    if not DOMAIN_CDN_CARRIER.has_key(domain):
        mailContents = mailContents + u"域名%s不存在，下载日志文件失败<br/>"%(domain)
        return
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    
    if not os.path.exists(logDirCDN):
        os.makedirs(logDirCDN)
    dateStr = datetime.datetime.strftime(fileDate, "%Y%m%d")
    data = {}
    data["date"] = dateStr
    data["domain"] = domain
    data['password'] = carrier["password"]
    data['user'] = carrier["username"]
    url = "http://customer.dnion.com/DCC/logDownLoad.do?" + urllib.urlencode(data)
    print url   
    gzFileName = "%s%s"%(getCDNFilename(domain,fileDate),".gz")
    mailContents = mailContents + u"开始下载日志文件：%s<br/>"%(gzFileName)
    destFilePath = logDirCDN + gzFileName
    attempts=0
    while attempts<20 :
        fp = None
        file1 = None
        try:
            if os.path.exists(destFilePath) :
                os.remove(destFilePath)
            fp = urllib.urlopen(url)
            file1 = open(destFilePath, 'wb')
            file1.write(fp.read())
            file1.close()
            fp.close()
            if (os.path.exists(destFilePath) == False)  or (os.path.getsize(destFilePath) < 1):
                attempts =  attempts + 1
                continue
            #解压gz文件
            os.system('gzip -d -f %s'%destFilePath)
            localFile=destFilePath[:-3]
            if (os.path.exists(localFile) == False) or (os.path.getsize(localFile)<1):
                attempts =  attempts + 1
                continue
            size = os.path.getsize(localFile)
            size = size/1024/1024
            mailContents = mailContents + u"重试次数：%s,下载文件%s成功,解压后文件大小为：%sM <br/>"%(attempts,localFile,size)
            break
        except Exception, e:
            print e
            if fp:
                fp.close()
            if file1:
                file1.close()
            attempts =  attempts + 1
            continue

########################################下载日志功能结束#######################################################

########################################分析日志功能开始#######################################################
'''
分析日志文件,并将数据放入基础数据表
@author: helin
@param domain:  cdn域名
@param fileDate:   日期对象
'''
def analysisLogFile(domain,fileDate):
    global mailContents
    logFile = "%s%s"%(logDirCDN,getCDNFilename(domain,fileDate))
    mailContents = mailContents + u"开始分析日志文件%s<br/>"%(logFile)
    if not DOMAIN_CDN_CARRIER.has_key(domain):
        mailContents = mailContents + u"域名%s不存在，分析日志文件失败!!!<br/>"%(domain)
        return
    if (os.path.exists(logFile) == False) or (os.path.getsize(logFile)<1):
        mailContents = mailContents + u"文件%s不存在，分析失败！！！<br/>"%(logFile)
        return
    
    gameDictLoadSuccess = loadGameIdAndResourceType()
    
    if not gameDictLoadSuccess:
        mailContents = mailContents + u"加载资源失败，分析失败！！！<br/>"
        return
    
    deleteDBDataResult = deleteDBData(domain,fileDate)
    if deleteDBDataResult !=True:
        mailContents = mailContents + u"删除数据库中记录失败，分析失败！！！<br/>"
        return
    
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    pattern = carrier["pattern"]
    removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60)#24小时内同一个ip同一个UA下载同一个游戏的多次下载，只计为一次下载
    tempDataList = []
    f = open(logFile, 'rb')
    allCount = 0
    filterCount = 0
    while True:
        line=f.readline()
        if not line: 
            break
        line=line.strip()
        m=pattern.match(line)
        if not m:
            continue
        status=m.group('STATUS')
        if status not in ['200','206']: 
            continue
        ip=""+m.group('IP')
        recordTime=m.group('TIME')
        recordTime=getRecordTime(recordTime)
        gid=m.group('GID')
        flag=m.group('CHANNEL_FLAG')
        source = '';
        if(m.groupdict().has_key('SOURCE')):
           source = m.group('SOURCE')
        ua=m.group('UA')
        fileName=m.group('FILE_NAME')
        tag = ""
        if not fileName:
            print line
            continue
        if domain[:-3] in ["res5.d.cn","res8.d.cn"]:
            game_id = 0 #网游不记录id
            resourceType = 5
            if flag and CHAN_FLAG_DICT.has_key(flag):
                channel = CHAN_FLAG_DICT[flag]
            elif source.find("android.d.cn", 0) > 0:
                channel = 10
            elif ua.find("Digua/", 0) > 0:
                ua=ua[0:ua.find("Digua/", 0)]#ua中，包含了cdn下载相关的调试信息
                channel = 30
            else:
                continue
            allCount = allCount +1
            if not removeUtil.isValidByTime( fileName+ip+ua, recordTime):
                filterCount = filterCount +1
                continue
        else:
            game = m.group('GAME') #game/game1/emulatorgame
            if game == 'game1':
                game_id=int(gid)^110111
            else :
                game_id=int(gid)
            if game_id == 374 and domain.find("g.androidgame-store.com") > -1 :#地瓜升级接口
                continue
            if ua.find("Digua/", 0) > 0:
                ua=ua[0:ua.find("Digua/", 0)]#ua中，包含了cdn下载相关的调试信息
            else :
                ua="-"
            resourceType = GAME_ID_RESOURCETYPE_DICT.get(game_id)
            if game == 'emulatorgame':
                game_id=0
                tag = "emulatorgame"
                resourceType = 1
            if not resourceType:
                resourceType = 1
                tag = "unknown resourceType"
                continue
            channel = 0
            if flag and CHAN_FLAG_DICT.has_key(flag):
                channel = CHAN_FLAG_DICT[flag]
            elif flag and not CHAN_FLAG_DICT.has_key(flag):
                print "unknown channel flag:%s"%line
            if channel == 0:
                if domain.find("g.androidgame-store.com") > -1 :
                    if line.find(".apk?", 0) > 0 or line.find(".dpk?", 0) > 0:
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
                elif "g5.androidgame-store.com" == domain :
                    channel = 30 #默认是地瓜
            allCount = allCount +1
            if not removeUtil.isValidByTime( fileName+ip+ua, recordTime):
                filterCount = filterCount +1
                continue
        if robot_count_dict.has_key(ip):
            robot_count_dict[ip] = robot_count_dict[ip] + 1
            #如果同一个ip，下载了3个以上的包，才记录
            if robot_count_dict[ip] > 3:
                if robot_detail_dict.has_key(ip):
                    robot_detail_dict[ip].append(line)
                else:
                    detailArr= []
                    detailArr.append(line)
                    robot_detail_dict[ip] = detailArr
        else:
            robot_count_dict[ip] = 1
            
        #GAME_ID,PKG_ID,CHANNEL_FLAG,RESOURCE_TYPE,CREATED_DATE,IP,DOMAIN
        tempDataList.append((game_id, 0, channel, resourceType,recordTime, ip, domain,tag))
        if len(tempDataList) >= 1000:
            insertDataToLog(domain, tempDataList)
            tempDataList = []
    print "valid line count: %s,filtered line count: %s"%(allCount,filterCount)
    if tempDataList and len(tempDataList) > 0:
        insertDataToLog(domain, tempDataList)
        tempDataList = []
    f.close()

'''
删除该域名下该天的所有数据
@author: helin
'''
def deleteDBData(domain,fileDate):
    dateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    nextDateStr = datetime.datetime.strftime(fileDate + datetime.timedelta(days=1), '%Y-%m-%d')
    sql="delete from ANDROID_GAME_DOWNLOAD_LOG where domain = %s and CREATED_DATE >= %s and CREATED_DATE < %s"
    result = download_stat_168.delete(sql, (domain,dateStr, nextDateStr))
    return result

#加载游戏/软件id和resourcetype的对应关系
def loadGameIdAndResourceType(): 
    sql = 'select ID, RESOURCE_TYPE from GAME'
    rows = droid_game.queryList(sql)
    if not rows: 
        return False
    for row in rows:
        GAME_ID_RESOURCETYPE_DICT[int(row[0])] = int(row[1])
    return True

#加载网游包id和专区id的对应关系
'''
def loadNetgamePkgidAndChannelid(): # 获取资源类型
    sql = 'select g.id,c.id  from NETGAME_GAME g,NETGAME_CHANNEL c where g.CHANNEL_ID=c.id'
    rows = droid_game.queryList(sql)
    if not rows: 
        return False
    for row in rows:
        NETGAME_PKGID_CHANNELID_DICT[int(row[0])] = int(row[1])
    return True
'''

def getRecordTime(recordTimeStr):
    if(recordTimeStr.find('T')>-1):
         tempTime=datetime.datetime.strptime(recordTimeStr, '%Y-%m-%dT%H:%M:%S.%f+08:00')
         return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')
    tempTime=datetime.datetime.strptime(recordTimeStr, '%d/%b/%Y:%H:%M:%S')
    return datetime.datetime.strftime(tempTime, '%Y-%m-%d %H:%M:%S')
    
def insertDataToLog(domain, dataList): 
    sql="insert into    ANDROID_GAME_DOWNLOAD_LOG (GAME_ID,PKG_ID,CHANNEL_FLAG,RESOURCE_TYPE,CREATED_DATE,IP,DOMAIN,TAG) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        download_stat_168.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                download_stat_168.insert(sql, data)
            except:
                print data
########################################分析日志功能结束#######################################################


########################################分析下载量排行前十的记录开始#######################################################
'''
分析下载量最高的ip前10位
@param fileDate: 日期对象
'''
def analysisRobot(fileDate):
    dateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    file=reportFile%dateStr
    fs = open(file, 'wb')
    try:
        sorted_count_list= sorted(robot_count_dict.iteritems(), key=lambda d:d[1], reverse = True)
        count=0
        sendCountInfo = ""
        sendDetailInfo = ""
        for item in sorted_count_list:
            count = count + 1
            ip = item[0]
            downs = item[1]
            if count > 10 :
                break
            sendCountInfo = sendCountInfo + "ip:%s : 下载量：%s  \r\n<br/>"%(ip,downs)
            detailArr = robot_detail_dict.get(ip)
            if detailArr:
                for item in detailArr:
                    fs.write("%s \n"%item)
        fs.close()
        cmd = "tar -zcf %s.tar %s"%(file,file)
        os.system(cmd)
        sendRobotMail(dateStr,sendCountInfo)
    finally:
        if fs:
            fs.close()
########################################分析下载量排行前十的记录结束#######################################################
#发送邮件
def sendRobotMail(dateStr,sendCountInfo):
    body = "安卓下载量按ip排行前10位:<br>%s<br>详情见附件"%sendCountInfo
    file="%s.tar"%(reportFile%dateStr)
    mailFromName=u"安卓业务报表".encode("gbk")
    mailSubject = (u"安卓下载量按ip排行前10位-%s"%dateStr).encode("gbk")
    mail=MailUtil(file, mailServer, mailFromName, mailFromAddr, reportReceivers, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailAttachment(body)




def sendMail(fileDate):
    global mailContents
    fileDateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    mailContents = (mailContents + u'<br/>执行日期：%s<br/>统计日期：%s<br/>错误信息：%s<br/>谢谢！' % (datetime.datetime.today(), fileDateStr, ERROR_MSG)).encode("gbk")
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

'''
统计某个域名某天的下载量
@param downloadFile: 是否要下载文件
@param domain: 下载域名
@param fileDate: 日期对象
'''
def stat(downloadFile,domain,fileDate):
    global info
    if downloadFile == True:
        downloadLogFile(domain,fileDate)
    analysisLogFile(domain,fileDate)
    
    
    
    
    
###############################################################
'''
下载cdn日志并分析（将下载量基础数据添加到数据库中）
@author: helin
@param --FILE_DATE: 统计日期，如果不传该参数，网宿默认统计前天的数据，帝联默认统计昨天的数据
@param --domain: 下载域名，如果传了明确的域名，则只统计该域名的数据，否则统计安卓业务所有cdn下载域名的数据（包括网游res5.d.cn）
@param --downloadFile: 是否要下载文件，参数值为“no”表示文件已下载到指定位置并解压，不需要重新下载；参数值不传或为其他任何值，都要下载日志文件
'''
if __name__ == '__main__':
    print "android_download_log_analysis.py=============start %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
    mailContents = mailContents + u"安卓下载量统计情况：<br/>"
    
    try:
        #今天
        today = datetime.datetime.today()
        #昨天
        yesterday = today - datetime.timedelta(days = 1)
        #前天
        day_before_yesterday = today - datetime.timedelta(days = 2)
        
        manualFileDate = None #手动传入的时间
        manualDomain = None #手动传入的域名
        downloadFile = True #是否要下载文件
        opts = OptsUtil.getOpts(sys.argv)
        if opts and opts.get('--FILE_DATE'): 
            manualFileDate = opts.get('--FILE_DATE')
        if opts and opts.get('--domain'): 
            manualDomain = opts.get('--domain')
        if opts and "no" == opts.get('--downloadFile'): 
            downloadFile = False
        
        if manualFileDate:#如果传入了明确的日期，则统计该天的数据
            fileDate = datetime.datetime.strptime(manualFileDate, '%Y-%m-%d')
        else:
            fileDate = day_before_yesterday # 默认统计前天的数据
            
        print "stat date : %s"%(datetime.datetime.strftime(fileDate, "%Y-%m-%d"))
        
        if manualDomain :#如果传入了明确的下载域名，则统计该域名的数据
            if DOMAIN_CDN_CARRIER.has_key(manualDomain):
                stat(downloadFile,manualDomain,fileDate)
            else:
                print "domain not exist:%s"%(manualDomain)
        else:
            stat(downloadFile,"g.androidgame-store.com.cn",fileDate)
            stat(downloadFile,"g3.androidgame-store.com.cn",fileDate)
            # stat(downloadFile,"g.androidgame-store.com.hk",fileDate)
            # stat(downloadFile,"g.androidgame-store.com.ov",fileDate)
            stat(downloadFile,"g2.androidgame-store.com",fileDate)
            stat(downloadFile,"res5.d.cn.cn",fileDate)
            # stat(downloadFile,"res5.d.cn.hk",fileDate)
            # stat(downloadFile,"res5.d.cn.ov",fileDate)
            stat(downloadFile,"res8.d.cn.cn",fileDate)
            # stat(downloadFile,"res8.d.cn.hk",fileDate)
            # stat(downloadFile,"res8.d.cn.ov",fileDate)
            stat(downloadFile,"down.androidgame-store.com",fileDate)
            stat(downloadFile,"u.androidgame-store.com",fileDate)
            stat(downloadFile,"p.androidgame-store.com",fileDate)
            stat(downloadFile,"qr.androidgame-store.com",fileDate)
            stat(downloadFile,"res3.d.cn",fileDate)
            stat(downloadFile,"g5.androidgame-store.com",fileDate)
            
            analysisRobot(fileDate)
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: 
            download_stat_168.close()
        if droid_game:
            droid_game.close()
        if ERROR_MSG:
            print ERROR_MSG
            sendMail(fileDate)
    print "android_download_log_analysis.py=============end   %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
