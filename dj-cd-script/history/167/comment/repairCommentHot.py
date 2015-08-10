#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月10日

@author: qiu.zhong@downjoy.com
# 0.只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）

'''
import pymongo
import MySQLdb

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment
key_hot = "hot"
key_resource = "resourceKey"
key_hotrange = "hr"
key_maxhot = "mh"
key_hotcount = "hc"
key_pubtime= "pubTime"

# 0. 只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）
def main():
    #1.1
    config = getConfig()
    #初始化资源热度值
    for out in db.resourceComment.find({"isHot":{"$exists":False}}, {"resourceKey":1, "goodRat":1, "subCnt":1, "content":1}):
        lenContent = len(out["content"])
        isHot = False
        if(lenContent>=config["n"] and count5Chinese(out["content"])):
            isHot = True
        db.resourceComment.update({"_id":out["_id"]}, {"$set":{"isHot":isHot}})


def count5Chinese(content):
#     us = unicode(content, "utf-8")
    count = 0
    for ch in content:
        b = isChinese(ord(ch))
        if(b):
            count = count + 1
            if(count >= 5):
                return True
    return False

def isChinese(ch):
    return (ch >= 0x4E00 and ch < 0xA000) or (ch >= 0x3400 and ch < 0x4DBF) or (ch >= 0xF900 and ch < 0xFAFF)

# 1.1 取编辑设置的N(字数), M, E（字数占权重）
def getConfig():
    conf = db.commentParamTO.find_one({"type":"hotConfig"})
    n = conf["hotRank"]
    l = conf["wordNum"]
    decayFactor = conf["decayFactor"]
    m = conf["constantM"]
    e = conf["constantE"]
 
    return {"rank":n, "decayFactor":decayFactor, "n":l, "m":m, "e":e}

main()   