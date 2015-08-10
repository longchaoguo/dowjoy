#!/usr/bin/python
# -*- coding: cp936 -*-
'''
 加载网游的游戏拼音字段数据进入地瓜道具中心item表
 SELECT CONCAT(id,"`",PINYIN,"`",NAME) from NETGAME_CHANNEL'
'''
__author__ = 'sgq'
import MySQLdb
import os
import sys
import numbers
from djutil.OptsUtil import OptsUtil
mysql = MySQLdb.connect(host="192.168.0.21",port=3312, user="moster", passwd="shzygjrmdwg", db="djstore",charset="utf8", use_unicode=True)
cursor = mysql.cursor()
fileName = 'data.txt'
def loadData():
    if not os.path.exists(fileName):
        print u'文件路径不对'
        return
    f = open(fileName,'rb')
    dicts = {}
    while 1:
        line = f.readline()
        if not line:
            break
        fields = line.split('`')
        gameId = fields[0]
        pinyin = fields[1]
        name = str(fields[2]).decode("gbk").encode('utf-8')
        firstChar = pinyin[:1].upper()
        if firstChar.isdigit():
            print u' 首字符为数字'+firstChar
            firstChar = "#"
        ascll= ord(firstChar)
        dicts[gameId]=[ascll,name]
    f.close()
    return dicts
def insertData(dicts = {}):
    if not dicts or len(dicts)<1:
        return
    keys = dicts.keys();
    dataList = []
    sql = 'update ITEM SET FIRST_CHAR=%s,GAME_NAME=%s where NETGAME_CHANNEL_ID=%s '
    for key in keys:
        dataList.append((dicts[key][0],dicts[key][1],key))
    cursor.executemany(sql,tuple(dataList))
    mysql.commit()
if __name__ == '__main__':
    opts = OptsUtil.getOpts(sys.argv)
    fileDate = None
    global fileName
    if not opts or not opts.get('--PATH'):
        fileName = "data.txt"
    else:
        fileDate = opts.get('--PATH')
    dicts = loadData()
    insertData(dicts)

