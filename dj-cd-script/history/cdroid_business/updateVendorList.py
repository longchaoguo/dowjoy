#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: liangshan$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/10/20 17:46 $"

#####################################################
#�˽ű�ÿ20����ִ��һ�Σ������̹�������Ϸ����Ѷ��Ϣ����A��B���С�
#####################################################
import datetime
import StringIO
import traceback
import re
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

#��ʼ������
dbUtil_droid_game = DBUtil('droid_game_10')

#��ʶ�����б�
VENDOR_LIST_TYPE = 'VENDOR_GAME_NEWS_LIST'

#����
today = datetime.datetime.today()

#####�ʼ���������
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"������������".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"��׿�����б����ɴ�����Ϣ".encode("gbk")
mailTo=['shan.liang@downjoy.com']
mailContents=u'Hi: \n'

#��ȡ���̡���Ϸ��Ϣ(�ų�Internet)
def getVendorGameList():
    sql = '''SELECT V.ID, 
                    V.NAME, 
                    V.EN_NAME,
                    G.ID, 
                    G.NAME, 
                    G.EN_NAME, 
                    G.ICON, 
                    G.STARS, 
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT, 
                    G.DATA_TYPE, 
                    G.OUTLINE, 
                    G.DESCRIPTION, 
                    G.OTHER_INFOS,
                    G.CREATED_DATE,
                    G.PUBLISH_DATE,
                    G.RESOURCE_TYPE,
                    G.EXACT_RELEASE_DATE, 
                    G.ESTIMATE_RELEASE_DATE, 
                    G.GAME_CATEGORY_ID,
                    GP.PACKAGE_NAME
            FROM VENDOR V 
            INNER JOIN GAME G ON V.ID = G.VENDOR_ID 
            INNER JOIN GAME_PKG GP ON GP.GAME_ID = G.ID 
            WHERE V.ID != 1
            AND G.RESOURCE_TYPE = 1 
            AND G.STATUS > 0
            GROUP BY G.ID 
            ORDER BY V.ID
        '''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        rows = dbUtil_droid_game.queryList(curSql, (startIdx, pageNum))
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    vendorGameList = []
    if not allRows:
        return vendorGameList
    for row in allRows:
        vendorGameInfo = {}
        vendorGameInfo['VENDOR_ID'] = row[0]
        vendorGameInfo['VENDOR_NAME'] = row[1]
        vendorGameInfo['VENDOR_EN_NAME'] = row[2]
        vendorGameInfo['GAME_ID'] = row[3]
        vendorGameInfo['GAME_NAME'] = row[4]
        vendorGameInfo['GAME_EN_NAME'] = row[5]
        vendorGameInfo['GAME_ICON'] = row[6]
        vendorGameInfo['GAME_STARS'] = row[7]
        vendorGameInfo['GAME_HOT_CNT'] = row[8]
        vendorGameInfo['GAME_DATA_TYPE'] = row[9]
        vendorGameInfo['GAME_OUTLINE'] = row[10]
        vendorGameInfo['GAME_DESCRIPTION'] = row[11]
        vendorGameInfo['GAME_OTHER_INFOS'] = row[12]
        vendorGameInfo['GAME_CREATED_DATE'] = row[13]
        vendorGameInfo['GAME_PUBLISH_DATE'] = row[14]
        vendorGameInfo['GAME_RESOURCE_TYPE'] = row[15]
        vendorGameInfo['GAME_EXACT_RELEASE_DATE'] = row[16]
        vendorGameInfo['GAME_ESTIMATE_RELEASE_DATE'] = row[17]
        vendorGameInfo['GAME_CATEGORY_ID'] = row[18]
        vendorGameInfo['GAME_PACKAGE_NAME'] = row[19]
        vendorGameList.append(vendorGameInfo)

    return vendorGameList
    
#��ȡ����Ϸ�й����ĳ������ţ�35������Ϸ���⣨37������Ϸ���ԣ�36��
def getGameNewsDic():
    sql = '''SELECT GNA.GAME_ID, 
                    N.ID, 
                    N.TITLE, 
                    N.ICON, 
                    N.AUTHOR, 
                    N.GAME_CATEGORY_ID, 
                    N.PUBLISH_DATE, 
                    NC.CONTENT, 
                    N.HAS_VIDEO,
                    N.ORIGINAL_URL
            FROM GAME_NEWS_ASSOCIATE GNA 
            INNER JOIN NEWS N ON N.ID = GNA.NEWS_ID 
            INNER JOIN NEWS_CONTENT NC ON NC.NEWS_ID = N.ID 
            WHERE N.GAME_CATEGORY_ID IN (35,36,37) 
            AND N.STATUS = 1 
            AND NC.PAGE_ID = 1
        '''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        rows = dbUtil_droid_game.queryList(curSql, (startIdx, pageNum))
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    gameNewsDic = {}
    if not allRows:
        return gameNewsDic
    for row in allRows:
        newsInfo = {}
        gameId = row[0]
        newsInfo['NEWS_ID'] = row[1]
        newsInfo['NEWS_TITILE'] = row[2]
        newsInfo['NEWS_ICON'] = row[3]
        newsInfo['NEWS_AUTHOR'] = row[4]
        newsInfo['NEWS_GAME_CATEGORY_ID'] = row[5]
        newsInfo['NEWS_PUBLISH_DATE'] = row[6]
        newsInfo['NEWS_FIRST_PAGE_CONTENT'] = row[7]
        newsInfo['NEWS_HAS_VIDEO'] = row[8]
        newsInfo['NEWS_ORIGINAL_URL'] = row[9]
        if gameId in gameNewsDic:
            gameNewsDic[gameId].append(newsInfo)
        else:
            newsList = []
            newsList.append(newsInfo)
            gameNewsDic[gameId] = newsList
           
    return gameNewsDic
            
#��ȡ�������ı���
def getTableNameForInsert():
    tableName = ''
    sql = "select TABLE_NAME from GAME_LIST_TABLE_STATUS where TYPE = '%s'" % VENDOR_LIST_TYPE
    row = dbUtil_droid_game.queryRow(sql)
    if row and row[0]:
        tableName = row[0]

    if tableName[-1] == 'A':
        tableName = tableName[:-1] + 'B'
    elif tableName[-1] == 'B':
        tableName = tableName[:-1] + 'A'
    else:
        tableName = ''

    return tableName

#��մ�������
def clearTable(tableName):
    sql = ''
    sql = "TRUNCATE TABLE %s" % tableName
    dbUtil_droid_game.delete(sql)
 
 #����Ϸother_info�����ȡ��Ƶ��ַ
def getVideoAddr(gameOtherInfoJson):
    videoAddr = None
    if not gameOtherInfoJson or len(gameOtherInfoJson) == 0:
        return videoAddr
        
    #��Ƶ��Ϣ
    gameOtherInfoDic = eval(gameOtherInfoJson)
    videoInfo = gameOtherInfoDic.get('video')
    if not videoInfo:
        return videoAddr
    
    #ֻ��ȡ��Ƶ��ַ��Ϣ
    startPos = videoInfo.find('src')
    if startPos > -1:
        startPos = videoInfo.find('\"', startPos)
        endPos = videoInfo.find('\"', startPos + 1)
        videoAddr = videoInfo[(startPos + 1):endPos]
    return videoAddr
 
#������Ϣ�����ݿ���
def insertInfos(tableName, vendorGameList, gameNewsDic):
    #����SQL
    sql = "INSERT INTO %s " % tableName
    sql += "(VENDOR_ID, VENDOR_NAME, VENDOR_EN_NAME, GAME_ID, GAME_NAME, GAME_EN_NAME, GAME_ICON, GAME_STARS, GAME_HOT_CNT, GAME_DATA_TYPE, GAME_OUTLINE, GAME_DESCRIPTION, GAME_VIDEO, GAME_VIDEO_ICON, GAME_CREATED_DATE, GAME_PUBLISH_DATE, GAME_RESOURCE_TYPE, GAME_RELEASE_DATE, GAME_CATEGORY_ID, GAME_PACKAGE_NAME, NEWS_ID, NEWS_TITLE, NEWS_ICON, NEWS_AUTHOR, NEWS_DESCRIPTION, NEWS_CATEGORY_ID, NEWS_PUBLISH_DATE, NEWS_HAS_VIDEO, NEWS_ORIGINAL_URL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    #����������Ϸ
    datalist = []
    for vendorGameInfo in vendorGameList:
        #��Ϸ��Ƶ��ַ��Ϣ
        gameVideoAddr = getVideoAddr(vendorGameInfo['GAME_OTHER_INFOS'])
        
        #Ԥ����Ϸ����ʱ��
        releaseDate = None
        exactReleaseDate = vendorGameInfo['GAME_EXACT_RELEASE_DATE']
        if exactReleaseDate:
            estimateReleaseDate = vendorGameInfo['GAME_ESTIMATE_RELEASE_DATE']
            if exactReleaseDate < today:
                releaseDate = u'��Ʊ'
            elif estimateReleaseDate != None:
                releaseDate = estimateReleaseDate
            else:
                releaseDate = exactReleaseDate
        
        #��ѯ��ǰ��Ϸ��������Ѷ
        newsList = gameNewsDic.get(vendorGameInfo['GAME_ID'])
        
        #��Ϸ��ƵͼƬ��Ϣ��������Ϸ����Ѷ��ICON��Ϣ�������ƵͼƬ��Ϣ��
        gameVideoIcon = getVideoIconByNewsList(newsList)
        
        #��������
        if newsList:
            for newsInfo in newsList:
                #��Ѷ������Ϣ
                datalist.append((vendorGameInfo['VENDOR_ID'],
                                vendorGameInfo['VENDOR_NAME'],
                                vendorGameInfo['VENDOR_EN_NAME'],
                                vendorGameInfo['GAME_ID'],
                                vendorGameInfo['GAME_NAME'],
                                vendorGameInfo['GAME_EN_NAME'],
                                vendorGameInfo['GAME_ICON'],
                                vendorGameInfo['GAME_STARS'],
                                vendorGameInfo['GAME_HOT_CNT'],
                                vendorGameInfo['GAME_DATA_TYPE'],
                                vendorGameInfo['GAME_OUTLINE'],
                                vendorGameInfo['GAME_DESCRIPTION'],
                                gameVideoAddr,
                                gameVideoIcon,
                                vendorGameInfo['GAME_CREATED_DATE'],
                                vendorGameInfo['GAME_PUBLISH_DATE'],
                                vendorGameInfo['GAME_RESOURCE_TYPE'],
                                releaseDate,
                                vendorGameInfo['GAME_CATEGORY_ID'],
                                vendorGameInfo['GAME_PACKAGE_NAME'],
                                newsInfo['NEWS_ID'],
                                newsInfo['NEWS_TITILE'],
                                newsInfo['NEWS_ICON'],
                                newsInfo['NEWS_AUTHOR'],
                                newsInfo['NEWS_FIRST_PAGE_CONTENT'],
                                newsInfo['NEWS_GAME_CATEGORY_ID'],
                                newsInfo['NEWS_PUBLISH_DATE'],
                                newsInfo['NEWS_HAS_VIDEO'],
                                newsInfo['NEWS_ORIGINAL_URL']))
        else:
            datalist.append((vendorGameInfo['VENDOR_ID'],
                            vendorGameInfo['VENDOR_NAME'],
                            vendorGameInfo['VENDOR_EN_NAME'],
                            vendorGameInfo['GAME_ID'],
                            vendorGameInfo['GAME_NAME'],
                            vendorGameInfo['GAME_EN_NAME'],
                            vendorGameInfo['GAME_ICON'],
                            vendorGameInfo['GAME_STARS'],
                            vendorGameInfo['GAME_HOT_CNT'],
                            vendorGameInfo['GAME_DATA_TYPE'],
                            vendorGameInfo['GAME_OUTLINE'],
                            vendorGameInfo['GAME_DESCRIPTION'],
                            gameVideoAddr,
                            gameVideoIcon,
                            vendorGameInfo['GAME_CREATED_DATE'],
                            vendorGameInfo['GAME_PUBLISH_DATE'],
                            vendorGameInfo['GAME_RESOURCE_TYPE'],
                            releaseDate,
                            vendorGameInfo['GAME_CATEGORY_ID'],
                            vendorGameInfo['GAME_PACKAGE_NAME'],
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,))
        if len(datalist)>=1000:
            dbUtil_droid_game.insertMany(sql, tuple(datalist))
            datalist = []
    if datalist:
        dbUtil_droid_game.insertMany(sql, tuple(datalist))
        datalist = []                
    
 #���±������������б�ı���
def updateTableName(tableName):
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),VENDOR_LIST_TYPE)
    dbUtil_droid_game.update(sql)

#��������ص���Ѷ�б��е�ICON��Ϣ��ȡ��Ϸ��ƵͼƬ��Ϣ
def getVideoIconByNewsList(newsList):
    videoIcon = None
    
    #������ѶICON���ų��պ�Ĭ�ϵ�ICON��
    if newsList:
        for newsInfo in newsList:
            newsIcon = newsInfo['NEWS_ICON']
            if newsIcon and (newsIcon != '') and (newsIcon.startswith('http://img.android.d.cn/android/cdroid_stable/newsIcon') == False) and (newsIcon.startswith('http://raw.android.d.cn/cdroid_res/web/news') == False):
                videoIcon = newsIcon
                break
                
    return videoIcon

#����Ϣ���뵽���ݿ���
def insert(vendorGameList, gameNewsDic):
    #��ȡ����������
    tableName = getTableNameForInsert()
    print 'tableName: %s' % tableName

    #��մ�������
    clearTable(tableName)

    #��������
    print 'start insert'
    insertInfos(tableName, vendorGameList, gameNewsDic)
    print 'end insert'

    #���±������������б�ı���
    updateTableName(tableName)
    
#�ʼ�
def sendMail():
    global mailContents
    mailContents=(mailContents+u'���̽ű�ִ�г���\n������Ϣ��%s\nлл'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
if __name__ == "__main__":
    print "=============start %s===="%datetime.datetime.now()
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
       
        #��ȡ���̡���Ϸ��Ϣ
        vendorGameList = getVendorGameList()
        
        #��ȡ����Ϸ�й����ĳ������ţ�35������Ϸ���⣨37������Ϸ���ԣ�36��
        gameNewsDic = getGameNewsDic()
        
        #������Ϣ�����ݿ���
        insert(vendorGameList, gameNewsDic)
        
        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        maxTime = datetime.timedelta(minutes=15)
        if spentTime > maxTime:
             #�ű����г�ʱ�����澯��Ϣ�����䣬�п������ݿ����ܻ���~~~
             ERROR_MSG = u'�ű����г�ʱ'
    except Exception, ex:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_droid_game: dbUtil_droid_game.close()
        if ERROR_MSG:
            sendMail()
    print "=============end   %s===="%datetime.datetime.now()