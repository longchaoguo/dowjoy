#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2014/10/30 $"

import MySQLdb
import traceback
import datetime
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import smtplib
import httplib


#�쳣�ʼ�������
#MONITOR_MAIL=['zhou.wu@downjoy.com','shan.liang@downjoy.com','xiaodong.zheng@downjoy.com']
MONITOR_MAIL=['shan.liang@downjoy.com']

#���ݿ�����
conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game", use_unicode=True, charset='utf8')
cursor = conn.cursor()

#��ʶԤ���б�
TRAILER_LIST_TYPE = 'GAME_SOFTWARE_NETGAME_TRAILER_LIST'

#����
today = datetime.datetime.today()

#�����ʼ�
def sendmail(From, To, msgBody, title):
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(msgBody, 'html', 'gb2312')
    main_msg.attach(text_msg)

    main_msg['From'] = From
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = title
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail(From, To, fullText)
    finally:
        server.quit()

#��ȡ��Ϸ�����Ԥ���б�
def getTrailerListOfGameSoftware():
    sql = '''SELECT G.ID,
                    G.NAME,
                    G.EN_NAME,
                    G.GAME_CATEGORY_ID,
                    G.COMMENTS,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.ICON,
                    G.LATEST_VERSION_NAME,
                    G.DATA_TYPE,
                    G.LANGUAGE_TYPE,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE AS G_CREATED_DATE,
                    G.GOOD_RATING_CNT,
                    C.NAME AS CNAME,
                    G.BANNER,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    G.RESOURCE_TYPE,
                    G.EXACT_RELEASE_DATE, 
                    G.ESTIMATE_RELEASE_DATE,
                    V.NAME AS VENDOR_NAME,
                    V.EN_NAME AS VENDOR_EN_NAME,
                    BIT_OR(GP.CHANNEL_FLAG_SET & GP.SYNC_CHANNEL_FLAG_SET),
                    G.LAST_MODIFY_DATE 
            FROM GAME G
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN VENDOR V ON G.VENDOR_ID = V.ID
            INNER JOIN GAME_PKG GP ON GP.GAME_ID = G.ID
            WHERE G.DATA_TYPE & 32 = 32 
            AND G.STATUS > 0 
            AND G.EXACT_RELEASE_DATE IS NOT NULL 
            GROUP BY G.ID
        '''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(curSql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    gameSoftwareTrailerList = []
    if not allRows:
        return gameSoftwareTrailerList
    for row in allRows:
        resourceInfo = {}
        resourceInfo['RESOURCE_ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ENNAME'] = row[2]
        resourceInfo['PINYIN'] = ''
        resourceInfo['CATEGORY_ID'] = row[3]
        resourceInfo['CATEGORY_NAME'] = row[14]
        resourceInfo['RESOURCE_TYPE'] = row[21]
        resourceInfo['COMMENT'] = row[4]
        resourceInfo['HOT_CNT'] = row[5]
        resourceInfo['STARTS'] = row[6]
        resourceInfo['RESOURCE_PUBLISH_DATE'] = row[11]
        resourceInfo['ICON'] = row[7]
        resourceInfo['BANNER'] = row[15]
        resourceInfo['GOOD_RATING_CNT'] = row[13]
        resourceInfo['LATEST_VERSION_NAME'] = row[8]
        resourceInfo['CREATED_DATE'] = row[12]
        resourceInfo['DATA_TYPE'] = row[9]
        resourceInfo['LANGUAGE_TYPE'] = row[10]
        resourceInfo['COPYRIGHT_TYPE'] = row[16]
        resourceInfo['SCORE'] = row[17]
        resourceInfo['OUTLINE'] = row[18]
        resourceInfo['DESCRIPTION'] = row[19]
        resourceInfo['IMAGE_410X250'] = row[20]
        resourceInfo['EXACT_RELEASE_DATE'] = row[22]
        resourceInfo['ESTIMATE_RELEASE_DATE'] = row[23]
        resourceInfo['VENDOR_NAME'] = row[24]
        resourceInfo['VENDOR_EN_NAME'] = row[25]
        resourceInfo['PKG_CHANNEL_FLAG_SET'] = row[26]
        resourceInfo['LAST_MODIFY_DATE'] = row[27]
        gameSoftwareTrailerList.append(resourceInfo)

    return gameSoftwareTrailerList

#��ȡ����Ԥ���б�
def getTrailerListOfNetgame():
    sql = '''SELECT C.ID,
                C.NAME,
                C.PINYIN,
                C.HDICON,
                C.TAG_NAMES,
                C.STARS,
                C.HOT_CNT,
                C.CREATED_DATE,
                C.LAST_UPDATE_DATE,
                C.BANNER,
                C.TAG_IDS,
                C.SCORE,
                CASE
                    WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                    ELSE C.OUTLET_LINE
                END AS OUTLINE,
                C.DESCRIPTION,
                NM.ACTIVITY_TIME,
                C.CP_NAME
            FROM NETGAME_MEMORABILIA_UNPUBLISH NM 
            INNER JOIN NETGAME_CHANNEL C ON C.ID = NM.CHANNEL_ID
            LEFT JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            LEFT JOIN NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            WHERE (C.NETGAME_SYNC_STATUS = 1 || C.NETGAME_SYNC_STATUS = 2)
            AND C.STATUS = 1
            AND GP.NETGAME_SYNC_STATUS IS NULL
            GROUP BY C.ID
        '''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(curSql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    netgameTrailerList = []
    if not allRows:
        return netgameTrailerList
    for row in allRows:
        resourceInfo = {}
        resourceInfo['RESOURCE_ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ENNAME'] = ''
        resourceInfo['PINYIN'] = row[2]
        resourceInfo['CATEGORY_ID'] = row[10]
        resourceInfo['CATEGORY_NAME'] = row[4]
        resourceInfo['RESOURCE_TYPE'] = 5
        resourceInfo['COMMENT'] = None
        resourceInfo['HOT_CNT'] = row[6]
        resourceInfo['STARTS'] = row[5]
        resourceInfo['RESOURCE_PUBLISH_DATE'] = row[8]
        resourceInfo['ICON'] = row[3]
        resourceInfo['BANNER'] = row[9]
        resourceInfo['GOOD_RATING_CNT'] = None
        resourceInfo['LATEST_VERSION_NAME'] = None
        resourceInfo['CREATED_DATE'] = row[7]
        resourceInfo['DATA_TYPE'] = 0
        resourceInfo['LANGUAGE_TYPE'] = 7 #����Ĭ��֧����-2��Ӣ-1����-4
        resourceInfo['COPYRIGHT_TYPE'] = None
        resourceInfo['SCORE'] = row[11]
        resourceInfo['OUTLINE'] = row[12]
        resourceInfo['DESCRIPTION'] = row[13]
        resourceInfo['IMAGE_410X250'] = None
        resourceInfo['EXACT_RELEASE_DATE'] = row[14]
        resourceInfo['ESTIMATE_RELEASE_DATE'] = None
        resourceInfo['VENDOR_NAME'] = row[15]
        resourceInfo['VENDOR_EN_NAME'] = ''
        resourceInfo['PKG_CHANNEL_FLAG_SET'] = 511
        resourceInfo['LAST_MODIFY_DATE'] = row[8]
        netgameTrailerList.append(resourceInfo)
        
    return netgameTrailerList

#����й��λ���롢�������б�
def getSortList():
    #��ȡ��Ϸ�����Ԥ���б�
    gameSoftwareTrailerList = getTrailerListOfGameSoftware()
    
    #��ȡ����Ԥ���б�
    netgameTrailerList = getTrailerListOfNetgame()
    
    #��ȡ ��Ʊ ��Ԥ��
    bounceList = []
    for trailerTO in gameSoftwareTrailerList[:]:
        if trailerTO['EXACT_RELEASE_DATE'] < today:
            bounceList.append(trailerTO)
            gameSoftwareTrailerList.remove(trailerTO)
    for trailerTO in netgameTrailerList[:]:
        if trailerTO['EXACT_RELEASE_DATE'] < today:
            bounceList.append(trailerTO)
            netgameTrailerList.remove(trailerTO)
    
    #����
    sortList = []
    sortList.extend(gameSoftwareTrailerList)
    sortList.extend(netgameTrailerList)
    sortList.sort(key=lambda x:x['EXACT_RELEASE_DATE'])
    
    #��ƱԤ�棬��Ҫ�ŵ�����Ԥ���б��ĩβ
    sortList.extend(bounceList)
    
    return sortList

#��ȡ�������ı���
def getTableNameForInsert():
    tableName = ''
    sql = "select TABLE_NAME from GAME_LIST_TABLE_STATUS where TYPE = '%s'" % TRAILER_LIST_TYPE
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows and (len(rows) != 0) and (rows[0][0]):
        tableName = rows[0][0]

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
    cursor.execute(sql)
    conn.commit()

#�����������б���Ϣ
def insertResourceInfos(tableName, sortList):
    sql = ''
    seq = 1
    if not sortList: return
    datalist = []

    for resourceInfo in sortList:
        sql = "INSERT INTO %s " % tableName
        sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, VENDOR_NAME, VENDOR_EN_NAME, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, GOOD_RATING_CNT, LATEST_VERSION_NAME, CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, COPYRIGHT_TYPE,SCORE,OUTLINE,DESCRIPTION,IMAGE_410X250,RELEASE_DATE,PKG_CHANNEL_FLAG_SET,LAST_MODIFY_DATE,EXACT_RELEASE_DATE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #Ԥ�����ʾʱ�䴦��
        estimateReleaseDate = resourceInfo['ESTIMATE_RELEASE_DATE']
        exactReleaseDate = resourceInfo['EXACT_RELEASE_DATE']
        if exactReleaseDate < today:
            releaseDate = u'��Ʊ'
        elif (estimateReleaseDate != None) and (estimateReleaseDate.strip() != ''):
            releaseDate = estimateReleaseDate.strip()
        else:
            releaseDate = exactReleaseDate
        #����
        datalist.append((seq,
                         resourceInfo['RESOURCE_ID'],
                         resourceInfo['NAME'],
                         resourceInfo['ENNAME'],
                         resourceInfo['PINYIN'],
                         resourceInfo['CATEGORY_ID'],
                         resourceInfo['CATEGORY_NAME'],
                         resourceInfo['VENDOR_NAME'],
                         resourceInfo['VENDOR_EN_NAME'],
                         resourceInfo['RESOURCE_TYPE'],
                         resourceInfo['COMMENT'],
                         resourceInfo['HOT_CNT'],
                         resourceInfo['STARTS'],
                         resourceInfo['RESOURCE_PUBLISH_DATE'],
                         resourceInfo['ICON'],
                         resourceInfo['BANNER'],
                         resourceInfo['GOOD_RATING_CNT'],
                         resourceInfo['LATEST_VERSION_NAME'],
                         resourceInfo['CREATED_DATE'],
                         resourceInfo['DATA_TYPE'],
                         resourceInfo['LANGUAGE_TYPE'],
                         resourceInfo['COPYRIGHT_TYPE'],
                         resourceInfo['SCORE'],
                         resourceInfo['OUTLINE'],
                         resourceInfo['DESCRIPTION'],
                         resourceInfo['IMAGE_410X250'],
                         releaseDate,
                         resourceInfo['PKG_CHANNEL_FLAG_SET'],
                         resourceInfo['LAST_MODIFY_DATE'],
                         resourceInfo['EXACT_RELEASE_DATE']))
        seq += 1
        if len(datalist)>=1000:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []
    if datalist:
        cursor.executemany(sql, tuple(datalist))
        conn.commit()
        datalist = []

#���±������������б�ı���
def updateTableName(tableName):
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),TRAILER_LIST_TYPE)
    cursor.execute(sql)
    conn.commit()

#���������б���Ϣ���뵽���ݿ���
def insertSortList(sortList):
    #��ȡ����������
    tableName = getTableNameForInsert()
    print 'tableName: %s' % tableName

    #��մ�������
    clearTable(tableName)

    #��������
    print 'start insert'
    insertResourceInfos(tableName, sortList)
    print 'end insert'

    #���±������������б�ı���
    updateTableName(tableName)

###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
       
        #��ȡ�������б���Ϣ
        sortList = getSortList()

        #�����������б���Ϣ�����ݿ���
        insertSortList(sortList)
        
        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        maxTime = datetime.timedelta(minutes=15)
        if spentTime > maxTime:
             #�ű����г�ʱ�����澯��Ϣ�����䣬�п������ݿ����ܻ���~~~
             sendmail('webmaster@downjoy.com', MONITOR_MAIL, "�ű���ʱ", "android ��������Ԥ���б�--�ű���ʱ,211.147.5.167_usr_local_bin_advertiseListOfTrailer.py")

    except Exception, ex:
        #print(sys.exc_info()[0],sys.exc_info()[1])
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), "android ��������Ԥ���б����,211.147.5.167_usr_local_bin_advertiseListOfTrailer.py")
        raise Exception

    finally:
        cursor.close()
        conn.close()
