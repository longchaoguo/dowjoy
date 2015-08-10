#!/usr/bin/python
#encoding=utf-8
'''

'''
import pymongo
import traceback
import StringIO

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment

def main():
    for out in db.resourceComment.find({"subComments":{"$exists":True}}):
        subComments = out["subComments"]
        if(subComments!=None):
            l = len(subComments)
            if(l>0):
                db.resourceComment.update({"_id":out["_id"]}, {"$set":{"replyId":subComments[l-1]["_id"]}})


if __name__ == '__main__':
    try:
        main()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if connection:
            connection.close()