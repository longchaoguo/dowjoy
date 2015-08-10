#!/usr/bin/python  
# -*- #coding:cp936  
  
import os  
import sys  
import re
import time
import datetime
import StringIO
import traceback
from urllib import urlopen  
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil

#邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"静态页抓取".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"静态页抓取脚本出错".encode("gbk")
mailTo = ['zhou.wu@downjoy.com', 'shan.liang@downjoy.com']
mailContents = u'Hi: \n'

def init():
    global url, filePath, tempFilePath
    #url = ''
    #filePath = ''
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_PATH') or not opts.get('--URL'):
        print "please execute the command : 'python gen_web_index_page.py --URL=网页地址 --FILE_PATH=文件全路径 '  to update the web index page"  
        return False
        
    filePath = opts.get('--FILE_PATH')
    if not filePath.endswith('.html'):
        print 'FILE_PATH is error'
        return False
        
    idx = filePath.rfind('/')
    if idx <= 0:
        print 'FILE_PATH is error'
        return False
    fileDir = filePath[:(idx + 1)]
    fileName = filePath[(idx + 1):]
    tempFileName = "temp_"+fileName
    tempFilePath = fileDir + tempFileName
    
    url = opts.get('--URL')
    if not url:
        print 'URL is error'
        return False
        
    print url
    print filePath
    print tempFilePath
    
    return True
    
def genPage(url, filePath, tempFilePath):
    pageData = urlopen(url).read()  
    if pageData.find("</html>") < 2000:  
        print "the original web "+url+" page is error! "  
        return  
        
    if os.path.exists(tempFilePath):
        print '正在抓取中....'
        return
    else:
        fp = file(tempFilePath, 'w')  
        fp.write(pageData)  
        fp.close()
    
    if os.path.getsize(tempFilePath) < 30000:
        os.system("rm %s"%(tempFilePath))
        print url+" the original web index page size is too small! "  
        return  
  
    os.system("mv %s %s"%(tempFilePath, filePath))

def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        #初始化
        if init():
            #抓取静态页面
            genPage(url, filePath, tempFilePath)
        
            #检验
            if os.path.exists(filePath):
                delayMinuites = (time.time() - time.mktime(time.localtime(os.stat(filePath).st_mtime)))/60
                if delayMinuites > 15:
                    ERROR_MSG = filePath + ": " + u"静态页文件太旧了！"
            else:
                ERROR_MSG = filePath + ": " + u"静态页文件未生成成功，不存在！"
            
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = url + ": " + filePath + ": " + str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if ERROR_MSG:
            sendMail()
    print "=================end   %s======" % datetime.datetime.now()

