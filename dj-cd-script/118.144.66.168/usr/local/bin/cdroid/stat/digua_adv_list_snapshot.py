#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: helin$"
################################################
#功能描述：记录地瓜广告位的快照
################################################
import os
import datetime
import sys
import StringIO
import traceback
import xlwt
import xlrd
import smtplib
import email
import base64
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil
from xlutils.copy import copy #@UnresolvedImport
import xlwt
from xlwt import Formula

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailContents = u'Hi: <br/>'
#############################################

#数据库连接
droid_game_10=DBUtil('droid_game_10')



fileDir = "/usr/local/bin/cdroid/report/data/"
fileName = "digua_adv_snapshot_%s.xls"
fileBackupName = "digua_adv_snapshot_%s_bak_%s.xls"

#网游专区id和拼音带对应关系
NETGAME_CHANNEL_PINYIN_DICT = {}
#网游id和拼音带对应关系
NETGAME_GAME_PINYIN_DICT = {}

urltemplate_game="http://android.d.cn/game/%s.html"
urltemplate_software="http://android.d.cn/software/%s.html"
urltemplate_netgame="http://android.d.cn/%s"
global currentSheetRow
currentSheetRow=0
#################################################


'''
获取首页滚动广告位
'''
def statIndexAdv(sheet,dateStr):
    global currentSheetRow
    currentSheetRow = currentSheetRow+1
    sql = '''select A.RESOURCE_ID as resourceId,A.NAME as name,A.INDEX_ADV_TYPE as indexAdvType,A.language_type
                   from INDEX_ADV47 A
                   where
                   (A.START_DATE < now() or A.START_DATE is null)
                   and (A.END_DATE > now() or A.END_DATE is null)
                   and A.STATUS = 1 and A.IMAGE_TYPE = 1
                   and A.VERSION = '6.4' and A.GROUP_ID = 1
                   ORDER BY language_type,ORDER_NO limit 100 '''
    
    rows = droid_game_10.queryList(sql)
    if not rows:
        return
    for row in rows:
        currentSheetRow = currentSheetRow+1
        resId=str(row[0])
        name=row[1]
        advtype=row[2]
        language_type=row[3]
        typename=""
        url=""
        languageTypeName=""
        if advtype == 1:
            typename=u"游戏"
            url = urltemplate_game%resId
        elif advtype == 2:
            typename=u"软件"
            url = urltemplate_software%resId
        elif advtype == 3:
            typename=u"网游"
            pinyin=""
            if NETGAME_GAME_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_GAME_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        elif advtype == 4:
            typename=u"专题"
        elif advtype == 5:
            typename=u"广告"
        elif advtype == 6:
            typename=u"资讯"
        if language_type == 2:
            languageTypeName = u"中文"
        elif language_type == 4:
            languageTypeName = u"韩文"
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'首页大图')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, '%s'%languageTypeName)

'''
获取首页推荐广告位
'''
def statIndexRecomment(sheet,dateStr):
    global currentSheetRow
    currentSheetRow = currentSheetRow+1
    sql = ''' SELECT RESOURCE_ID AS resourceId,
        NAME AS name,
        INDEX_ADV_TYPE AS indexAdvType,
        language_type
        FROM INDEX_ADV47
        WHERE GROUP_ID = 2
        AND VERSION = '6.4'
        ORDER BY language_type,ORDER_NO 
        limit 100'''
    
    rows = droid_game_10.queryList(sql)
    if not rows:
        return
    for row in rows:
        currentSheetRow = currentSheetRow+1
        resId=str(row[0])
        name=row[1]
        advtype=row[2]
        language_type=row[3]
        typename=""
        url=""
        languageTypeName=""
        if advtype == 1:
            typename=u"游戏"
            url = urltemplate_game%resId
        elif advtype == 2:
            typename=u"软件"
            url = urltemplate_software%resId
        elif advtype == 3:
            typename=u"网游"
            pinyin=""
            if NETGAME_GAME_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_GAME_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        if language_type == 2:
            languageTypeName = u"中文"
        elif language_type == 4:
            languageTypeName = u"韩文"
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'首页推荐')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, '%s'%languageTypeName)
'''
获取首页推荐广告位
'''
def statLatestGame(sheet,dateStr):
    global currentSheetRow
    currentSheetRow = currentSheetRow+1
    sql = '''SELECT  resource_id, name,resource_type
             from GAME_LIST_NEWEST_A order by id asc limit 50'''
    
    rows = droid_game_10.queryList(sql)
    if not rows:
        return
    for row in rows:
        currentSheetRow = currentSheetRow+1
        resId=str(row[0])
        name=row[1]
        resource_type=row[2]
        typename=""
        url=""
        if resource_type == 1:
            typename=u"游戏"
            url = urltemplate_game%resId
        elif resource_type == 2:
            typename=u"软件"
            url = urltemplate_software%resId
        elif resource_type == 5:
            typename=u"网游"
            pinyin=""
            if NETGAME_CHANNEL_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_CHANNEL_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'最新列表')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, u'-')


'''
写入历史数据
'''
def addHistoryData(sheet,dataList):
    global currentSheetRow
    for data in dataList:
        currentSheetRow = currentSheetRow+1
        if len(data) <7 :
            continue
        sheet.write(currentSheetRow, 0, data[0])
        sheet.write(currentSheetRow, 1, data[1])
        sheet.write(currentSheetRow, 2, data[2])
        sheet.write(currentSheetRow, 3, data[3])
        sheet.write(currentSheetRow, 4, data[4])
        sheet.write(currentSheetRow, 5, data[5])
        sheet.write(currentSheetRow, 6, data[6])



def initNetgameChannelPinyinDict():
    sql="select G.id,C.pinyin from NETGAME_CHANNEL C,NETGAME_GAME G WHERE G.CHANNEL_ID=C.ID"
    rows = droid_game_10.queryList(sql)
    for row in rows:
        NETGAME_GAME_PINYIN_DICT[str(row[0])] = row[1]
    sql="select id,pinyin from NETGAME_CHANNEL"
    rows = droid_game_10.queryList(sql)
    for row in rows:
        NETGAME_CHANNEL_PINYIN_DICT[str(row[0])] = row[1]
    
        
def backupAndReadData(monthStr):
    filePath = fileDir + fileName%monthStr
    dataList = []
    if not os.path.exists(filePath):
        return dataList
    rb = xlrd.open_workbook(filePath,encoding_override='utf-8')
    sheet = rb.sheet_by_index(0)
    nrows = sheet.nrows
    for i in range(1,nrows):
        row = sheet.row_values(i)
        data = []
        for j in range(0,7):
            data.append(row[j])
        dataList.append(data)
    nowStr = dateStr = datetime.datetime.strftime(today, "%Y%m%d%H%M%S")
    fileBackupPath = fileDir + fileBackupName%(monthStr,nowStr)
    rmPath = fileDir + fileBackupName%(monthStr,'*')
    cmd = "rm -f %s"%rmPath
    os.system(cmd)
    cmd = "mv -f %s %s"%(filePath,fileBackupPath)
    os.system(cmd)
    return dataList


#发送邮件
def sendReportMail(reportFile):
    reportReceivers = ["jacky@downjoy.com","xinjie.wang@downjoy.com","eric@downjoy.com","cherry.zhang@downjoy.com","shan.liang@downjoy.com","zhou.wu@downjoy.com"]
    #reportReceivers = ["lin.he@downjoy.com"]
    body = "您好：地瓜广告位snapshot报表，见附件。如有需求和问题，请和[梁珊]联系。"

    mailFromName=u"安卓业务报表".encode("gbk")
    mailSubject = (u"地瓜广告位snapshot报表_%s" %(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))).encode("gbk")
    mail=MailUtil(reportFile, mailServer, mailFromName, mailFromAddr, reportReceivers, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailAttachment(body)


def sendMail():
    global mailContents
    mailSubject=u"记录地瓜广告位快照错误信息".encode("gbk")
    mailFromName=u"当乐数据中心".encode("gbk")
    mailContents=(mailContents + u" 记录地瓜广告位快照出错，\n错误信息：%s\n谢谢!"%ERROR_MSG).encode('gbk')
    mailTo=['lin.he@downjoy.com']
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#############################################
if __name__ == '__main__':
    try:
        today = datetime.datetime.today()
        dateStr = datetime.datetime.strftime(today, "%Y-%m-%d %H:%M")
        monthStr = datetime.datetime.strftime(today, "%Y-%m")
        
        initNetgameChannelPinyinDict()
        #先将之前的报表数据读出来，然后写在当前统计的数据后面，保证最新的数据在前面
        dataList = backupAndReadData(monthStr)
        global workbook
        reportFile = fileDir + fileName%monthStr
        if not os.path.exists(reportFile):
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet('%s'%monthStr, cell_overwrite_ok=True)
            sheet.write(0, 0, u'时间')
            sheet.write(0, 1, u'栏目')
            sheet.write(0, 2, u'资源id')
            sheet.write(0, 3, u'资源名称')
            sheet.write(0, 4, u'类型')
            sheet.write(0, 5, u'url')
            sheet.write(0, 6, u'语言版本')
            #patternOdd = xlwt.Pattern()
            #patternOdd.pattern = patternOdd.SOLID_PATTERN
            #patternOdd.pattern_fore_colour = 5
            #styleOdd = xlwt.XFStyle() 
            #styleOdd.pattern = patternOdd 
            #style = styleOdd
            statIndexAdv(sheet,dateStr)
            statIndexRecomment(sheet,dateStr)
            statLatestGame(sheet,dateStr)
            
            addHistoryData(sheet,dataList)
            
            workbook.save(reportFile)
            sendReportMail(reportFile)
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if droid_game_10: 
            droid_game_10.close()
        if ERROR_MSG:
            sendMail()


