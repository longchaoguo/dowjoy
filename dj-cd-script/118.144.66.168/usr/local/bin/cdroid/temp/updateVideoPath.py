#!/usr/bin/env python
#-*- encoding: utf8 -*-
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
        conn = MySQLdb.connect(host='192.168.0.35', user='moster', passwd='shzygjrmdwg', db='droid_game',
                               charset='utf8')
        return conn
    except:
        print 'Connection mysql error!!'

def main():
    conn = getDroidConnection();
    fp=open("/usr/local/bin/cdroid/temp/videoPath.txt", "r");
    updateVideoSql = "UPDATE GAME G SET G.VIDEO = '%s' WHERE G.ID = %s";
    
    for eachline in fp:
       list = eachline.split('#');
       print list;
       execSql(conn, updateVideoSql%(list[1], list[0]));
    closeConn(conn);

       
main();