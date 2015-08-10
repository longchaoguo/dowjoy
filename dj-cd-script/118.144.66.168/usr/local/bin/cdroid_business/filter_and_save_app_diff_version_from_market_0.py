#!/usr/bin/env python
#-*- encoding: utf8 -*-
# author : Jonathan Lai(xingbing.lai@downjoy.com)
# version: 1.1.0
# Date   : 2013/05/07 09:30:00
# 功能   : 定期在Google Play抓取游戏软件最新版本信息

import time
import urllib2
import re
import os
import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def closeConn(conn):
    conn.close()

def getRs(conn, sql):
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.commit()
        return rows
    except MySQLdb.Error, er:
        print er
        pass
    except:
        pass
    finally:
        try:
            cursor.close()
        except:
            pass


def execSql(conn, sql):
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql.decode("gb2312"))
        conn.commit()
    except MySQLdb.Error, er:
        print er
        pass
    except:
        pass
    finally:
        try:
            cursor.close()
        except:
            pass


def execSqlWithParams(conn, sql, params):
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql.decode("gb2312"), params)
        conn.commit()
    except MySQLdb.Error, er:
        print er
        pass
    except:
        pass
    finally:
        try:
            cursor.close()
        except:
            pass


def getDroidConnection():
    try:
        conn = MySQLdb.connect(host='192.168.0.35', user='moster', passwd='shzygjrmdwg', db='droid_game',
                               charset='utf8')
        return conn
    except:
        print 'Connection mysql error!!'


def getDoc(url):
    try:
        html = urllib2.urlopen(url, timeout=6).read()
        return html
    except urllib2.HTTPError, e:
        print "获取应用失败：[Code:%s]" % e.code
        print url
        return None
    except urllib2.URLError, e:
        print "获取应用失败：[Code:%s]" % e.reason
        print url
        return None
    except Exception, e:
        print e
        return None

def getVersion(doc):
    reg = r'<div class="content" itemprop="softwareVersion">(.+?)</div>'
    match = re.search(reg, doc)
    if match:
        return match.group(1)
    return None


def getUpdatedate(doc):
    reg = r'<div class="content" itemprop="datePublished">(.+?)</div>'
    match = re.search(reg, doc)
    if match:
        return match.group(1)
    return None


def getPrice(doc):
    reg = r'<meta content="￥(.+?)" itemprop="price">'
    match = re.search(reg, doc)
    if match:
        return match.group(1)
    return None


def main():
    droidConn = getDroidConnection()
    url_prefix = 'https://play.google.com/store/apps/details?hl=zh_CN&id='
    dateDiff= getRs(droidConn, '''select datediff(now(), min(CREATED_DATE)) from APP_DIFF_VERSION_FROM_MARKET''')

    if dateDiff[0][0] > 0:
        execSql(droidConn, 'truncate APP_DIFF_VERSION_FROM_MARKET')
    print "------1"
    markedApps = getRs(droidConn, '''select PKG_NAME from MARKED_APP_DIFF_VERSION_FROM_MARKET''')
    markedMap = {}
    print "------2-->> Marked cnt: "+str(len(markedApps))
    if markedApps:
        for app in markedApps:
            markedMap[app[0]] = app
    
    sql = '''SELECT GP.GAME_ID, GP.PACKAGE_NAME, GP.VERSION_NAME, G.NAME, G.EN_NAME, 
             C.RESOURCE_TYPE FROM GAME_PKG GP INNER JOIN GAME G ON G.ID=GP.GAME_ID 
             INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID 
             WHERE GP.STATUS = 1 AND G.STATUS = 1 
             group by G.ID
             order by G.ID desc 
             limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    appRows = []
    while True:
        curSql = sql % (startIdx, pageNum)
        print curSql
        rows = getRs(droidConn, curSql)
        if not rows:
            break
        else:
            appRows.extend(rows)
            startIdx += pageNum
    print "------3-->> Package cnt: "+str(len(appRows))
    
    for app in appRows:
        point = time.time()
        gameId = app[0]
        pkgName = app[1]
        versionName = app[2]
        name = app[3]
        en_name = app[4]
        resourceType = app[5]
        url = url_prefix + pkgName
        try:
            print "------->>start fetch document"
            doc = getDoc(url)
            if doc is None:
                print "安卓市场无此游戏：%s(%s)"%(app[3],app[1])
                continue
            else:
                print "------->>start analysis document"
                version = getVersion(doc)
                updatedate = getUpdatedate(doc)
                price = getPrice(doc)
                if len(en_name) > 0:
                    name = "%s(%s)"%(name, en_name)
                print name,'>>>>', version,'>>>>', updatedate,'>>>>', price
                priceType=1
                if not price:
                    priceType=0
                if version.strip().decode() != versionName:
                    if pkgName in markedMap:
                        execSqlWithParams(droidConn, '''insert into APP_DIFF_VERSION_FROM_MARKET(ID, NAME,
                        PKG_NAME, VERSION, MARKET_VERSION, MARKET_UPDATE_DATE, STATUS, CREATED_DATE,
                        RESOURCE_TYPE, PRICE_TYPE)
                        values(%s, %s, %s, %s, %s, %s, 2, now(), %s, %s)''',
                                          (gameId, name, pkgName, versionName, version, updatedate, resourceType, priceType))
                    else:
                        execSqlWithParams(droidConn, '''insert into APP_DIFF_VERSION_FROM_MARKET(ID, NAME,
                        PKG_NAME, VERSION, MARKET_VERSION, MARKET_UPDATE_DATE, STATUS, CREATED_DATE,
                        RESOURCE_TYPE, PRICE_TYPE)
                        values(%s, %s, %s, %s, %s, %s, 1, now(), %s, %s)''',
                                          (gameId, name, pkgName, versionName, version, updatedate, resourceType, priceType))
                else:
                    print "Same version -->> %s" % pkgName
        except Exception,ex:
            print "[ERROR] GameID: ",gameId, ex
            pass
        print "gameid:%s used %s sec" % (gameId, time.time()-point)
    
    closeConn(droidConn)


class LogUtil():
    """
        日志工具类
        backup：备份日志文件到指定的路径下 ，备份结果为在原有日志名称后添加日期字符串。
        比如：/var/log/market_version.log  >>>  /var/log/log_bak/market_version_20130516131210.log
    """
    def __init__(self, srcLogFile, descLogPath):
        self.srcLogFile = srcLogFile
        self.descLogPath = descLogPath

    def backup(self):
        self.__copyLog()
        self.__delLog()

    def __copyLog(self):
        date = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if not os.path.exists(self.descLogPath):
            os.mkdir(self.descLogPath)
        fi = open(self.srcLogFile)
        name = fi.name
        descFileName = name[name.rfind('/') + 1:name.rfind('.')]
        fo = open(self.descLogPath+'/'+descFileName+'_'+date+'.log', "w+")
        try:
            allText = fi.read()
            fo.write(allText)
        finally:
            fo.close()
            fi.close()

    def __delLog(self):
        fi = open(self.srcLogFile,'w')
        fi.write("")
        fi.close()


if __name__ == "__main__":
    srcLogFile = '/var/log/market_version.log'
    descLogPath = '/var/log'
    log = LogUtil(srcLogFile,descLogPath)
    #log.backup()
    print '>>BEGIN<<'
    start = time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))
    main()
    end = time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end))
    print "#########filter_and_save_app_diff_version_from_market.py over. Used %s" % (end - start)
    print '>>END<<'
