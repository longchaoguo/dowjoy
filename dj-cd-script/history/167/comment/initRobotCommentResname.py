#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月10日

@author: qiu.zhong@downjoy.com
# 0.只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）

'''
import pymongo

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.robotComment

def main():
    for out in db.robotUrlMappingInfo.find({},{"rid":1, "rt":1, "rn":1}):
        rid = out["rid"]
        rt = out["rt"]
        rn = out["rn"]
        db.robotComment.update({"rid":rid,"rt":rt}, {"$set":{"rn":rn}}, upsert=False, multi=True)

main()   





