#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime as dt
import time
import ftplib
import MySQLdb
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def closeConn(conn):
    conn.close();

def getRs(conn, sql):
    try:
        cursor = conn.cursor();
        cursor.execute(sql);
        rows = cursor.fetchall();
        conn.commit();
        return rows;
    except:
        pass;
    finally:
        try:
            cursor.close();
        except:
            pass;

def execSql(conn, sql):
    try:
        cursor = conn.cursor();
        cursor.execute(sql.decode("gb2312"));
        conn.commit();
    except:
        pass;
        print sql
    finally:
        try:
            cursor.close();
        except:
            pass;

def execSqlWithParams(conn, sql, params):
    try:
        cursor = conn.cursor();
        cursor.execute(sql.decode("gb2312"), params);
        conn.commit();
    except:
        pass;
        print sql%params
    finally:
        try:
            cursor.close();
        except:
            pass;

def getDroidGameConnection():
    try:
        conn = MySQLdb.connect(host='192.168.0.35',user='moster',passwd='shzygjrmdwg',db='droid_game', charset='utf8')
        return conn
    except Exception,e:
        print str(e);

def processpkg(pkg, name):
    if pkgMap.get(pkg):
        pkgMap[pkg]["cnt"] +=1
    else:
        if not pkgMapFromDB.has_key(pkg):
            dict={}
            dict["name"] = name
            dict["cnt"] = 1
            pkgMap[pkg] = dict

def proccessPkgs(pkgs):
    pkgs = pkgs.replace('{', "").replace('}', "").replace(' ', "")
    arr = pkgs.split(",")
    for pkg in arr:
        arr = pkg.split("=")
        if len(arr) >= 2:
            processpkg(arr[0], arr[1])
            

def proccessLine(line):
    arr = line.split("|")
    #imei = arr[0]
    pkgs = arr[1]
    #time = arr[2]
    proccessPkgs(pkgs)

def write(path, line):
    f = open(path, "a")
    f.write(line.encode('utf8') + '\n\r')
    f.close 

def execute(sql, conn):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        cords = cursor.fetchall()
        conn.commit()
        if not cords:
            return None
        return cords
    except Exception,e:
        print str(e)
        pass;

def getDataFromFtp(filename):
    if os.path.exists("data.txt"):
        os.remove("data.txt")
    
    print("open tem file...")
    f=open('data.txt', 'ab')
    print("download log file from 155 by ftp")
    ftp=ftplib.FTP('192.168.0.155')
    ftp.login('ftpdownjoy','djftp119')
    #追加上新版数据接口日志
    try:
        ftp.retrbinary("RETR ./client_350/%s"%filename, f.write)
    except Exception, ex:
        print '155 file not exist: ./client_350/%s'%filename
    ftp.quit()
    
    print("download log file from 176 by ftp")
    ftp=ftplib.FTP('192.168.0.176')
    ftp.login('ftpdownjoy','djftp119')
    #追加上新版数据接口日志
    try:
        ftp.retrbinary("RETR ./client_350/%s"%filename, f.write)
    except Exception, ex:
        print '176 file not exist: ./client_350/%s'%filename
    ftp.quit()
    
    print("download log file from 167 by ftp")
    ftp=ftplib.FTP('192.168.0.167')
    ftp.login('ftpdownjoy','djftp119')
    #追加上新版数据接口日志
    try:
        ftp.retrbinary("RETR ./client_350/%s"%filename, f.write)
    except Exception, ex:
        print '167 file not exist: ./client_350/%s'%filename
    ftp.quit()
    f.close()
    
    f=open('data.txt', 'r')
    lines = f.readlines()
    f.close()
    if os.path.exists("data.txt"):
        os.remove("data.txt")
    return lines


def main():
    start = time.time()
    print("#########start =>")
    droidGameConn = getDroidGameConnection()
    
    lastDate = dt.date.today() - dt.timedelta(days=1)
    fileName="upgrade.info." + str(lastDate) + ".txt"
    lines = getDataFromFtp(fileName)
    #f = open('C:/Users/DwaNdw/Desktop/upgrade.info.2011-12-05.txt', 'r')
    #lines = f.readlines()
    
    print("delete last day's data from APP_NOT_IN_DB_FROM_USER")
    execSql(droidGameConn, 'delete from APP_NOT_IN_DB_FROM_USER')
    
    rs = getRs(droidGameConn, 'select PACKAGE_NAME from GAME_PKG')
    for r in rs:
        pkgMapFromDB[r[0]] = r[0]
    
    rs = getRs(droidGameConn, 'select PKG_NAME from MARKED_APP_NOT_IN_DB_FROM_USER')
    for r in rs:
        markedAppMap[r[0]] = r[0]
    
    lineTmp=""
    for line in lines:
        line = line.replace("\n", "").replace("\r", "")
        if len(lineTmp) < 1:
            arr = line.split("|")
            if len(arr) < 3:
                lineTmp += line
            else:
                proccessLine(line)
        else:
            line = lineTmp + line
            arr = line.split("|")
            if len(arr) < 3:
                lineTmp += line
            else:
                proccessLine(line)
        lineTmp=""
    
    for (k, v) in pkgMap.items():
        try:
            if markedAppMap.has_key(k):
                status = 2
            else:
                status = 1
            execSqlWithParams(droidGameConn, 'insert into APP_NOT_IN_DB_FROM_USER(PKG_NAME, NAME, INSTALL_CNT, CREATED_DATE, STATUS) values(%s, %s, %s, now(), %s)', (k, v['name'], v['cnt'], status))
        except Exception,e:
            print str(e)
            pass;
    
    closeConn(droidGameConn)
    print("#########over. use %s")%(time.time()-start)
    
pkgMap = {}
pkgMapFromDB={}
markedAppMap={}
main()
