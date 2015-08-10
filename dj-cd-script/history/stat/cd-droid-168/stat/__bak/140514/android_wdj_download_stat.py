#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xin.wen $"
__version__ = "$Revision: 1.8 $"
__date__ = "$Date: 2012/10/31 02:06:30 $"

import re
import os
import sys
import datetime
import urllib
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
from djutil.RemoveRepeatUtil import RemoveRepeatUtil
################################################################
yesterdayStr = None#datetime.datetime.strftime(yesterday, "%Y-%m-%d")

logDir = '/opt/logs/addownlog/'
#logDir='f:/'
#dbUtil=DBUtil('download_stat_111')
dbUtil_10 = DBUtil('droid_game_10')
dbUtil_168 = DBUtil('download_stat_168')
queueCount = 0 # 队列的容量
queueSize = 0 # 队列的个数 
queue = [] # 模拟队列的数组
wdj = 'wandoujia_1'
wdj_adv = 'wandoujia_1_1'
setup_wdj = 'wandoujia_2'
setup_wdj_adv = 'wandoujia_2_1'
CHAN_FLAG_DICT = {
                wdj: '60',
                wdj_adv: '61',
                setup_wdj: '70',
                setup_wdj_adv: '71'
}

ID_DICT = {}
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"安卓豌豆荚下载量统计错误信息".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
################################################################
def init():
    global yesterdayStr
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):# raise Exception, 'can not find the datetime params!'
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 1), '%Y-%m-%d')
    else:
        fileDate = opts.get('--FILE_DATE')
    print fileDate
    yesterdayStr = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")

def initIdDictForResId(): # 获取资源ID
    sql = 'select g.ID, gc.RESOURCE_TYPE from GAME g inner join GAME_CATEGORY gc on gc.ID=g.GAME_CATEGORY_ID '
    rows = dbUtil_10.queryList(sql, ())
    if not rows: return
    for row in rows:
        ID_DICT[int(row[0])] = int(row[1])

#豌豆荚日志下载
def getFileForWDJ(domain, destFilePath):
    if not os.path.exists(destFilePath[:destFilePath.rfind('/') + 1]):
        os.makedirs(destFilePath[:destFilePath.rfind('/') + 1])
    if os.path.exists(destFilePath) :
        os.remove(destFilePath)
    data = {}
    data["domain"] = domain
    data['password'] = 'cdn123!@#push'
    data['user'] = 'cdnpush'
    url = "http://customer.dnion.com/DCC/logDownLoad.do?" + urllib.urlencode(data)
    print url   
    fp = urllib.urlopen(url)
    file1 = open(destFilePath, 'wb')
    file1.write(fp.read())
    file1.close()
    fp.close()

###############################################
#统计豌豆荚下载量统计（按照旧版原则）
def count(path):
    if os.path.isfile(path) == False:
        return
    initQueue(getLineCount(path))
    file = open(path, 'rb')
    tempDataList = []
    removeUtil = RemoveRepeatUtil()
    while True:
        line = file.readline()
        if not line: break
        url = re.compile("((\d+\.\d+\.\d+\.\d+) .* \[(\S*).*\].* http://(t.casualgame-down.com|t2.casualgame-down.com)/android/new/(game|game1)/\d+/(\d+)/([\w\.!]+)\.(zip|apk|rar))[\?]f=([^\?=&\s]*)\S* \S* (\S*) .*")
        gid = 0
        for value in url.findall(line):
            gid = value[5]
            ip = value[1]
            gameParam = value[4]
            pkgStr = value[6]
            param = value[8]
            if pkgStr.find('adv__') != -1 or pkgStr.find('dcn__') != -1:
                param = param + '_1'
            if gameParam == "game1":
                gameId = int(gid) ^ 110111
            else:
                gameId = int(gid)
            resType = ID_DICT.get(gameId, 0)
            chanFlag = CHAN_FLAG_DICT.get(param)
            if not chanFlag: continue
            if chanFlag in ('61', '71'):
                timeRecord = value[2]
                timeRecord = datetime.datetime.strftime(datetime.datetime.strptime(timeRecord, '%d/%b/%Y:%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                status = value[9]
                if status != '200':continue
                if not removeUtil.isValidByTime(str(gameId) + "_" + ip, timeRecord): continue
            else:
                if not isValidData(str(gameId) + "_" + ip): continue
            tempDataList.append((gameId, 0, chanFlag, resType, ip, yesterdayStr))
            if len(tempDataList) >= 1000:
                insertDataToLog(dbUtil_168, tempDataList)
                tempDataList = []
    if tempDataList:
        insertDataToLog(dbUtil_168, tempDataList)
        tempDataList = []
    file.close()

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

def getLineCount(path):
    file = open(path)
    lineCount = 0
    for line in file:
        lineCount = lineCount + 1
    file.close()
    return lineCount

#初始化队列
def initQueue(lineCount):
    global queue
    global queueCount
    global queueSize
    queueSize = lineCount / 288
    queueCount = 0
    queue = []

#验证是否为有效数据（豌豆荚排重）
def isValidData(value):
    global queue
    global queueCount
    global queueSize
    flag = True
    if queueCount > queueSize:
        queue.pop(0)
        queueCount = queueCount - 1
    if any(value in s for s in queue):
        flag = False
    queue.append(value)
    queueCount = queueCount + 1
    return flag

def clearData():
    nextDate = datetime.datetime.strftime(datetime.datetime.strptime(yesterdayStr, '%Y-%m-%d') + datetime.timedelta(days = 1), '%Y-%m-%d')
    sql1 = "delete from ANDROID_GAME_DOWNLOAD_LOG where CREATED_DATE >= %s and CREATED_DATE < %s and CHANNEL_FLAG in (60,61,70,71)"
    dbUtil_168.delete(sql1, (yesterdayStr, nextDate))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢' % (datetime.datetime.today(), yesterdayStr, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
#########################################################
if __name__ == '__main__':
    print "============wdj start %s" % datetime.datetime.now()
    try:
        init()
        INFO_WDJ_DICT = {
                   #'t.androidgame-store.com': [logDir + 'wdj/t.androidgame-store.com_%s.gz' % yesterdayStr],
                   #'t2.androidgame-store.com': [logDir + 'wdj/t2.androidgame-store.com_%s.gz' % yesterdayStr],
                   't.casualgame-down.com': [logDir + 'wdj/t.casualgame-down.com_%s.gz' % yesterdayStr],
                   't2.casualgame-down.com': [logDir + 'wdj/t2.casualgame-down.com_%s.gz' % yesterdayStr]
        }
        ######################################################
        clearData() #清理数据
        print 'clear data over~!'
        initIdDictForResId() #初始化资源ID
        for key, value in INFO_WDJ_DICT.items(): #遍历日志并统计
            index = 0
            while True: #index控制ftp错误，针对每个日志最大容错为5次
                try:
                    if os.path.exists(value[0]):
                        break
                    index = index + 1
                    getFileForWDJ(key, value[0])
                    break
                except Exception, ex:
                    if index > 5:
                        raise ex
            os.system('gzip -d %s' % value[0])
            count(value[0][:-3])
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_168: dbUtil_168.close()
        if dbUtil_10: dbUtil_10.close()
        if ERROR_MSG:
            sendMail()
    print "============wdj end   %s" % datetime.datetime.now()
