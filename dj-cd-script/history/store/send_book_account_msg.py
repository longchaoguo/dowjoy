#!/usr/bin/python
# -*- #coding:utf-8

#用于给预订用户发放领取礼包的站内信
#在礼包开始领取的40分钟之内的，给用户发相关的站内信
#部署服务器：118.144.65.121 /usr/local/bin/ 

import MySQLdb
import os
import sys
import datetime
reload(sys)
sys.setdefaultencoding("UTF-8")

conn = MySQLdb.connect(host="192.168.0.21", port=3312, user="moster", passwd="shzygjrmdwg", db="djstore", charset="utf8")
##message.url=jdbc:mysql://192.168.0.21:3309/dj_message?characterEncoding=utf8&noAccessToProcedureBodies=true
msgConn = MySQLdb.connect(host="192.168.0.21", port=3309, user="moster", passwd="shzygjrmdwg", db="dj_message", charset="utf8")

cursor = conn.cursor()
msgCursor = msgConn.cursor()

def  sendMsg(saleSettingId, mid, itemName, startDate):
    print saleSettingId, mid, itemName.encode("UTF-8"), startDate.strftime('%Y-%m-%d %H:%M')
    msg = "您预订的“"+itemName+"”礼包，将于"+ startDate.strftime('%Y-%m-%d %H:%M') +"开始领取。查看详情([url=http://sq.d.cn/mall/detail_"+str(saleSettingId)+".html]手机从此进入[/url].[url=http://mall.d.cn/detail_"+str(saleSettingId)+".html]电脑从此进入[/url])。"
    sql = """insert into MESSAGE(CREATED_DATE, CREATED_BY, RECEIVER, CONTENT, ISREAD, ISREPLYREAD, CREATED_BY_INFO, RECEIVED_BY_INFO, STATUS)
             values(now(), '3', %s, %s, 0, 0, '当当^_^乐乐(3)', %s, 1)"""
    msgCursor.execute(sql, (mid, msg, mid))

    
sql = "select S.ID, I.NAME, subdate(S.START_DATE, interval 30 minute) from SALE_SETTING S, ITEM I where I.ID = S.ITEM_ID and S.STOCKS>0 and S.BOOKABLE=1 and  now() > subdate(S.START_DATE, interval 40 minute) and S.START_DATE > subdate(now(), interval 60 minute) and S.START_DATE < now()"
cursor.execute(sql)
SALE_SETTINGS=cursor.fetchall()

if not SALE_SETTINGS:
    exit(1)

for saleSetting in SALE_SETTINGS:
    if saleSetting[2] > datetime.datetime.now():
        sql = "select MID from BOOK_ACCOUNT where SALE_SETTING_ID = %s and SENDED_MSG=0"
        cursor.execute(sql, (saleSetting[0]))
        rows=cursor.fetchall()
        if not rows:
            continue
        for row in rows:
            sendMsg(saleSetting[0], row[0], saleSetting[1], saleSetting[2])
            sql = "update BOOK_ACCOUNT set SENDED_MSG = 1 where SALE_SETTING_ID = %s and MID=%s"
            cursor.execute(sql, (saleSetting[0], row[0]))
    else:
        sql = "update BOOK_ACCOUNT set SENDED_MSG = 1 where SALE_SETTING_ID = %s"
        cursor.execute(sql, saleSetting[0])
            
msgConn.commit()
conn.commit()

msgConn.close()
conn.close()