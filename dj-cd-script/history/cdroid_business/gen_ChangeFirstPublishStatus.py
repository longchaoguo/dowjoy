#!/usr/bin/python
#-*- encoding: utf8 -*-
# author : Jonathan Lai(xingbing.lai@downjoy.com)
# version: 1.0.0
# Date   : 2013/03/21 09:57:36
# 功能   : 定期修改游戏首发状态
import time
import MySQLdb


def main():
    try:
        conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game", charset="utf8", use_unicode=True)
        cursor = conn.cursor()
        sql1 = '''
        SELECT G.ID FROM GAME G
        INNER JOIN GAME_PKG GP ON GP.GAME_ID=G.ID
        WHERE G.IS_FIRST_PUBLISH = 1
        AND TO_DAYS(NOW()) - TO_DAYS(GP.CREATED_DATE) > 5
        ORDER BY GP.CREATED_DATE DESC'''

        cursor.execute(sql1)
        data = cursor.fetchall()
        for row in data:
            gameId = row[0]
            sql2 = "UPDATE GAME G SET G.IS_FIRST_PUBLISH = 0 WHERE G.ID = %s" % gameId
            cursor.execute(sql2)
            conn.commit()
            print 'Changed success ! [gameId = %s ]' % gameId
        cursor.close()
        conn.close()
    except MySQLdb.Error, e:
        print 'Cannot connect to server'
        print 'Error code:', e.args[0]
        print 'Error message:', e.args[1]

if __name__ == "__main__":
    print '>>BEGIN<<'
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    main()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print '>>END<<'
