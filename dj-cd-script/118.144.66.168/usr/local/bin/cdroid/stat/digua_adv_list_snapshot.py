#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: helin$"
################################################
#������������¼�عϹ��λ�Ŀ���
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

#####�ʼ���������
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailContents = u'Hi: <br/>'
#############################################

#���ݿ�����
droid_game_10=DBUtil('droid_game_10')



fileDir = "/usr/local/bin/cdroid/report/data/"
fileName = "digua_adv_snapshot_%s.xls"
fileBackupName = "digua_adv_snapshot_%s_bak_%s.xls"

#����ר��id��ƴ������Ӧ��ϵ
NETGAME_CHANNEL_PINYIN_DICT = {}
#����id��ƴ������Ӧ��ϵ
NETGAME_GAME_PINYIN_DICT = {}

urltemplate_game="http://android.d.cn/game/%s.html"
urltemplate_software="http://android.d.cn/software/%s.html"
urltemplate_netgame="http://android.d.cn/%s"
global currentSheetRow
currentSheetRow=0
#################################################


'''
��ȡ��ҳ�������λ
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
            typename=u"��Ϸ"
            url = urltemplate_game%resId
        elif advtype == 2:
            typename=u"���"
            url = urltemplate_software%resId
        elif advtype == 3:
            typename=u"����"
            pinyin=""
            if NETGAME_GAME_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_GAME_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        elif advtype == 4:
            typename=u"ר��"
        elif advtype == 5:
            typename=u"���"
        elif advtype == 6:
            typename=u"��Ѷ"
        if language_type == 2:
            languageTypeName = u"����"
        elif language_type == 4:
            languageTypeName = u"����"
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'��ҳ��ͼ')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, '%s'%languageTypeName)

'''
��ȡ��ҳ�Ƽ����λ
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
            typename=u"��Ϸ"
            url = urltemplate_game%resId
        elif advtype == 2:
            typename=u"���"
            url = urltemplate_software%resId
        elif advtype == 3:
            typename=u"����"
            pinyin=""
            if NETGAME_GAME_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_GAME_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        if language_type == 2:
            languageTypeName = u"����"
        elif language_type == 4:
            languageTypeName = u"����"
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'��ҳ�Ƽ�')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, '%s'%languageTypeName)
'''
��ȡ��ҳ�Ƽ����λ
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
            typename=u"��Ϸ"
            url = urltemplate_game%resId
        elif resource_type == 2:
            typename=u"���"
            url = urltemplate_software%resId
        elif resource_type == 5:
            typename=u"����"
            pinyin=""
            if NETGAME_CHANNEL_PINYIN_DICT.has_key(resId):
                pinyin = NETGAME_CHANNEL_PINYIN_DICT[resId]
                url = urltemplate_netgame%pinyin
        sheet.write(currentSheetRow, 0, u'%s'%dateStr)
        sheet.write(currentSheetRow, 1, u'�����б�')
        sheet.write(currentSheetRow, 2, '%s'%resId)
        sheet.write(currentSheetRow, 3, u'%s'%name)
        sheet.write(currentSheetRow, 4, '%s'%typename)
        sheet.write(currentSheetRow, 5, '%s'%url)
        sheet.write(currentSheetRow, 6, u'-')


'''
д����ʷ����
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


#�����ʼ�
def sendReportMail(reportFile):
    reportReceivers = ["jacky@downjoy.com","xinjie.wang@downjoy.com","eric@downjoy.com","cherry.zhang@downjoy.com","shan.liang@downjoy.com","zhou.wu@downjoy.com"]
    #reportReceivers = ["lin.he@downjoy.com"]
    body = "���ã��عϹ��λsnapshot������������������������⣬���[��ɺ]��ϵ��"

    mailFromName=u"��׿ҵ�񱨱�".encode("gbk")
    mailSubject = (u"�عϹ��λsnapshot����_%s" %(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))).encode("gbk")
    mail=MailUtil(reportFile, mailServer, mailFromName, mailFromAddr, reportReceivers, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailAttachment(body)


def sendMail():
    global mailContents
    mailSubject=u"��¼�عϹ��λ���մ�����Ϣ".encode("gbk")
    mailFromName=u"������������".encode("gbk")
    mailContents=(mailContents + u" ��¼�عϹ��λ���ճ���\n������Ϣ��%s\nлл!"%ERROR_MSG).encode('gbk')
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
        #�Ƚ�֮ǰ�ı������ݶ�������Ȼ��д�ڵ�ǰͳ�Ƶ����ݺ��棬��֤���µ�������ǰ��
        dataList = backupAndReadData(monthStr)
        global workbook
        reportFile = fileDir + fileName%monthStr
        if not os.path.exists(reportFile):
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet('%s'%monthStr, cell_overwrite_ok=True)
            sheet.write(0, 0, u'ʱ��')
            sheet.write(0, 1, u'��Ŀ')
            sheet.write(0, 2, u'��Դid')
            sheet.write(0, 3, u'��Դ����')
            sheet.write(0, 4, u'����')
            sheet.write(0, 5, u'url')
            sheet.write(0, 6, u'���԰汾')
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
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if droid_game_10: 
            droid_game_10.close()
        if ERROR_MSG:
            sendMail()


