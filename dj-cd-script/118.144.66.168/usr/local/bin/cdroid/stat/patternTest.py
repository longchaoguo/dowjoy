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

def analysisLogFile():
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
        source=m.group('SOURCE')
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