#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2013/11/21 $"

import MySQLdb
import traceback
import datetime
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import smtplib
import httplib


#�쳣�ʼ�������
MONITOR_MAIL=['shan.liang@downjoy.com']

#���ݿ�����
conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game", use_unicode=True, charset='utf8')
cursor = conn.cursor()

#��ʶ��ͬ�����б�
GAME_HOTEST_LIST = 1            #��Ϸ�����б�
SOFTWARE_HOTEST_LIST = 2        #��������б�
NETGAME_HOTEST_LIST = 3         #���������б�
GAME_FIVESTAR_LIST = 4          #��Ϸ�����б�
SOFTWARE_FIVESTAR_LIST = 5      #��������б�
NETGAME_FIVESTAR_LIST = 6       #���������б�
GAME_NEWEST_LIST = 7            #��Ϸ�����б�
SOFTWARE_NEWEST_LIST = 8        #��������б�
NETGAME_NEWEST_LIST = 9         #���������б�
GAME_ORIGINAL_LIST = 9999       #��Ϸԭʼ�б�
SOFTWARE_ORIGINAL_LIST = 9998   #���ԭʼ�б�
NETGAME_ORIGINAL_LIST = 9997    #����ԭʼ�б�
TYPE_DIC = {GAME_HOTEST_LIST:'WEB_GAME_HOTEST_LIST', GAME_FIVESTAR_LIST:'WEB_GAME_5STARS_LIST', GAME_NEWEST_LIST:'WEB_GAME_NEWEST_LIST', GAME_ORIGINAL_LIST:'WEB_GAME_ORIGINAL_LIST', SOFTWARE_HOTEST_LIST:'WEB_SOFTWARE_HOTEST_LIST', SOFTWARE_FIVESTAR_LIST:'WEB_SOFTWARE_5STARS_LIST', SOFTWARE_NEWEST_LIST:'WEB_SOFTWARE_NEWEST_LIST', SOFTWARE_ORIGINAL_LIST:'WEB_SOFTWARE_ORIGINAL_LIST', NETGAME_HOTEST_LIST:'WEB_NETGAME_HOTEST_LIST', NETGAME_FIVESTAR_LIST:'WEB_NETGAME_5STARS_LIST', NETGAME_NEWEST_LIST:'WEB_NETGAME_NEWEST_LIST', NETGAME_ORIGINAL_LIST:'WEB_NETGAME_ORIGINAL_LIST'}


#��ʶ��ͬ��Դ���
RESOURCE_TYPE_GAME = 1      #��Ϸ
RESOURCE_TYPE_SOFTWARE = 2  #���
RESOURCE_TYPE_NETGAME = 5   #����

#��ʶ��ͬ�����б����Դ���ͣ�resource_type��
LIST_RESOURCE_TYPE_DIC = {GAME_HOTEST_LIST:RESOURCE_TYPE_GAME, GAME_FIVESTAR_LIST:RESOURCE_TYPE_GAME, GAME_NEWEST_LIST:RESOURCE_TYPE_GAME, GAME_ORIGINAL_LIST:RESOURCE_TYPE_GAME, SOFTWARE_HOTEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_FIVESTAR_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_NEWEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_ORIGINAL_LIST:RESOURCE_TYPE_SOFTWARE, NETGAME_HOTEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_FIVESTAR_LIST:RESOURCE_TYPE_NETGAME, NETGAME_NEWEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_ORIGINAL_LIST:RESOURCE_TYPE_NETGAME}

#����Ҫ������λ���б�
NOT_ADVERTISE_LIST = [GAME_ORIGINAL_LIST, SOFTWARE_ORIGINAL_LIST, NETGAME_ORIGINAL_LIST]

#web��վ������IP:port
WEB_IP_LIST = ['192.168.0.211:8080', '192.168.0.155:8080', '192.168.0.167:8080', '192.168.0.174:8080']
DIGUA_IP_LIST = ['192.168.0.211:7011', '192.168.0.155:7011', '192.168.0.167:7011', '192.168.0.174:7011']

#ȫ�ֱ���
TAG_DIC = {} #��ǩ
ORG_GAME_LIST = [] #ԭʼ��Ϸ�б�
ORG_SOFTWARE_LIST = [] #ԭʼ����б�
ORG_NETGAME_LIST = [] #ԭʼ�����б�
SPECIAL_CHANNEL_DIC = {} #�ض��ĵ���ר����Ϣ��dataType, tipType, languageType��

#�����ʼ�
def sendmail(From, To, msgBody, title):
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","bourne@8.3")
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

#����web����ӿڣ�����web����Ķ��������е��б�״̬��Ϣ
def cleanListTableStatusCache():
    #���web����
    for ip in WEB_IP_LIST:
        url = "/djweb/clean/cleanTableStatus"
        conn = httplib.HTTPConnection(ip)
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()

    return
    
#��ʼ����ǩ��Ϣ
def initTag():
    global TAG_DIC
    sql = '''SELECT T.ID, T.NAME FROM CLIENT_TAG T WHERE T.STATUS = 1'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows and (len(rows) > 0) and rows[0][0]:
        for row in rows:
            TAG_DIC[row[1]] = row[0]
    
#��ȡ��Ϸ�б���Ϣ����publishDate����
def initOrgGameList():
    #�����Ϸ������Ϣ
    global ORG_GAME_LIST
    sql = '''SELECT G.CHANNEL_ID,
                    G.NAME,
                    G.EN_NAME,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.SCORE,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.ICON,
                    G.BANNER,
                    G.IMAGE_410X250,
                    G.COLLECT_CNT,
                    G.GAME_CATEGORY_ID,
                    C.NAME AS GAME_CATEGORY_NAME,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TAGS,
                    G.LATEST_VERSION_NAME,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE,
                    P.FILE_SIZE,
                    P.CREATED_DATE AS P_CREATED_DATE,
                    P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET,
                    G.VENDOR_ID,
                    G.DATA_TYPE,
                    G.TIP_TYPE,
                    G.LANGUAGE_TYPE,
                    G.STATUS 
            FROM GAME G 
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 1
            AND G.STATUS = 1
            AND G.CHANNEL_ID = G.ID 
            AND P.ID = (SELECT P1.ID FROM GAME_PKG P1 WHERE P1.GAME_ID = G.ID ORDER BY P1.CREATED_DATE DESC, P1.FILE_SIZE DESC LIMIT 1)
            AND P.STATUS = 1
            ORDER BY G.PUBLISH_DATE DESC 
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        #��WEB��WAP������û��ͬ���õ���Ϸ���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
        if row[21] & 1 == 0 and row[21] & 2 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setChannelId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setHotCnt(row[3])
        channelTO.setStars(row[4])
        channelTO.setScore(row[5])
        channelTO.setOutline(row[6])
        channelTO.setDescription(row[7])
        channelTO.setIcon(row[8])
        channelTO.setBanner(row[9])
        channelTO.setImage_410X250(row[10])
        if row[11]:
            channelTO.setCollectCnt(row[11])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setCategoryId(row[12])
        channelTO.setCategoryName(row[13])
        channelTO.setCategoryTabFlagSet(row[14])
        channelTO.setTagIds(getTagIdsByNames(row[15]))
        channelTO.setLastestVerName(row[16])
        channelTO.setPublishDate(row[17])
        channelTO.setCreatedDate(row[18])
        channelTO.setPkgFileSize(row[19])
        channelTO.setPkgCreatedDate(row[20])
        channelTO.setPkgChannelFlagSet(row[21])
        channelTO.setVendorId(row[22])
        channelTO.setResourceType(1)
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        if channelTO.getChannelId() in SPECIAL_CHANNEL_DIC:
            specialChannelTO = SPECIAL_CHANNEL_DIC[channelTO.getChannelId()]
            channelTO.setDataType(specialChannelTO.getDataType())
            channelTO.setTipType(specialChannelTO.getTipType())
            channelTO.setLanguageType(specialChannelTO.getLanguageType())
        else:
            channelTO.setDataType(row[23])
            channelTO.setTipType(row[24])
            channelTO.setLanguageType(row[25])
        channelTO.setStatus(row[26])
        ORG_GAME_LIST.append(channelTO)

#��ȡ�����Ϣ����publishDate����
def initOrgSoftwareList():
    #������������Ϣ
    global ORG_SOFTWARE_LIST
    sql = '''SELECT G.CHANNEL_ID,
                    G.NAME,
                    G.EN_NAME,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.SCORE,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.ICON,
                    G.BANNER,
                    G.IMAGE_410X250,
                    G.COLLECT_CNT,
                    G.GAME_CATEGORY_ID,
                    C.NAME AS GAME_CATEGORY_NAME,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TAGS,
                    G.LATEST_VERSION_NAME,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE,
                    P.FILE_SIZE,
                    P.CREATED_DATE AS P_CREATED_DATE,
                    P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET,
                    G.VENDOR_ID,
                    G.DATA_TYPE,
                    G.TIP_TYPE,
                    G.LANGUAGE_TYPE,
                    G.STATUS 
            FROM GAME G 
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 2
            AND G.STATUS = 1
            AND G.CHANNEL_ID = G.ID 
            AND P.ID = (SELECT P1.ID FROM GAME_PKG P1 WHERE P1.GAME_ID = G.ID ORDER BY P1.CREATED_DATE DESC, P1.FILE_SIZE DESC LIMIT 1)
            AND P.STATUS = 1
            ORDER BY G.PUBLISH_DATE DESC 
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        #��WEB��WAP������û��ͬ���õ���Ϸ���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
        if row[21] & 1 == 0 and row[21] & 2 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setChannelId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setHotCnt(row[3])
        channelTO.setStars(row[4])
        channelTO.setScore(row[5])
        channelTO.setOutline(row[6])
        channelTO.setDescription(row[7])
        channelTO.setIcon(row[8])
        channelTO.setBanner(row[9])
        channelTO.setImage_410X250(row[10])
        if row[11]:
            channelTO.setCollectCnt(row[11])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setCategoryId(row[12])
        channelTO.setCategoryName(row[13])
        channelTO.setCategoryTabFlagSet(row[14])
        channelTO.setTagIds(getTagIdsByNames(row[15]))
        channelTO.setLastestVerName(row[16])
        channelTO.setPublishDate(row[17])
        channelTO.setCreatedDate(row[18])
        channelTO.setPkgFileSize(row[19])
        channelTO.setPkgCreatedDate(row[20])
        channelTO.setPkgChannelFlagSet(row[21])
        channelTO.setVendorId(row[22])
        channelTO.setResourceType(2)
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        if channelTO.getChannelId() in SPECIAL_CHANNEL_DIC:
            specialChannelTO = SPECIAL_CHANNEL_DIC[channelTO.getChannelId()]
            channelTO.setDataType(specialChannelTO.getDataType())
            channelTO.setTipType(specialChannelTO.getTipType())
            channelTO.setLanguageType(specialChannelTO.getLanguageType())
        else:
            channelTO.setDataType(row[23])
            channelTO.setTipType(row[24])
            channelTO.setLanguageType(row[25])
        channelTO.setStatus(row[26])
        ORG_SOFTWARE_LIST.append(channelTO)
        
#��ȡ������Ϣ
def initOrgNetgameList():
    #������������Ϣ
    global ORG_NETGAME_LIST
    sql = '''select C.ID,
                    C.NAME,
                    C.PINYIN,
                    C.HOT_CNT,
                    C.STARS,
                    C.SCORE,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION,
                    C.HDICON,
                    C.BANNER,
                    C.TAG_IDS,
                    C.TAG_NAMES,
                    C.LAST_UPDATE_DATE,
                    C.CREATED_DATE,
                    G.LAST_VERSION_NUM,
                    GP.FILE_SIZE,
                    MAX(GP.CREATED_DATE) AS P_CREATED_DATE,
                    C.CP_ID, 
                    C.COLLECT_CNT,
                    C.OPERATION_STATUS 
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            where C.NETGAME_SYNC_STATUS > 0 
            and C.STATUS = 1
            and (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS > 0)
            and (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS > 0)
            group by C.ID
            order by C.LAST_UPDATE_DATE desc
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        channelTO = ChannelTO()
        channelTO.setChannelId(row[0])
        channelTO.setName(row[1])
        channelTO.setPinyin(row[2])
        channelTO.setHotCnt(row[3])
        channelTO.setStars(row[4])
        channelTO.setScore(row[5])
        channelTO.setOutline(row[6])
        channelTO.setDescription(row[7])
        channelTO.setIcon(row[8])
        channelTO.setBanner(row[9])
        channelTO.setCategoryId(row[10])
        channelTO.setCategoryName(row[11])
        channelTO.setPublishDate(row[12])
        channelTO.setCreatedDate(row[13])
        channelTO.setLastestVerName(row[14])
        channelTO.setPkgFileSize(row[15])
        channelTO.setPkgCreatedDate(row[16])
        channelTO.setVendorId(row[17])
        if row[18]:
            channelTO.setCollectCnt(row[18])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setStatus(row[19])
        channelTO.setDataType(0)
        channelTO.setLanguageType(7) #����Ĭ��Ϊ֧����-2��Ӣ-1����-4
        channelTO.setResourceType(5)
        channelTO.setPkgChannelFlagSet(511) #����Ĭ��֧������
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        ORG_NETGAME_LIST.append(channelTO)
    
#��ȡר���ض���Ϣ��dataType, tipType��
def initChannelSpecialInfo():
    global SPECIAL_CHANNEL_DIC
    sql = '''SELECT G.CHANNEL_ID, BIT_OR(G.DATA_TYPE), BIT_OR(G.TIP_TYPE), BIT_OR(G.LANGUAGE_TYPE)
            FROM GAME G 
            WHERE G.STATUS > 0
            GROUP BY G.CHANNEL_ID
            HAVING COUNT(1) > 1
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        channelTO = ChannelTO()
        channelTO.setDataType(row[1])
        channelTO.setTipType(row[2])
        channelTO.setLanguageType(row[3])
        SPECIAL_CHANNEL_DIC[row[0]] = channelTO
        
#ת����ǩ���Ƶ���ǩID
def getTagIdsByNames(tagNames):
    if not tagNames:
        return None
        
    tagIds = ''
    tagNameArr = tagNames.strip().split(',')
    for tagName in tagNameArr:
        if tagName in TAG_DIC:
            tagId = TAG_DIC[tagName]
            tagIds = tagIds + ',' + str(tagId)
    
    if len(tagIds) > 0:
        tagIds = tagIds + ','
        
    return tagIds
   
#��ȡ����С��Χ
def getFileSizeScope(fileSize):
    if fileSize <= 50 * 1024 * 1024:
        return 1
    elif fileSize <= 100 * 1024 * 1024:
        return 2
    elif fileSize <= 300 * 1024 * 1024:
        return 3
    elif fileSize <= 500 * 1024 * 1024:
        return 4
    elif fileSize <= 1024 * 1024 * 1024:
        return 5
    else:
        return 6
        
#��ȡ�������
def getOnlineYear(createdDate):
    sysYear = datetime.date.today().year
    onlineYear = createdDate.year
    
    if onlineYear <= sysYear - 4: #���Ϊ���굹��4��֮������Ϊ-1����ʾ�����硯
        onlineYear = -1
    else:
        onlineYear = sysYear - onlineYear + 1
    
    return onlineYear
  
#��ȡ���ݿ��е��б�״̬��Ϣ
def getTableName(sortType):
    tableName = ''
    type = TYPE_DIC[sortType]
    sql = "select TABLE_NAME from GAME_LIST_TABLE_STATUS where TYPE = '%s'" % type
    cursor.execute(sql)
    rows = cursor.fetchall()

    if not rows or (len(rows) == 0) or (not rows[0][0]):
        return tableName
    else:
        tableName = rows[0][0]

    return tableName

#�����Դ��Ϣ��ϸ��Ϣ
def getResourceInfo(channelId, resourceType):
    channelTO = None
    if (resourceType == RESOURCE_TYPE_GAME) or (resourceType == RESOURCE_TYPE_SOFTWARE):
        sql = '''SELECT G.CHANNEL_ID,
                    G.NAME,
                    G.EN_NAME,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.SCORE,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.ICON,
                    G.BANNER,
                    G.IMAGE_410X250,
                    G.COLLECT_CNT,
                    G.GAME_CATEGORY_ID,
                    C.NAME AS GAME_CATEGORY_NAME,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TAGS,
                    G.LATEST_VERSION_NAME,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE,
                    P.FILE_SIZE,
                    P.CREATED_DATE AS P_CREATED_DATE,
                    P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET,
                    G.VENDOR_ID,
                    G.DATA_TYPE,
                    G.TIP_TYPE,
                    G.LANGUAGE_TYPE,
                    G.STATUS 
            FROM GAME G 
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.CHANNEL_ID = %d
            AND G.RESOURCE_TYPE = %d
            AND G.STATUS = 1
            AND G.CHANNEL_ID = G.ID 
            AND P.ID = (SELECT P1.ID FROM GAME_PKG P1 WHERE P1.GAME_ID = G.ID ORDER BY P1.CREATED_DATE DESC, P1.FILE_SIZE DESC LIMIT 1)
            AND P.STATUS = 1''' % (channelId, resourceType)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows and (len(rows) > 0) and rows[0][0]:
            #��WEB��WAP������û��ͬ���õ���Ϸ���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
            row = rows[0]
            if row[21] & 1 == 0 and row[21] & 2 == 0:
                return None
            channelTO = ChannelTO()
            channelTO.setChannelId(row[0])
            channelTO.setName(row[1])
            channelTO.setEnName(row[2])
            channelTO.setHotCnt(row[3])
            channelTO.setStars(row[4])
            channelTO.setScore(row[5])
            channelTO.setOutline(row[6])
            channelTO.setDescription(row[7])
            channelTO.setIcon(row[8])
            channelTO.setBanner(row[9])
            channelTO.setImage_410X250(row[10])
            if row[11]:
                channelTO.setCollectCnt(row[11])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setCategoryId(row[12])
            channelTO.setCategoryName(row[13])
            channelTO.setCategoryTabFlagSet(row[14])
            channelTO.setTagIds(getTagIdsByNames(row[15]))
            channelTO.setLastestVerName(row[16])
            channelTO.setPublishDate(row[17])
            channelTO.setCreatedDate(row[18])
            channelTO.setPkgFileSize(row[19])
            channelTO.setPkgCreatedDate(row[20])
            channelTO.setPkgChannelFlagSet(row[21])
            channelTO.setVendorId(row[22])
            channelTO.setResourceType(resourceType)
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            if channelTO.getChannelId() in SPECIAL_CHANNEL_DIC:
               specialChannelTO = SPECIAL_CHANNEL_DIC[channelTO.getChannelId()]
               channelTO.setDataType(specialChannelTO.getDataType() | 16) #16��ʾ����Դ��һ�����λ������ǰ̨�Ǳ��չʾ
               channelTO.setTipType(specialChannelTO.getTipType())
               channelTO.setLanguageType(specialChannelTO.getLanguageType())
            else:
                channelTO.setDataType(row[23] | 16) #16��ʾ����Դ��һ�����λ������ǰ̨�Ǳ��չʾ
                channelTO.setTipType(row[24])
                channelTO.setLanguageType(row[25])
            channelTO.setStatus(row[26])
            
    elif resourceType == RESOURCE_TYPE_NETGAME:
        sql = '''select C.ID,
                        C.NAME,
                        C.PINYIN,
                        C.HOT_CNT,
                        C.STARS,
                        C.SCORE,
                        CASE
                            WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                            ELSE C.OUTLET_LINE
                        END AS OUTLINE,
                        C.DESCRIPTION,
                        C.HDICON,
                        C.BANNER,
                        C.TAG_IDS,
                        C.TAG_NAMES,
                        C.LAST_UPDATE_DATE,
                        C.CREATED_DATE,
                        G.LAST_VERSION_NUM,
                        GP.FILE_SIZE,
                        MAX(GP.CREATED_DATE) AS P_CREATED_DATE,
                        C.CP_ID, 
                        C.COLLECT_CNT,
                        C.OPERATION_STATUS 
                FROM NETGAME_CHANNEL C
                LEFT JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID 
                LEFT JOIN NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID 
                WHERE C.ID = %d
                AND C.NETGAME_SYNC_STATUS > 0
                AND C.STATUS = 1
                AND (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS > 0)
                AND (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS > 0)''' % channelId
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows and (len(rows) > 0) and rows[0][0]:
            channelTO = ChannelTO()
            row = rows[0]
            channelTO.setChannelId(row[0])
            channelTO.setName(row[1])
            channelTO.setPinyin(row[2])
            channelTO.setHotCnt(row[3])
            channelTO.setStars(row[4])
            channelTO.setScore(row[5])
            channelTO.setOutline(row[6])
            channelTO.setDescription(row[7])
            channelTO.setIcon(row[8])
            channelTO.setBanner(row[9])
            channelTO.setCategoryId(row[10])
            channelTO.setCategoryName(row[11])
            channelTO.setPublishDate(row[12])
            channelTO.setCreatedDate(row[13])
            channelTO.setLastestVerName(row[14])
            channelTO.setPkgFileSize(row[15])
            channelTO.setPkgCreatedDate(row[16])
            channelTO.setVendorId(row[17])
            if row[18]:
                channelTO.setCollectCnt(row[18])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setStatus(row[19])
            channelTO.setDataType(16)#16��ʾ����Դ��һ�����λ������ǰ̨�Ǳ��չʾ
            channelTO.setLanguageType(7) #����Ĭ��Ϊ֧����-2��Ӣ-1����-4
            channelTO.setResourceType(5)
            channelTO.setPkgChannelFlagSet(511) #����Ĭ��֧������
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            
    return channelTO

#�����Ӫ�Զ�������б�ҳ�е���Դ����Ϸ/���/���Σ�������Ϣ
def getCustomSortDict(sortType):
    sql = '''SELECT CHANNEL_ID,
                    RESOURCE_TYPE,
                    POSITION
             FROM WEB_LIST_CUSTOM_ADV
             WHERE LIST_TYPE = %d
             ORDER BY POSITION ASC''' % (sortType)
    cursor.execute(sql)
    rows = cursor.fetchall()

    customSortDict = {}
    if not rows: return customSortDict
    for row in rows:
        position = int(row[2])
        # ҵ����������б���ֻ�ܲ������ι��λ����Ϸ/������˵�
        if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_NETGAME) and (row[1] != RESOURCE_TYPE_NETGAME):
            continue

        #��ȡ���λ��Դ��Ϣ
        resourceInfo = getResourceInfo(row[0], row[1])
        if not resourceInfo:
            continue
        customSortDict[position] = resourceInfo

    return customSortDict

#�����Ϸԭʼ������б�(exclusion_ids:�����Ѿ��ǹ��λ����Ҫ�ų���ID)
def getOriginalGameSortList(sortType, exclusion_ids):
    orgSortList = []
    if sortType == GAME_HOTEST_LIST:  #����
        for channelTO in ORG_GAME_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
        orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == GAME_NEWEST_LIST:  #����
        for channelTO in ORG_GAME_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    elif sortType == GAME_ORIGINAL_LIST: #ԭʼ
        orgSortList = ORG_GAME_LIST
    elif sortType == GAME_FIVESTAR_LIST: #����
        for channelTO in ORG_GAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    
    return orgSortList
    
 #������ԭʼ������б�
def getOriginalSoftwareSortList(sortType, exclusion_ids):
    orgSortList = []
    if sortType == SOFTWARE_HOTEST_LIST:  #����
        for channelTO in ORG_SOFTWARE_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
        orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == SOFTWARE_NEWEST_LIST:  #����
        for channelTO in ORG_SOFTWARE_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    elif sortType == SOFTWARE_ORIGINAL_LIST: #ԭʼ
        orgSortList = ORG_SOFTWARE_LIST
    elif sortType == SOFTWARE_FIVESTAR_LIST: #����
        for channelTO in ORG_SOFTWARE_LIST:
            if channelTO.getStars() != 5:
                continue
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    
    return orgSortList

#�������ԭʼ������б�
def getOriginalNetgameSortList(sortType, exclusion_ids):
    orgSortList = []
    if sortType == NETGAME_HOTEST_LIST:  #����
        for channelTO in ORG_NETGAME_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
        orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == NETGAME_NEWEST_LIST:  #����
        for channelTO in ORG_NETGAME_LIST:
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    elif sortType == NETGAME_ORIGINAL_LIST: #ԭʼ
        orgSortList = ORG_NETGAME_LIST
    elif sortType == NETGAME_FIVESTAR_LIST: #����
        for channelTO in ORG_NETGAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if exclusion_ids.find(',' + str(channelTO.getChannelId()) + ',') != -1:
                continue
            orgSortList.append(channelTO)
    
    return orgSortList

#����й��λ���롢�������б�
def getAdvertiseSortList(sortType):
    #��Ӫ�Զ�������
    customSortDict = getCustomSortDict(sortType)
    print 'custom rows len: %d' % (len(customSortDict))

    #��ȡ��Ҫ��ԭʼ������ȥ������ԴID
    exclusion_ids = ','
    for channelTO in customSortDict.values():
        if channelTO.getResourceType() == LIST_RESOURCE_TYPE_DIC[sortType]:
            exclusion_ids = exclusion_ids + str(channelTO.getChannelId()) + ','
    print exclusion_ids

    #ԭʼ����
    sortList = getOriginalSortList(sortType, exclusion_ids)

    #�������������
    keys = customSortDict.keys()
    keys.sort()
    for position in keys:
        if (position < 1) or (position > len(sortList)): continue
        sortList.insert(position - 1, customSortDict[position])
    print 'final rows len: %d' % len(sortList)

    return sortList

#��ȡԭʼ�����б�
def getOriginalSortList(sortType, exclusion_ids = None):
    originalSortList = []
    if LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_GAME:
        originalSortList = getOriginalGameSortList(sortType, exclusion_ids)
    elif LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_SOFTWARE:
        originalSortList = getOriginalSoftwareSortList(sortType, exclusion_ids)
    else:
        originalSortList = getOriginalNetgameSortList(sortType, exclusion_ids)
    print 'orignal rows len: %d' % (len(originalSortList))

    return originalSortList

#�����������õ��б�
def getSortList(sortType):
    if sortType in NOT_ADVERTISE_LIST:
        return getOriginalSortList(sortType)
    else:
        return getAdvertiseSortList(sortType)

#��ȡ�������ı���
def getTableNameForInsert(sortType):
    tableName = getTableName(sortType)
    print tableName

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

    for channelTO in sortList:
        sql = "INSERT INTO %s " % tableName
        sql += "(ID, CHANNEL_ID, NAME, ENNAME, PINYIN, RESOURCE_TYPE, HOT_CNT, STARS, SCORE, OUTLINE, DESCRIPTION, ICON, BANNER, IMAGE_410X250, COLLECT_CNT, DATA_TYPE, TIP_TYPE, CATEGORY_ID, CATEGORY_NAME, CATEGORY_TAB_FLAG_SET, TAG_IDS, LATEST_VERSION_NAME, PUBLISH_DATE, CREATED_DATE, PKG_FILE_SIZE, PKG_CREATED_DATE, PKG_CHANNEL_FLAG_SET, PKG_FILE_SIZE_SCOPE, ONLINE_YEAR, VENDOR_ID, LANGUAGE_TYPE, STATUS) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        datalist.append((seq,
                         channelTO.getChannelId(),
                         channelTO.getName(),
                         channelTO.getEnName(),
                         channelTO.getPinyin(),
                         channelTO.getResourceType(),
                         channelTO.getHotCnt(),
                         channelTO.getStars(),
                         channelTO.getScore(),
                         channelTO.getOutline(),
                         channelTO.getDescription(),
                         channelTO.getIcon(),
                         channelTO.getBanner(),
                         channelTO.getImage_410X250(),
                         channelTO.getCollectCnt(),
                         channelTO.getDataType(),
                         channelTO.getTipType(),
                         channelTO.getCategoryId(),
                         channelTO.getCategoryName(),
                         channelTO.getCategoryTabFlagSet(),
                         channelTO.getTagIds(),
                         channelTO.getLastestVerName(),
                         channelTO.getPublishDate(),
                         channelTO.getCreatedDate(),
                         channelTO.getPkgFileSize(),
                         channelTO.getPkgCreatedDate(),
                         channelTO.getPkgChannelFlagSet(),
                         channelTO.getPkgFileSizeScope(),
                         channelTO.getOnlineYear(),
                         channelTO.getVendorId(),
                         channelTO.getLanguageType(),
                         channelTO.getStatus()))
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
def updateTableName(sortType, tableName):
    type2 = TYPE_DIC[sortType]
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),type2)
    cursor.execute(sql)
    conn.commit()

#�����������б���Ϣ�����ݿ���
def insertSortList(sortType, sortList):
    #��ȡ����������
    tableName = ''
    tableName = getTableNameForInsert(sortType)
    print 'tableName: %s' % tableName

    #��մ�������
    clearTable(tableName)

    #��������
    print 'start insert'
    insertResourceInfos(tableName, sortList)
    print 'end insert'

    #���±������������б�ı���
    updateTableName(sortType, tableName)

#����sortType����ĳ���б�
def handleBySortType(sortType):
    #��ȡ�������б���Ϣ
    sortList = getSortList(sortType)

    #�����������б���Ϣ�����ݿ���
    insertSortList(sortType, sortList)
  
#ר��TO
class ChannelTO:
    def __init__(self):
        self.channelId = None
        self.name = None
        self.enName = None
        self.pinyin = None
        self.resourceType = None
        self.hotCnt = None
        self.stars = None
        self.score = None
        self.outline = None
        self.description = None
        self.icon = None
        self.banner = None
        self.image_410X250 = None
        self.collectCnt = None
        self.dataType = None
        self.tipType = None
        self.categoryId = None
        self.categoryName = None
        self.categoryTabFlagSet = None
        self.tagIds = None
        self.lastestVerName = None
        self.publishDate = None
        self.createdDate = None
        self.pkgFileSize = None
        self.pkgCreatedDate = None
        self.pkgChannelFlagSet = None
        self.pkgFileSizeScope = None
        self.onlineYear = None
        self.vendorId = None
        self.languageType = None
        self.status = None
    
    def setChannelId(self, channelId):
        self.channelId = channelId
        
    def getChannelId(self):
        return self.channelId
        
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def setEnName(self, enName):
        self.enName = enName
        
    def getEnName(self):
        return self.enName
        
    def setPinyin(self, pinyin):
        self.pinyin = pinyin
        
    def getPinyin(self):
        return self.pinyin
        
    def setResourceType(self, resourceType):
        self.resourceType = resourceType
        
    def getResourceType(self):
        return self.resourceType
        
    def setHotCnt(self, hotCnt):
        self.hotCnt = hotCnt
        
    def getHotCnt(self):
        return self.hotCnt
        
    def setStars(self, stars):
        self.stars = stars
        
    def getStars(self):
        return self.stars
        
    def setScore(self, score):
        self.score = score
        
    def getScore(self):
        return self.score

    def setOutline(self, outline):
        self.outline = outline
        
    def getOutline(self):
        return self.outline
        
    def setDescription(self, description):
        self.description = description
        
    def getDescription(self):
        return self.description
        
    def setIcon(self, icon):
        self.icon = icon
        
    def getIcon(self):
        return self.icon
        
    def setBanner(self, banner):
        self.banner = banner
        
    def getBanner(self):
        return self.banner
        
    def setImage_410X250(self, image_410X250):
        self.image_410X250 = image_410X250
        
    def getImage_410X250(self):
        return self.image_410X250
 
    def setCollectCnt(self, collectCnt):
        self.collectCnt = collectCnt
        
    def getCollectCnt(self):
        return self.collectCnt 
        
    def setDataType(self, dataType):
        self.dataType = dataType
        
    def getDataType(self):
        return self.dataType 
        
    def setTipType(self, tipType):
        self.tipType = tipType
        
    def getTipType(self):
        return self.tipType 

    def setCategoryId(self, categoryId):
        self.categoryId = categoryId
        
    def getCategoryId(self):
        return self.categoryId

    def setCategoryName(self, categoryName):
        self.categoryName = categoryName
        
    def getCategoryName(self):
        return self.categoryName

    def setCategoryTabFlagSet(self, categoryTabFlagSet):
        self.categoryTabFlagSet = categoryTabFlagSet
        
    def getCategoryTabFlagSet(self):
        return self.categoryTabFlagSet
      
    def setTagIds(self, tagIds):
        self.tagIds = tagIds
        
    def getTagIds(self):
        return self.tagIds
 
    def setLastestVerName(self, lastestVerName):
        self.lastestVerName = lastestVerName
        
    def getLastestVerName(self):
        return self.lastestVerName

    def setPublishDate(self, publishDate):
        self.publishDate = publishDate
        
    def getPublishDate(self):
        return self.publishDate

    def setCreatedDate(self, createdDate):
        self.createdDate = createdDate
        
    def getCreatedDate(self):
        return self.createdDate
        
    def setPkgFileSize(self, pkgFileSize):
        self.pkgFileSize = pkgFileSize
        
    def getPkgFileSize(self):
        return self.pkgFileSize
        
    def setPkgCreatedDate(self, pkgCreatedDate):
        self.pkgCreatedDate = pkgCreatedDate
        
    def getPkgCreatedDate(self):
        return self.pkgCreatedDate
        
    def setPkgChannelFlagSet(self, pkgChannelFlagSet):
        self.pkgChannelFlagSet = pkgChannelFlagSet
        
    def getPkgChannelFlagSet(self):
        return self.pkgChannelFlagSet
        
    def setPkgFileSizeScope(self, pkgFileSizeScope):
        self.pkgFileSizeScope = pkgFileSizeScope
        
    def getPkgFileSizeScope(self):
        return self.pkgFileSizeScope
        
    def setOnlineYear(self, onlineYear):
        self.onlineYear = onlineYear
        
    def getOnlineYear(self):
        return self.onlineYear
        
    def setVendorId(self, vendorId):
        self.vendorId = vendorId
        
    def getVendorId(self):
        return self.vendorId
        
    def setLanguageType(self, languageType):
        self.languageType = languageType
        
    def getLanguageType(self):
        return self.languageType
        
    def setStatus(self, status):
        self.status = status
        
    def getStatus(self):
        return self.status
   
###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
        
        #��ʼ��
        print 'init'
        initTag()
        initChannelSpecialInfo()
        initOrgGameList()
        initOrgSoftwareList()
        initOrgNetgameList()
        
        #��Ϸԭʼ�б�
        print '��Ϸԭʼ�б�'
        sortType = GAME_ORIGINAL_LIST
        handleBySortType(sortType)
        
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_HOTEST_LIST
        handleBySortType(sortType)
        
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_NEWEST_LIST
        handleBySortType(sortType)
        
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_FIVESTAR_LIST
        handleBySortType(sortType)
        
        #���ԭʼ�б�
        print '���ԭʼ�б�'
        sortType = SOFTWARE_ORIGINAL_LIST
        handleBySortType(sortType)
        
        #��������б�
        print '��������б�'
        sortType = SOFTWARE_HOTEST_LIST
        handleBySortType(sortType)
        
        #��������б�
        print '��������б�'
        sortType = SOFTWARE_NEWEST_LIST
        handleBySortType(sortType)
        
        #��������б�
        print '��������б�'
        sortType = SOFTWARE_FIVESTAR_LIST
        handleBySortType(sortType)
        
        #����ԭʼ�б�
        print '����ԭʼ�б�'
        sortType = NETGAME_ORIGINAL_LIST
        handleBySortType(sortType)
        
        #���������б�
        print '���������б�'
        sortType = NETGAME_HOTEST_LIST
        handleBySortType(sortType)
        
        #���������б�
        print '���������б�'
        sortType = NETGAME_NEWEST_LIST
        handleBySortType(sortType)
        
        #���������б�
        print '���������б�'
        sortType = NETGAME_FIVESTAR_LIST
        handleBySortType(sortType)

        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        print spentTime
        maxTime = datetime.timedelta(minutes=15)
        if spentTime > maxTime:
             #�ű����г�ʱ�����澯��Ϣ�����䣬�п������ݿ����ܻ���~~~
             sendmail('webmaster@downjoy.com', MONITOR_MAIL, "�ű���ʱ", "android ���ɹ��λ�б�--�ű���ʱ,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")

        #����web�������е��б�״̬��Ϣ����
        #cleanListTableStatusCache()

    except Exception, ex:
        #print(sys.exc_info()[0],sys.exc_info()[1])
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), "android ���ɹ��λ�б����,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")
        raise Exception

    finally:
        cursor.close()
        conn.close()
