#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shixuelin $"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2011/03/24 05:00:43 $"


import time
import string
import MySQLdb
import datetime

#获取日志产生时间
delayday = 1

handledate = str(datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(delayday), "%Y-%m-%d"))

connStat = MySQLdb.connect(host='192.168.0.38', user='moster', passwd='shzygjrmdwg', db='download_stat')
cursorStat = connStat.cursor()

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()

#更新游戏热度
def updateGameHotCnt(gameId, hotCnt):
    #if gameId == 40655 or gameId == 30201:
    #    hotCnt=hotCnt+3100
    sql="update GAME set HOT_CNT = %s where ID = %s"%(hotCnt, gameId)
    cursor.execute(sql)
    conn.commit()


#获取游戏一个月的总下载
'''def getGameMonthlyDowns(gameId):
    sql="select isNull(DOWNS, 0) from ANDROID_DOWNLOAD_MONTHLY_SUM where GAME_ID = %s and datediff(month, DATE, '%s') = 0"%(gameId, handledate)
    cursorStat.execute(sql)
    rs = cursorStat.fetchall()
    #如果没有此游戏的下载则按0计算
    if len(rs) == 0:
        return 0
    else:
        return rs[0][0]
'''

#获取游戏一周的总下载
def getGameWeeklyDowns(gameId):
    sql="select ifnull(DOWNS, 0) from ANDROID_DOWNLOAD_WEEKLY_SUM where GAME_ID = %s and DATE_ADD(stat_date,INTERVAL 7 DAY )>'%s 00:00:00'"%(gameId, handledate)
    cursorStat.execute(sql)
    rs = cursorStat.fetchall()
    #如果没有此游戏的下载则按0计算
    if len(rs) == 0:
        return 0
    else:
        return rs[0][0]


#获取上线时间
def getDays(createdDate):
    endDate=datetime.datetime.strptime(handledate,"%Y-%m-%d")
    startDate=createdDate
    diff = endDate - startDate
    days=diff.days
    #如果上线天数小于7天，则按7天计算
    if days < 7:
        return 7
    return days
    

#获取上线时间系数
def getCreatedDateCoefficient(days):
    #如果上线天数小于30天，则上线时间系数为1.0
    if days <= 30:
        return 1.0
    #如果上线天数大于30天并且小于60天，则上线时间系数为0.9
    if days > 30 and days <= 60:
        return 0.9
    #如果上线天数大于60天并且小于90天，则上线时间系数为0.8
    if days > 60 and days <= 90:
        return 0.8
    #如果上线天数大于90天并且小于180天，则上线时间系数为0.3
    if days > 90 and days <= 180:
        return 0.3
    #其他按照0.9的系数进行计算
    else:
        return 0.9


#获取星级系数
def getStarsCoefficient(stars):
    #如果星级为3星，则星级系数为1.0，其他按照(2 * stars) * 1.0 / 5的公式计算
    if stars < 3:
        return 1.0
    else:
        return (2 * stars) * 1.0 / 5


def main():
    sql="select ID, DOWNS, CREATED_DATE, STARS from GAME where STATUS = 1"
    #sql="select ID, DOWNS, CREATED_DATE, STARS from GAME where STATUS = 1 and id in (9149, 22694, 22589, 39482)"
    cursor.execute(sql)
    rs = cursor.fetchall()
    #循环所有的游戏
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
