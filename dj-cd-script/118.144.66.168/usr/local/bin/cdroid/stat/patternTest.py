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
    mailContents = mailContents + u"��ʼ������־�ļ�%s<br/>"%(logFile)
    if not DOMAIN_CDN_CARRIER.has_key(domain):
        mailContents = mailContents + u"����%s�����ڣ�������־�ļ�ʧ��!!!<br/>"%(domain)
        return
    if (os.path.exists(logFile) == False) or (os.path.getsize(logFile)<1):
        mailContents = mailContents + u"�ļ�%s�����ڣ�����ʧ�ܣ�����<br/>"%(logFile)
        return
    
    gameDictLoadSuccess = loadGameIdAndResourceType()
    
    if not gameDictLoadSuccess:
        mailContents = mailContents + u"������Դʧ�ܣ�����ʧ�ܣ�����<br/>"
        return
    
    deleteDBDataResult = deleteDBData(domain,fileDate)
    if deleteDBDataResult !=True:
        mailContents = mailContents + u"ɾ�����ݿ��м�¼ʧ�ܣ�����ʧ�ܣ�����<br/>"
        return
    
    carrier = DOMAIN_CDN_CARRIER.get(domain)
    pattern = carrier["pattern"]
    removeUtil=RemoveRepeatUtil(clearTimeDiff = 24*60*60, compareTimeDiff = 24*60*60)#24Сʱ��ͬһ��ipͬһ��UA����ͬһ����Ϸ�Ķ�����أ�ֻ��Ϊһ������
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
            game_id = 0 #���β���¼id
            resourceType = 5
            if flag and CHAN_FLAG_DICT.has_key(flag):
                channel = CHAN_FLAG_DICT[flag]
            elif source.find("android.d.cn", 0) > 0:
                channel = 10
            elif ua.find("Digua/", 0) > 0:
                ua=ua[0:ua.find("Digua/", 0)]#ua�У�������cdn������صĵ�����Ϣ
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
            if game_id == 374 and domain.find("g.androidgame-store.com") > -1 :#�ع������ӿ�
                continue
            if ua.find("Digua/", 0) > 0:
                ua=ua[0:ua.find("Digua/", 0)]#ua�У�������cdn������صĵ�����Ϣ
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
                        channel = 30 #Ĭ���ǵع�
                elif "down.androidgame-store.com" == domain :
                    channel = 10 #Ĭ����android.d.cn��վ
                elif "u.androidgame-store.com" == domain :
                    channel = 80 #Ĭ���ǰٶ�
                elif "p.androidgame-store.com" == domain :
                    channel = 20 #Ĭ����a.d.cn��վ
                elif "qr.androidgame-store.com" == domain :
                    channel = 10 #Ĭ����android.d.cn��վ
                elif "res3.d.cn" == domain :
                    channel = 30 #Ĭ���ǵع�
                elif "g5.androidgame-store.com" == domain :
                    channel = 30 #Ĭ���ǵع�
            allCount = allCount +1
            if not removeUtil.isValidByTime( fileName+ip+ua, recordTime):
                filterCount = filterCount +1
                continue
        if robot_count_dict.has_key(ip):
            robot_count_dict[ip] = robot_count_dict[ip] + 1
            #���ͬһ��ip��������3�����ϵİ����ż�¼
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