#!/usr/bin/python
# -*- #coding:cp936
'''ÿ���賿1:00ִ��һ�Σ������ڵĵع��û���Ϣ�ƶ�����ʷ��Ϣ����'''

__author__ = "$Author: helin $"
__version__ = "$Revision: 1.0$"
__date__ = "$Date: 2014/01/23 20:00:00 $"


import MySQLdb
import time
import datetime


#�����ڵĵع��û���Ϣ�ƶ�����ʷ��Ϣ����
def moveOutTimeDiguaMessage():
    sql="select id from SERVER_MESSAGE where expired_date< CURDATE() "
    cursor.execute(sql)
    rs = cursor.fetchall()
    for row in rs:
        id = row[0]
        if checkHistoryRecordExist(id) == True:
            continue
        else :
            sql="insert into SERVER_MESSAGE_HISTORY select * from SERVER_MESSAGE where id=%s"%(id)
            cursor.execute(sql)
            conn.commit()
            sql="delete from  SERVER_MESSAGE where id = %s "%(id)
            cursor.execute(sql)
            conn.commit()

#���ĳ��������history�����Ƿ����
def checkHistoryRecordExist(id):
    sql="select count(*) from SERVER_MESSAGE_HISTORY where id = %s"%(id)
    cursor.execute(sql)
    rs = cursor.fetchall()
    count = rs[0][0]
    if count < 1:
        return False
    else:
        return True

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()
moveOutTimeDiguaMessage()

endTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
print "cdroid_old_digua_message_clean.py end at %s"%endTime

