#-*- coding: utf-8 -*-
#Filename store_week_rank.py

import MySQLdb
import datetime
lastDay = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(1), '%Y-%m-%d')
conn104=MySQLdb.connect(host = "192.168.0.21", port=3312, user = "moster", passwd = "shzygjrmdwg", db = "djstore", charset="utf8")
def addObtainAccountRank():
    try:
        cursor = conn104.cursor()
        sql = "select SALE_SETTING_ID, ITEM_ID, count(*) as OBTAIN_CNT from HISTORY H inner join ITEM I on I.ID=H.ITEM_ID where I.TYPE = 2 and SALE_SETTING_ID is not null and datediff(%s, H.CREATED_DATE) between 0 and 6 group by SALE_SETTING_ID"
        cursor.execute(sql,(lastDay))
        rows=cursor.fetchall()
        if rows and rows[0]:
            for row in rows:
                addRankData(row,1)
        conn104.commit()
        cursor.close()
    except Exception, ex:
        conn104.close()
        raise ex
        
def addBookAccountRank():
    try:
        cursor = conn104.cursor()
        sql = "select SALE_SETTING_ID, ITEM_ID, count(*) as BOOK_CNT from BOOK_ACCOUNT where SALE_SETTING_ID is not null and datediff(%s, CREATED_DATE) between 0 and 6 group by SALE_SETTING_ID "
        cursor.execute(sql,(lastDay))
        rows=cursor.fetchall()
        if rows and rows[0]:
            for row in rows:
                addRankData(row,2)
        conn104.commit()
        cursor.close()
    except Exception, ex:
        conn104.close()
        raise ex

def addPublicAccountRank():
    try:
        cursor = conn104.cursor()
        sql = "select SALE_SETTING_ID,ITEM_ID,count(*) as PUBLIC_CNT from PUBLIC_ACCOUNT where SALE_SETTING_ID is not null and datediff(%s, CREATED_DATE) between 0 and 6 group by SALE_SETTING_ID"
        cursor.execute(sql,(lastDay))
        rows=cursor.fetchall()
        if rows and rows[0]:
            for row in rows:
                addRankData(row,3)
        conn104.commit()
        cursor.close()
    except Exception, ex:
        conn104.close()
        raise ex
        
def addRankData(row,dataType):
    addData="insert into ACCOUNT_WEEK_RANK(SALE_SETTING_ID, ITEM_ID, QTY, DATA_TYPE, CREATED_DATE) values(%s,%s,%s,%s,%s)"
    try:
        cursor = conn104.cursor()
        cursor.execute(addData,(row[0],row[1],int(row[2]),dataType,lastDay))
        cursor.close()
    except Exception, ex:
        conn104.close().close
        raise ex
    
def clearData():
    try:
        cursor=conn104.cursor() 
        sql="delete from ACCOUNT_WEEK_RANK where CREATED_DATE=%s"
        cursor.execute(sql,lastDay)
    except Exception,ex:
        conn104.close()
        raise ex
    
def main():
    clearData()
    addObtainAccountRank()
    addBookAccountRank()
    addPublicAccountRank()

if __name__=='__main__':
    main()
