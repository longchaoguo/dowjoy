#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.11 $"
__date__ = "$Date: 2012/10/30 05:34:38 $"

import re
import os
import sys
import time
import datetime
import StringIO
import traceback
import urllib
from djutil.DBUtil import DBUtil
from djutil.FtpUtil import FtpUtil
from djutil.RemoveRepeatUtil import RemoveRepeatUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil

yesterdayStr = None#datetime.datetime.strftime(yesterday, "%Y-%m-%d")
yesterdayStamp = None#datetime.datetime.strftime(yesterday, '%y%m%d')
yesterdayStampCDN = None

domain = "res3.d.cn"
domain_tencent = "tx.androidgame-store.com"
domain_360 = "360w.androidgame-store.com"
domain_360_2 = "360.androidgame-store.com"
domain_baidu = "u.androidgame-store.com"
domain_tencent_2 = "txw.androidgame-store.com"
logDir = '/opt/logs/addownlog/'
logDirCDN = '/opt/logs/addownlog/cdn/'
fileNameCDN = domain + '_%s.gz'
fileNameCDN_tencent = domain_tencent + '_%s.gz'
fileNameCDN_360 = domain_360 + '_%s.gz'
fileNameCDN_360_2 = domain_360_2 + '_%s.gz'
fileNameCDN_baidu = domain_baidu + '_%s.gz'
fileNameCDN_tencent_2 = domain_tencent_2 + '_%s.gz'

cooperation_360 = '360_1'
setup_360 = '360_2'
juhe_360 = '360_3'
wdj = 'wandoujia_1'
setup_wdj = 'wandoujia_2'
baidu = 'baidu_1'
tengxun_soso = 'tencent_1'
tengxun_setup = 'tencent_2'
tengxun_channel = 'tencent_3'
duote_1 = 'duote_1'
cooperation_360_adv = '360_1_1'
setup_360_adv = '360_2_1'
juhe_360_adv = '360_3_1'
wdj_adv = 'wandoujia_1_1'
setup_wdj_adv = 'wandoujia_2_1'
baidu_adv = 'baidu_1_1'
tengxun_soso_adv = 'tencent_1_1'
tengxun_setup_adv = 'tencent_2_1'
tengxun_channel_adv = 'tencent_3_1'
duote_1_adv = 'duote_1_1'

#以下分别问360合作、360一键安装的正则表达式
pattern1 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://360w.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
pattern2 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://360.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
#百度- 正则表达式
pattern3 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://u.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
#腾讯 正则表达式 
pattern4 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://tx.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
pattern5 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://txw.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
#有版权
pattern6 = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://res3.d.cn\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
#多特-正则表达式
pattern7 = re.compile("(?P<TIME>\S+ \S+) \S+ \/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*) f=(?P<PARAM>[^&=\?\s]*)\S* (?P<IP>\S*) (?P<STATUS>\d+)")
#迅雷-正则表达式 141
pattern8 = re.compile("(?P<TIME>\S+ \S+) \S+ \S* \S* \/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*) \S* \S* \S* (?P<IP>\S*) .* (?P<STATUS>\d+) \d* \d*")
CHAN_FLAG_DICT = {
                cooperation_360: 40,
                cooperation_360_adv: 41,
                setup_360: 50,
                setup_360_adv: 51,
                baidu: 80,
                baidu_adv: 81,
                tengxun_soso: 90,
                tengxun_soso_adv: 91,
                tengxun_setup: 100,
                tengxun_setup_adv: 101,
                tengxun_channel: 110,
                tengxun_channel_adv: 111,
                duote_1: 120,
                duote_1_adv: 121,
                juhe_360: 130,
                juhe_360_adv: 131
                }

ID_DICT = {}
username = 'wenxin' # FTP用户名
password = 'ftp@wenxin13' # FTP密码
#dbUtil=DBUtil('download_stat_111')
dbUtil_10 = DBUtil('droid_game_10')
dbUtil_168 = DBUtil('download_stat_168')

FTP_FILE = [
          ['duote.androidgame-store.com/W3SVC570444579/', 'ex%s.log', logDir + '119.184.120.42/duote.androidgame-store.com/W3SVC570444579/', 'ex%s.log', '119.164.255.244', '21', pattern7, None],
          #['thunder.androidgame-store.com/W3SVC688993420/', 'ex%s.rar', logDir + '119.184.120.43/thunder.androidgame-store.com/W3SVC688993420/', 'ex%s.rar', '119.164.255.245', '21', pattern8, 140],
          ]

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"安卓合作方下载量统计错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
###########################################################
def init():
    global yesterdayStr, yesterdayStamp, yesterdayStampCDN
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'): #raise Exception, 'can not find the datetime params!'
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), "%Y-%m-%d")
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    yesterdayStr = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
    yesterdayStamp = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%y%m%d")
    yesterdayStampCDN = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), '%Y%m%d')

def initIdDictForResId(): # 获取资源类型
    sql = 'select g.ID, gc.RESOURCE_TYPE from GAME g inner join GAME_CATEGORY gc on gc.ID=g.GAME_CATEGORY_ID '
    rows = dbUtil_10.queryList(sql, ())
    if not rows: return
    for row in rows:
        ID_DICT[int(row[0])] = int(row[1])

#分析日志并进行统计
def statFile(fileName, pattern , chanFlag, removeUtil1, removeUtil2):
    if not os.path.exists(fileName):
        raise Exception, "can't find the file: %s" % (fileName)
    f = open(fileName, 'rb')
    tempDataList = []
    while True:
        chanFlagValue = chanFlag
        line = f.readline()
        if not line:
            break
        line = line.strip()
        m = pattern.match(line)
        if not m:
            continue
        status = m.group('STATUS')
        if not status in ['200', '206']:
            continue
        game = m.group('GAME')
        if game not in ['game', 'game1']:
            continue
        ip = m.group('IP')
        recordTime = m.group('TIME')
        try:
            gameId = int(m.group('RID'))
            if game == 'game1':
                gameId = gameId ^ 110111
        except:
            continue
        resType = ID_DICT.get(gameId, 0) # 获取资源类别
        if not chanFlag or chanFlag == 'None':
            try:
                param = (m.group('PARAM')).strip()
                pkgStr = m.group('PKG')
                if pkgStr.find('adv__') != -1 or pkgStr.find('dcn__') != -1: #广告包自定义参数
                    param = param + '_1'
                if not CHAN_FLAG_DICT.has_key(param):
                    continue
                chanFlagValue = CHAN_FLAG_DICT.get(param)
            except:
                continue
        if not chanFlagValue:
            continue
        if chanFlagValue in [41, 51, 81, 91, 101, 111, 121, 131]:
            if status != '200':continue
            if not removeUtil2.isValidByTime(str(gameId) + '_' + ip, recordTime): continue
        else:
            if status == '206' and not removeUtil1.isValidByTime(str(gameId) + '_' + ip, recordTime): continue
        #服务器记载时间不准确，故不取日志记录时间进行插入
        tempDataList.append((gameId, 0, chanFlagValue, resType, ip, yesterdayStr))
        if len(tempDataList) >= 1000:
            insertDataToLog(dbUtil_168, tempDataList)
            tempDataList = []
    if tempDataList:
        insertDataToLog(dbUtil_168, tempDataList)
        tempDataList = []
    f.close()

def changeVarible(i, length):
    if i + 1 >= length: return 0
    else: return i + 1

def insertDataToLog(dbUtil, dataList): # 将数据插入ANDROID_GAME_DOWNLOAD_LOG表！
    sql = 'insert into ANDROID_GAME_DOWNLOAD_LOG(GAME_ID, PKG_ID, CHANNEL_FLAG, RESOURCE_TYPE, IP, CREATED_DATE) values(%s, %s, %s, %s, %s, %s)'
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                print data

def deleteDBData():
    nextDate = datetime.datetime.strftime(datetime.datetime.strptime(yesterdayStr, '%Y-%m-%d') + datetime.timedelta(days = 1), '%Y-%m-%d')
    sql1 = "delete from ANDROID_GAME_DOWNLOAD_LOG where CHANNEL_FLAG in (40,41,50,51,80,81,90,91,100,101,110,111,120,121,130,131,140) and CREATED_DATE >= %s and CREATED_DATE < %s"
    dbUtil_168.delete(sql1, (yesterdayStr, nextDate))

def handleCDNLog(domain, gzFile, pattern, user, passwd): #cdn日志统计
    getCDNFile(domain, gzFile, user, passwd)
    os.system("gzip -d %s" % (gzFile))
    removeUtil = RemoveRepeatUtil(logTimeFormat = '%d/%b/%Y:%H:%M:%S')
    removeUtil2 = RemoveRepeatUtil(logTimeFormat = '%d/%b/%Y:%H:%M:%S')
    statFile(gzFile[:gzFile.find('.gz')], pattern , None, removeUtil, removeUtil2)

#有版权下载移至CDN，日志
def getCDNFile(domain, gzFile, user, passwd):
    data = {}
    data['user'] = user
    data['password'] = passwd
    data['date'] = yesterdayStampCDN
    data['domain'] = domain
    url = "http://runreport.dnion.com/DCC/logDownLoad.do?" + urllib.urlencode(data)
    print url
    rs = urllib.urlopen(url)
    f = open(gzFile, 'wb')
    f.write(rs.read())
    f.close()
    rs.close()

def getFtpFile(value, datetimeStr):
    index = 0
    while True:
        index = index + 1
        isSucc = FtpUtil.getFileContinue(value[0], value[1] % datetimeStr, value[2], value[3] % datetimeStr, value[4], value[5], username, password)
            #getFile(value[0], value[1], value[2], value[3], value[4], value[5])
        if isSucc or index > 10: break

def statFtpFile():
    for value in FTP_FILE:
        print value[1]
        if not value: continue
        getFtpFile(value, yesterdayStamp)
        if value[3].find('.rar') != -1:
            os.system("unrar x %s %s" % (value[2] + value[3] % yesterdayStamp, value[2]))
            value[3] = value[3].replace('.rar', '.log')
        removeUtil = RemoveRepeatUtil()
        removeUtil2 = RemoveRepeatUtil()
        statFile(value[2] + value[3] % yesterdayStamp, value[6], value[7], removeUtil, removeUtil2)

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), yesterdayStr, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
###############################################################
if __name__ == '__main__':
    print "=============start %s" % datetime.datetime.now()
    try:
        init()
        #清理数据库数据
        deleteDBData()
        print 'clear data over~!'
        initIdDictForResId()
        #统计360合作、360一键安装、腾讯日志（下载-->统计）
        #handleCDNLog(domain, logDirCDN + fileNameCDN % yesterdayStampCDN, pattern6, 'res5push', 'Res5!@#123') # 有版权CDN统计
        handleCDNLog(domain_tencent, logDirCDN + fileNameCDN_tencent % yesterdayStampCDN, pattern4, 'cdnpush', 'cdn123!@#push') # 腾讯CDN统计       
        handleCDNLog(domain_360, logDirCDN + fileNameCDN_360 % yesterdayStampCDN, pattern1, 'cdnpush', 'cdn123!@#push')
        handleCDNLog(domain_360_2, logDirCDN + fileNameCDN_360_2 % yesterdayStampCDN, pattern2, 'cdnpush', 'cdn123!@#push')
        #handleCDNLog(domain_baidu, logDirCDN + fileNameCDN_baidu % yesterdayStampCDN, pattern3, 'cdnpush', 'cdn123!@#push')
        handleCDNLog(domain_tencent_2, logDirCDN + fileNameCDN_tencent_2 % yesterdayStampCDN, pattern5, 'cdnpush', 'cdn123!@#push')
        #统计多特等ftp日志数据
        #statFtpFile()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168:
            dbUtil_168.close()
        if dbUtil_10:
            dbUtil_10.close()
        if ERROR_MSG:
            sendMail()
    print "=============end   %s" % datetime.datetime.now()
