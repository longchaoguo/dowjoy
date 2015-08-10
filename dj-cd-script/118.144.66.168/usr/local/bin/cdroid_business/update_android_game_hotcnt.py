#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shixuelin $"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2011/03/24 05:00:43 $"


import time
import string
import MySQLdb
import datetime

#��ȡ��־����ʱ��
delayday = 1

handledate = str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(delayday), "%Y-%m-%d"))

connStat = MySQLdb.connect(host='192.168.0.38', user='moster', passwd='shzygjrmdwg', db='download_stat')
cursorStat = connStat.cursor()

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()

#������Ϸ�ȶ�
def updateGameHotCnt(gameId, hotCnt):
    #if gameId == 40655 or gameId == 30201:
    #    hotCnt=hotCnt+3100
    sql="update GAME set HOT_CNT = %s where ID = %s"%(hotCnt, gameId)
    cursor.execute(sql)
    conn.commit()


#��ȡ��Ϸһ���µ�������
'''def getGameMonthlyDowns(gameId):
    sql="select isNull(DOWNS, 0) from ANDROID_DOWNLOAD_MONTHLY_SUM where GAME_ID = %s and datediff(month, DATE, '%s') = 0"%(gameId, handledate)
    cursorStat.execute(sql)
    rs = cursorStat.fetchall()
    #���û�д���Ϸ��������0����
    if len(rs) == 0:
        return 0
    else:
        return rs[0][0]
'''

#��ȡ��Ϸһ�ܵ�������
def getGameWeeklyDowns(gameId):
    sql="select ifnull(DOWNS, 0) from ANDROID_DOWNLOAD_WEEKLY_SUM where GAME_ID = %s and DATE_ADD(stat_date,INTERVAL 7 DAY )>'%s 00:00:00'"%(gameId, handledate)
    cursorStat.execute(sql)
    rs = cursorStat.fetchall()
    #���û�д���Ϸ��������0����
    if len(rs) == 0:
        return 0
    else:
        return rs[0][0]


#��ȡ����ʱ��
def getDays(createdDate):
    endDate=datetime.datetime.strptime(handledate,"%Y-%m-%d")
    startDate=createdDate
    diff = endDate - startDate
    days=diff.days
    #�����������С��7�죬��7�����
    if days < 7:
        return 7
    return days
    

#��ȡ����ʱ��ϵ��
def getCreatedDateCoefficient(days):
    #�����������С��30�죬������ʱ��ϵ��Ϊ1.0
    if days <= 30:
        return 1.0
    #���������������30�첢��С��60�죬������ʱ��ϵ��Ϊ0.9
    if days > 30 and days <= 60:
        return 0.9
    #���������������60�첢��С��90�죬������ʱ��ϵ��Ϊ0.8
    if days > 60 and days <= 90:
        return 0.8
    #���������������90�첢��С��180�죬������ʱ��ϵ��Ϊ0.3
    if days > 90 and days <= 180:
        return 0.3
    #��������0.9��ϵ�����м���
    else:
        return 0.9


#��ȡ�Ǽ�ϵ��
def getStarsCoefficient(stars):
    #����Ǽ�Ϊ3�ǣ����Ǽ�ϵ��Ϊ1.0����������(2 * stars) * 1.0 / 5�Ĺ�ʽ����
    if stars < 3:
        return 1.0
    else:
        return (2 * stars) * 1.0 / 5


def main():
    sql="select ID, DOWNS, CREATED_DATE, STARS from GAME where STATUS = 1"
    #sql="select ID, DOWNS, CREATED_DATE, STARS from GAME where STATUS = 1 and id in (9149, 22694, 22589, 39482)"
    cursor.execute(sql)
    rs = cursor.fetchall()
    #ѭ�����е���Ϸ
    for row in rs:
        gameId=row[0]
        downs=row[1]
        createdDate=row[2]
        stars=row[3]
        #monthlyDowns=getGameMonthlyDowns(gameId)
        weeklyDowns=getGameWeeklyDowns(gameId)
        days=getDays(createdDate)
        createdDateCoef=getCreatedDateCoefficient(days)
        starsCoef=getStarsCoefficient(stars)
        hotCnt=((weeklyDowns * 1.0 / 7) * 0.8 + (downs * 1.0 / days) * 0.2) * createdDateCoef * starsCoef
        updateGameHotCnt(gameId, int(hotCnt))

main()

cursor.close();
cursorStat.close();
conn.close()
connStat.close()
