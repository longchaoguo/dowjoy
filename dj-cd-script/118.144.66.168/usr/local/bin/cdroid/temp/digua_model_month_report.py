#!/usr/bin/python
# -*-#coding: cp936
'''和dust的djguastat.py配合使用'''

import sys
import os
import datetime
from djutil.FtpUtil import FtpUtil
import calendar
import string
import re
from djutil.DBUtil import DBUtil

reload(sys)
sys.setdefaultencoding("utf8")

username = "ftpdownjoy"
password = "djftp119"
FILE_PATH = [
['client_350/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.155/client_350/', '155'],
['client/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.155/client/', '155'],
['client_350/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.135/client_350/', '135'],
['client/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.135/client/', '135'],
['client_350/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.167/client_350/', '167'],
['client/', 'android.client.stat.%s.txt', '/opt/logs/211.147.5.167/client/', '167'],

# ['client_350/', '155_client_350_121126-121202.tar.gz', '/home/downjoy/stat/ftp/155/client_350/', '155'],
# ['client/', '155_client_121126-121202.tar.gz', '/home/downjoy/stat/ftp/155/client/', '155'],
# ['client_350/', '135_client_350_121126-121202.tar.gz', '/home/downjoy/stat/ftp/135/client_350/', '135'],
# ['client/', '135_client_121126-121202.tar.gz', '/home/downjoy/stat/ftp/135/client/', '135'],

           ]

dbUtilEqp = DBUtil('equipment_10')

userDict = {}
deviceCntDict = {}
channelIdAndUserDict = {}
osCntDict = {}
resolutionCntDict = {}
versionCntDict = {}
meizuCntDict = {}
ID_EQP_DICT = {}  # id -- eqp
EQP_ID_SET_DICT = {}  # eqp/temp/arr--id
EQP_SET_DICT = {}  # eqp/temp/arr -- brandId
EQP_EQP_DICT = {}
EQP_DATA_DICT = {}  # eqp -- cnt
BRAND_DICT = {}  # brandId--name




def init():
    day=sys.argv[1]
    global firstDayStr
    global endDayStr
    firstDayStr=day[:8] + "01"
    dayCount=calendar.monthrange(int(firstDayStr[0:4]),int(firstDayStr[5:7]))[1]
    endDayStr=datetime.datetime.strftime(datetime.datetime.strptime(firstDayStr, '%Y-%m-%d')+datetime.timedelta(days=(dayCount-1)), '%Y-%m-%d')
    print "firstDayStr:"+firstDayStr
    print "endDayStr:"+endDayStr

def getDateList():
    dateList = []
    firstDay = datetime.datetime.strptime(firstDayStr, '%Y-%m-%d')
    endDay = datetime.datetime.strptime(endDayStr, '%Y-%m-%d')
    while firstDay <= endDay:
        tempDayStr = datetime.datetime.strftime(firstDay, '%Y-%m-%d')
        dateList.append(tempDayStr)
        firstDay = firstDay + datetime.timedelta(days = 1)
    print "dateList:%s"%dateList
    return dateList

def ftpFile(day):
    print "get ftp file,day=%s"%day
    for f in FILE_PATH:
        print "ftpFile()+++++++++ %s"%(f[2] + f[1] % day)
        print "f:::%s"%f
        if os.path.exists(f[2] + f[1] % day):continue
        FtpUtil.getFile(f[0], f[1] % day, f[2], f[1] % day, f[3], 21, username, password)



# 分析每天日志，进行用户登录天数累加
def getImeiCount(day):
    for f in FILE_PATH:
        filepath=f[2]+f[1]%day;
        if os.path.exists(filepath):
            print "getImeiCount(),file exist:"+filepath
        else:
            print "getImeiCount(),no    file:"+filepath
            continue;
        file = open(filepath, 'rU')
        for line in file:
            if line == "":
                continue
            array = string.split(line, "|")
            if len(array) < 11:
                continue
            imei = array[0]
            rId = array[2]
            osId = array[3]
            version = array[4]
            device = array[6]
            if not userDict.has_key(imei):
                userDict[imei] = 1

                if device == 'meizu_m9':
                    meizuCntDict[imei] = line

                if deviceCntDict.has_key(device):
                    deviceCntDict[device] += 1
                else:
                    deviceCntDict[device] = 1

                if osCntDict.has_key(osId):
                    osCntDict[osId] += 1
                else:
                    osCntDict[osId] = 1

                if resolutionCntDict.has_key(rId):
                    resolutionCntDict[rId] += 1
                else:
                    resolutionCntDict[rId] = 1

                if versionCntDict.has_key(version):
                    versionCntDict[version] += 1
                else:
                    versionCntDict[version] = 1
        file.close()

def analysisClientLog():
    print "analysisClientLog() start"
    fileNamePre = firstDayStr[:7]
    for day in dateList:
        getImeiCount(day)

    saveFile = open("%s_device.csv" % (fileNamePre), "w")
    for deviceName in deviceCntDict.keys():
        saveFile.write(deviceName)
        saveFile.write(",")
        saveFile.write(str(deviceCntDict[deviceName]))
        saveFile.write("\n")
    saveFile.flush()
    saveFile.close()

    saveFile = open("%s_os.csv" % (fileNamePre), "w")
    for osId in osCntDict.keys():
        saveFile.write(osId)
        saveFile.write(",")
        saveFile.write(str(osCntDict[osId]))
        saveFile.write("\n")
    saveFile.flush()
    saveFile.close()

    saveFile = open("%s_resolution.csv" % (fileNamePre), "w")
    for rId in resolutionCntDict.keys():
        saveFile.write(rId)
        saveFile.write(",")
        saveFile.write(str(resolutionCntDict[rId]))
        saveFile.write("\n")
    saveFile.flush()
    saveFile.close()

    saveFile = open("%s_version.csv" % (fileNamePre), "w")
    for versionName in versionCntDict.keys():
        saveFile.write(versionName)
        saveFile.write(",")
        saveFile.write(str(versionCntDict[versionName]))
        saveFile.write("\n")
    saveFile.flush()
    saveFile.close()

    saveFile = open("%s_m9.csv" % (fileNamePre), "w")
    for imei in meizuCntDict.keys():
        saveFile.write(meizuCntDict[imei])
        saveFile.write("\n")
    saveFile.flush()
    saveFile.close()
    print "analysisClientLog() end"

def getEQPData():
    sql = "select ID,NAME,ALIAS_NAME,BRAND_ID from EQP where STATUS=1"
    rows = dbUtilEqp.queryList(sql, ())
    for row in rows:
        eqp = row[1].upper().encode('utf8')
        eqp = eqp.replace('_', ' ').replace('-', ' ')
        ID_EQP_DICT[int(row[0])] = eqp
        EQP_SET_DICT[eqp] = int(row[3])
        EQP_EQP_DICT[eqp] = row[1].encode('utf8')
        EQP_ID_SET_DICT[eqp] = int(row[0])
        if row[2]:
            temp = row[2].upper().encode('utf8')
            temp = temp.replace('_', ' ').replace('-', ' ')
            if temp.find('#') == -1:
                EQP_SET_DICT[temp] = int(row[3])
                EQP_ID_SET_DICT[temp] = int(row[0])
            else:
                arrs = temp.split('#')
                for arr in arrs:
                    arr = arr.upper().encode('utf8')
                    arr = arr.replace('_', ' ').replace('-', ' ')
                    EQP_SET_DICT[arr] = int(row[3])
                    EQP_ID_SET_DICT[arr] = int(row[0])
    sql2 = "select ID, NAME from BRAND"
    rows2 = dbUtilEqp.queryList(sql2, ())
    for row in rows2:
        BRAND_DICT[int(row[0])] = row[1].encode('utf8')

def readEQPFile():
    fileNamePre = firstDayStr[:7]
    f = open("%s_device.csv" % (fileNamePre), 'rb')
    while True:
        line = f.readline()
        if not line: break
        line = line.strip()
        arrs = line.split(',')
        item = arrs[0].upper()
        try:
            cnt = int(arrs[1])
        except: continue
        (rsId, rs) = isFind(item)
        if not rs:continue
        key = ID_EQP_DICT.get(rsId)
        EQP_DATA_DICT[key] = EQP_DATA_DICT.get(key, 0) + cnt
    f.close()

def isFind(item):
    rs = False
    eqpSet = set(EQP_ID_SET_DICT.keys())
    rsId = None
    for eqp in eqpSet:
        index = item.find(eqp)
        indexE = index + len(eqp)
        indexF = index - 1
        if index == -1: continue
        isOk = False
        try:
            if indexF == -1 or item[indexF] in [' ', '_', '-']:
                isOk = True
        except: isOk = True
        if not isOk: continue
        try:
            if item[indexE] in [' ', '_', '-']:
                rs = True
        except: rs = True
        if not rs: continue
        rsId = EQP_ID_SET_DICT.get(eqp)
        if item.find('I910') != -1 and len(item) == 4 and eqp == 'I910':
            print index, indexE, indexF, rsId, ID_EQP_DICT.get(rsId), rs
        break
    return (rsId, rs)

def saveResultData():
    rsList = sorted(EQP_DATA_DICT.items(), lambda x, y: cmp(x[1], y[1]), reverse = True)
    f = open('eqp_save.log', 'wb')
    for (eqp, cnt) in rsList:
        brandId = EQP_SET_DICT.get(eqp)
        tempStr = BRAND_DICT.get(brandId, '')
        oldEqp = EQP_EQP_DICT.get(eqp, eqp)
        f.write(oldEqp + '|' + tempStr + '|' + str(cnt) + '\n')
    f.close()

if __name__ == '__main__':
    #########初始化################
    init()
    ###############从135、155、167取下client指定月的日志##########
    dateList = getDateList()
    #for day in dateList:
    #    ftpFile(day)
    #############分析client日志，生成机型等文件##########
    analysisClientLog()
    ###################从机型文件中，统计出用户机型排行################
    getEQPData()
    readEQPFile()
    saveResultData()
    if dbUtilEqp:
        dbUtilEqp.close()
    
