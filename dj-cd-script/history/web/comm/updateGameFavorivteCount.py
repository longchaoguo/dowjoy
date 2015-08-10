__author__ = 'longr.chen@downjoy.com'
import time, MySQLdb
import pymongo
import json
import sys
from bson import BSON 
from bson import json_util as jsonb

connection=pymongo.Connection('192.168.0.72',27017)
db = connection.communication
param=[{ "$unwind" : "$favorites"},{ "$group" : { "_id" : { "id" : "$favorites.id" , "resType" : "$favorites.resType"} , "favorites" : { "$sum" : 1}}},{ "$sort" : { "favorites" : -1}}]
res = db.command('aggregate', 'comm_user_feed', pipeline=param)
strRes=jsonb.dumps(list(res['result']))
resouceCount = json.loads(strRes)
#print type(resouceCount)
def main():
    try:
        conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game",charset="utf8", use_unicode=True)
        cursor = conn.cursor()
        operatorData(cursor, resouceCount)
        conn.commit()
        cursor.close()
        conn.cursor()
        conn.close()
        print "SUCCESS"
    except MySQLdb.Error, e:
        print 'Cannot connect to server'
        print 'Error code:', e.args[0]
        print 'Error message:', e.args[1]
        sys.exit(1)

def operatorData(cursor,resouceCount):
    #fileSqlname = '1.txt'
    #fileSql = open(fileSqlname,'w')
    for row in resouceCount:
        sql=''
        if row['_id']['resType'] == 1 :
            sql="update GAME set COLLECT_CNT=%s where ID=%s" % (row['favorites'],row['_id']['id'])
            cursor.execute(sql)
        if row['_id']['resType'] == 2 :
            sql="update GAME set COLLECT_CNT=%s where ID=%s" % (row['favorites'],row['_id']['id'])
            cursor.execute(sql)
        if row['_id']['resType'] == 5 :
            sql="update NETGAME_CHANNEL set COLLECT_CNT=%s where ID=%s" % (row['favorites'],row['_id']['id'])
            cursor.execute(sql)
        #fileSql.write(sql+";")
        #fileSql.write("\n")
       
main()
        

