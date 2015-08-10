#!/usr/bin/python
# -*- #coding:cp936


#####################################################
#此脚本每小时执行一次，收集所有游戏包名
#####################################################
import datetime
from djutil.DBUtil import DBUtil

dbUtilGame=DBUtil('droid_game_10')

ALL_PACKAGE={}
#####################################################
#获取上一小时内更新的所有游戏包名
def getAllPackageName():
    sql = "select PACKAGE_NAME FROM DIGUA_ALL_GAME_PACKAGE_NAME"
    rows = dbUtilGame.queryList(sql)
    for row in rows:
        ALL_PACKAGE[row[0]]=1

def addPackageName():
    insertSql = "insert into DIGUA_ALL_GAME_PACKAGE_NAME(GAME_ID, RESOURCE_TYPE, PACKAGE_NAME) values(%s, %s, %s)"
    sql = "SELECT G.ID, GP.PACKAGE_NAME FROM GAME_PKG GP INNER JOIN GAME G ON GP.GAME_ID = G.ID WHERE G.RESOURCE_TYPE = 1  AND G.STATUS = 1 and DATE_ADD(GP.CREATED_DATE, INTERVAL 1 HOUR)>NOW() GROUP BY GP.PACKAGE_NAME"
    rows = dbUtilGame.queryList(sql)
    for row in rows:
        print row[1]
        if ALL_PACKAGE.has_key(row[1]):
            continue
        dbUtilGame.insert(insertSql, (row[0], 1, row[1]))

    sql = "SELECT GAME_ID, PACKAGE_NAME FROM NETGAME_GAME_PKG WHERE DATE_ADD(CREATED_DATE, INTERVAL 1 HOUR)>NOW() GROUP BY PACKAGE_NAME"
    rows = dbUtilGame.queryList(sql)
    for row in rows:
        if ALL_PACKAGE.has_key(row[1]):
            continue
        dbUtilGame.insert(insertSql, (row[0], 5, row[1]))

def main():
    print "=============start %s===="%datetime.datetime.now()
    getAllPackageName()
    addPackageName()
    print "=============end   %s===="%datetime.datetime.now()

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtilGame: dbUtilGame.close()
