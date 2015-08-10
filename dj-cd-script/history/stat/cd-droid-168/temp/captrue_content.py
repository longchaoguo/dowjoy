#!/usr/bin/env python
#-*- encoding: utf8 -*-

import time
import urllib2
import re
import os
import MySQLdb
import socket

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def closeConn(conn):
    conn.close()

def execSql(conn, sql):
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql.decode("utf8"))
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
        conn = MySQLdb.connect(host='192.168.0.35', user='moster', passwd='shzygjrmdwg', db='droid_game', charset='utf8')
        return conn
    except:
        print 'Connection mysql error!!'

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

def getKoreanName(doc):
    reg = r'<div class="document-title" itemprop="name"> <div>(.*?)</div> </div>'
    match = re.search(reg, doc)
    if match:
        return match.group(1)
    return None

def getKoreanDescrption(doc):
    reg = r'<div class="id-app-orig-desc">(.*?)</div>'
    match = re.search(reg, doc)
    if match:
        return match.group(1)
    return None 
 

def getDoc(url):
    try:
        time.sleep(10)
        socket.setdefaulttimeout(50000)
        html = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        print url
        return None    
    return html


def updateLangageType(droidConn, games, updateLanguageTypeSql):
    for game in games:
        print game
        if game[1] != '':
            languageType = game[1] - 1
        if game[0] != '':
            id = game[0]
        execSql(droidConn, updateLanguageTypeSql % (int(languageType), int(id)))
    

def cutHtmlTag(html):
    html = re.sub(r'</?\w+[^>]*>','',html).replace('&quot', '');
    return html;


def main():
    droidConn = getDroidConnection()

    packageNames = getRs(droidConn, "select GP.package_name, GP.id from GAME_PKG GP INNER JOIN GAME G ON GP.GAME_ID = G.ID WHERE RESOURCE_TYPE = 2 and length(G.KO_NAME)=0 order by GP.id");
    games = getRs(droidConn, "SELECT ID, LANGUAGE_TYPE FROM GAME WHERE IS_COOPERATE = 1 AND LANGUAGE_TYPE & 1=1");
    url_prefix = 'https://play.google.com/store/apps/details?id=%s&hl=ko'
    updateSql = "update GAME G INNER JOIN GAME_PKG GP ON G.ID = GP.GAME_ID SET G.KO_NAME = '%s', G.KO_DESCRIPTION = '%s' WHERE GP.PACKAGE_NAME = '%s'";

    
    #update all software  support English 
    updateLanguageTypeSql = "UPDATE GAME G SET G.LANGUAGE_TYPE = %d WHERE G.ID = %d"
    updateLangageType(droidConn, games, updateLanguageTypeSql);
    
#    for packageName in packageNames:
#        url = url_prefix%(packageName[0]);
#        doc = getDoc(url);
#        if not doc is None:
#            koreanName = getKoreanName(doc);
#            koreanDescrption = getKoreanDescrption(doc);
#            koreanDescrption = cutHtmlTag(koreanDescrption);
#            execSql(droidConn, updateSql%(koreanName, koreanDescrption, packageName[0]));
#            #print koreanName;
#            print '=============================GKG_ID:%d'%packageName[1];
#            #print koreanDescrption;
#    
    closeConn(droidConn)
        
        
main();














       
        
        
