#!/usr/bin/python
# -*- #coding:cp936
from __builtin__ import str

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2013/11/21 $"

import sys
import MySQLdb
import traceback
import datetime
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import smtplib
import httplib

#�쳣�ʼ�������
MONITOR_MAIL=['jiang.liu@downjoy.com']

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
TYPE_DIC = {GAME_HOTEST_LIST:'GAME_HOTEST_LIST', GAME_FIVESTAR_LIST:'GAME_5STARS_LIST', GAME_NEWEST_LIST:'GAME_NEWEST_LIST', GAME_ORIGINAL_LIST:'GAME_ORIGINAL_LIST', SOFTWARE_HOTEST_LIST:'SOFTWARE_HOTEST_LIST', SOFTWARE_FIVESTAR_LIST:'SOFTWARE_5STARS_LIST', SOFTWARE_NEWEST_LIST:'SOFTWARE_NEWEST_LIST', SOFTWARE_ORIGINAL_LIST:'SOFTWARE_ORIGINAL_LIST', NETGAME_HOTEST_LIST:'NETGAME_HOTEST_LIST', NETGAME_FIVESTAR_LIST:'NETGAME_5STARS_LIST', NETGAME_NEWEST_LIST:'NETGAME_NEWEST_LIST', NETGAME_ORIGINAL_LIST:'NETGAME_ORIGINAL_LIST'}

#��ʶ��ͬ��Դ���
RESOURCE_TYPE_GAME = 1      #��Ϸ
RESOURCE_TYPE_SOFTWARE = 2  #���
RESOURCE_TYPE_NETGAME = 5   #����

#��ʶ��ͬ�����б����Դ���ͣ�resource_type��
LIST_RESOURCE_TYPE_DIC = {GAME_HOTEST_LIST:RESOURCE_TYPE_GAME, GAME_FIVESTAR_LIST:RESOURCE_TYPE_GAME, GAME_NEWEST_LIST:RESOURCE_TYPE_GAME, GAME_ORIGINAL_LIST:RESOURCE_TYPE_GAME, SOFTWARE_HOTEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_FIVESTAR_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_NEWEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_ORIGINAL_LIST:RESOURCE_TYPE_SOFTWARE, NETGAME_HOTEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_FIVESTAR_LIST:RESOURCE_TYPE_NETGAME, NETGAME_NEWEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_ORIGINAL_LIST:RESOURCE_TYPE_NETGAME}

#����Ҫ������λ���б�
NOT_ADVERTISE_LIST = [GAME_ORIGINAL_LIST, SOFTWARE_ORIGINAL_LIST, NETGAME_ORIGINAL_LIST]

#�عϷ�����IP:port
DIGUA_IP_LIST = ['192.168.0.211:7011', '192.168.0.155:7011', '192.168.0.167:7011', '192.168.0.174:7011']

#ȫ�ֱ���
TAG_DIC = {} #��ǩ
ORG_GAME_LIST = [] #ԭʼ��Ϸ�б�
ORG_SOFTWARE_LIST = [] #ԭʼ����б�
ORG_NETGAME_LIST = [] #ԭʼ�����б�

class Entry(object):
    def __init__(self, val, p= None):
        self.data = val
        self.next = p

    # ÿ��append����������ͷ��λ�����
    def append(self, value):
        prevous = Entry(self.data)
        self.data = value;
        self.next = prevous
    
    def gettail(self):
        p = self
        while p and p.next:
            p = self.next
        return p    

    def tolist(self):
        result = []
        if(self.data):
            result.append(self.data)
        p = self.next
        while p:
            if p.data:
                result.append(p.data)
            p = p.next
        
        return result

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
    #���digua����
    for ip in DIGUA_IP_LIST:
        url = "/clean/ablist"
        conn = httplib.HTTPConnection(ip)
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()

	#���newdigua�б���
    url = "/newdiguaserver/clean/redis/cleankeyprefix?key=_new_digua_game_newest_list_language"
    conn = httplib.HTTPConnection("api2014.digua.d.cn")
    conn.request("GET", url)
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
    global ORG_GAME_LIST
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
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 1
            AND G.STATUS = 1
            AND P.STATUS = 1
            GROUP BY G.ID
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
        #�����DIGUA��WEB��WAP������û��ͬ���õ���Ϸ���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
        if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setCategoryId(row[3])
        channelTO.setComments(row[4])
        channelTO.setHotCnt(row[5])
        channelTO.setStars(row[6])
        channelTO.setIcon(row[7])
        channelTO.setLastestVerName(row[8])
        channelTO.setDataType(row[9])
        channelTO.setLanguageType(row[10])
        channelTO.setPublishDate(row[11])
        channelTO.setCreatedDate(row[12])
        channelTO.setGoodRatingCnt(row[13])
        channelTO.setCategoryName(row[14])
        channelTO.setBanner(row[15])
        channelTO.setPkgFileSize(row[16])
        channelTO.setPkgCreatedDate(row[17])
        channelTO.setPkgChannelFlagSet(row[18])
        channelTO.setMinSdk(row[19])
        channelTO.setSreenSizeSet(row[20])
        channelTO.setCopyrightType(row[21])
        channelTO.setScore(row[22])
        channelTO.setDowns(row[23])
        channelTO.setOutline(row[24])
        channelTO.setDescription(row[25])
        channelTO.setImage_410X250(row[26])
        channelTO.setUrl(row[27])
        channelTO.setChannelId(row[28])
        channelTO.setCategoryTabFlagSet(row[29])
        channelTO.setTipType(row[30])
        if row[31]:
            channelTO.setCollectCnt(row[31])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setTagIds(getTagIdsByNames(row[32]))
        channelTO.setStatus(row[33])
        channelTO.setVendorId(row[34])
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        channelTO.setResourceType(1)
        channelTO.setAdvLanguageType(0)
        
        ORG_GAME_LIST.append(channelTO)
#��ȡ�����Ϣ����publishDate����
def initOrgSoftwareList():
    global ORG_SOFTWARE_LIST
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
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 2
            AND G.STATUS = 1
            AND P.STATUS = 1
            GROUP BY G.ID
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
        #��DIGUA��WEB��WAP������û��ͬ���õ���Ϸ���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
        if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setCategoryId(row[3])
        channelTO.setComments(row[4])
        channelTO.setHotCnt(row[5])
        channelTO.setStars(row[6])
        channelTO.setIcon(row[7])
        channelTO.setLastestVerName(row[8])
        channelTO.setDataType(row[9])
        channelTO.setLanguageType(row[10])
        channelTO.setPublishDate(row[11])
        channelTO.setCreatedDate(row[12])
        channelTO.setGoodRatingCnt(row[13])
        channelTO.setCategoryName(row[14])
        channelTO.setBanner(row[15])
        channelTO.setPkgFileSize(row[16])
        channelTO.setPkgCreatedDate(row[17])
        channelTO.setPkgChannelFlagSet(row[18])
        channelTO.setMinSdk(row[19])
        channelTO.setSreenSizeSet(row[20])
        channelTO.setCopyrightType(row[21])
        channelTO.setScore(row[22])
        channelTO.setDowns(row[23])
        channelTO.setOutline(row[24])
        channelTO.setDescription(row[25])
        channelTO.setImage_410X250(row[26])
        channelTO.setUrl(row[27])
        channelTO.setChannelId(row[28])
        channelTO.setCategoryTabFlagSet(row[29])
        channelTO.setTipType(row[30])
        if row[31]:
            channelTO.setCollectCnt(row[31])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setTagIds(getTagIdsByNames(row[32]))
        channelTO.setStatus(row[33])
        channelTO.setVendorId(row[34])
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        channelTO.setResourceType(2)
        
        ORG_SOFTWARE_LIST.append(channelTO)
        
#��ȡ������Ϣ
def initOrgNetgameList():
    global ORG_NETGAME_LIST
    sql = '''select C.ID,
                    C.NAME,
                    C.PINYIN,
                    C.HDICON,
                    C.TAG_NAMES,
                    C.STARS,
                    C.HOT_CNT,
                    C.CREATED_DATE,
                    C.LAST_UPDATE_DATE,
                    G.LAST_VERSION_NUM,
                    GP.FILE_SIZE,
                    C.BANNER,
                    MIN(GPM.MIN_SDK),
                    BIT_OR(GPM.SCREEN_SIZE_SET),
                    C.TAG_IDS,
                    C.SCORE,
                    C.DOWNS,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION,
                    MAX(GP.CREATED_DATE), 
                    C.COLLECT_CNT,
                    C.OPERATION_STATUS,
                    C.CP_ID 
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            left join NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
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
        channelTO.setId(row[0])
        channelTO.setChannelId(row[0])
        channelTO.setName(row[1])
        channelTO.setPinyin(row[2])
        channelTO.setIcon(row[3])
        channelTO.setCategoryName(row[4])
        channelTO.setStars(row[5])
        channelTO.setHotCnt(row[6])
        channelTO.setCreatedDate(row[7])
        channelTO.setPublishDate(row[8])
        channelTO.setLastestVerName(row[9])
        channelTO.setPkgFileSize(row[10])
        channelTO.setBanner(row[11])
        channelTO.setMinSdk(row[12])
        channelTO.setSreenSizeSet(row[13])
        channelTO.setCategoryId(row[14])
        channelTO.setScore(row[15])
        channelTO.setDowns(row[16])
        channelTO.setOutline(row[17])
        channelTO.setDescription(row[18])
        channelTO.setPkgCreatedDate(row[19])
        if row[20]:
            channelTO.setCollectCnt(row[20])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setStatus(row[21])
        channelTO.setVendorId(row[22])
        channelTO.setDataType(0)
        channelTO.setLanguageType(7) #����Ĭ��Ϊ֧����-2��Ӣ-1����-4
        channelTO.setResourceType(5)
        channelTO.setTipType(0)
        channelTO.setPkgChannelFlagSet(511)
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        ORG_NETGAME_LIST.append(channelTO)

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
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G 
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.ID = %d
            AND G.RESOURCE_TYPE = %d
            AND G.STATUS = 1
            AND P.STATUS = 1''' % (channelId, resourceType)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows and (len(rows) > 0) and rows[0][0]:
            #���DIGUA��WEB��WAP������û��ͬ����,���˳�ȥ��1��WEB  2: WAP  4��DIGUA��
            row = rows[0]
            if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
                return None
            channelTO = ChannelTO()
            channelTO.setId(row[0])
            channelTO.setName(row[1])
            channelTO.setEnName(row[2])
            channelTO.setCategoryId(row[3])
            channelTO.setComments(row[4])
            channelTO.setHotCnt(row[5])
            channelTO.setStars(row[6])
            channelTO.setIcon(row[7])
            channelTO.setLastestVerName(row[8])
            channelTO.setDataType(row[9] | 16) #16��ʾ����Դ��һ�����λ������ǰ̨�Ǳ��չʾ
            channelTO.setLanguageType(row[10])
            channelTO.setPublishDate(row[11])
            channelTO.setCreatedDate(row[12])
            channelTO.setGoodRatingCnt(row[13])
            channelTO.setCategoryName(row[14])
            channelTO.setBanner(row[15])
            channelTO.setPkgFileSize(row[16])
            channelTO.setPkgCreatedDate(row[17])
            channelTO.setPkgChannelFlagSet(row[18])
            channelTO.setMinSdk(row[19])
            channelTO.setSreenSizeSet(row[20])
            channelTO.setCopyrightType(row[21])
            channelTO.setScore(row[22])
            channelTO.setDowns(row[23])
            channelTO.setOutline(row[24])
            channelTO.setDescription(row[25])
            channelTO.setImage_410X250(row[26])
            channelTO.setUrl(row[27])
            channelTO.setChannelId(row[28])
            channelTO.setCategoryTabFlagSet(row[29])
            channelTO.setTipType(row[30])
            if row[31]:
                channelTO.setCollectCnt(row[31])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setTagIds(getTagIdsByNames(row[32]))
            channelTO.setStatus(row[33])
            channelTO.setVendorId(row[34])
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            channelTO.setResourceType(resourceType)
               
    elif resourceType == RESOURCE_TYPE_NETGAME:
        sql = '''select C.ID,
                        C.NAME,
                        C.PINYIN,
                        C.HDICON,
                        C.TAG_NAMES,
                        C.STARS,
                        C.HOT_CNT,
                        C.CREATED_DATE,
                        C.LAST_UPDATE_DATE,
                        G.LAST_VERSION_NUM,
                        GP.FILE_SIZE,
                        C.BANNER,
                        MIN(GPM.MIN_SDK),
                        BIT_OR(GPM.SCREEN_SIZE_SET),
                        C.TAG_IDS,
                        C.SCORE,
                        C.DOWNS,
                        CASE
                            WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                            ELSE C.OUTLET_LINE
                        END AS OUTLINE,
                        C.DESCRIPTION,
                        MAX(GP.CREATED_DATE), 
                        C.COLLECT_CNT,
                        C.OPERATION_STATUS,
                        C.CP_ID 
                FROM NETGAME_CHANNEL C
                LEFT JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID
                LEFT JOIN NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
                LEFT JOIN NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
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
            channelTO.setId(row[0])
            channelTO.setChannelId(row[0])
            channelTO.setName(row[1])
            channelTO.setPinyin(row[2])
            channelTO.setIcon(row[3])
            channelTO.setCategoryName(row[4])
            channelTO.setStars(row[5])
            channelTO.setHotCnt(row[6])
            channelTO.setCreatedDate(row[7])
            channelTO.setPublishDate(row[8])
            channelTO.setLastestVerName(row[9])
            channelTO.setPkgFileSize(row[10])
            channelTO.setBanner(row[11])
            channelTO.setMinSdk(row[12])
            channelTO.setSreenSizeSet(row[13])
#             channelTO.setCategoryId(row[14])
            channelTO.setScore(row[15])
            channelTO.setDowns(row[16])
            channelTO.setOutline(row[17])
            channelTO.setDescription(row[18])
            channelTO.setPkgCreatedDate(row[19])
            if row[20]:
                channelTO.setCollectCnt(row[20])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setStatus(row[21])
            channelTO.setVendorId(row[22])
            channelTO.setDataType(16) #16��ʾ����Դ��һ�����λ������ǰ̨�Ǳ��չʾ
            channelTO.setLanguageType(7) #����Ĭ��Ϊ֧����-2��Ӣ-1����-4
            channelTO.setResourceType(5)
            channelTO.setTipType(0)
            channelTO.setPkgChannelFlagSet(511)
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            
    return channelTO

#�����Ӫ�Զ�������б�ҳ�е���Դ����Ϸ/���/���Σ�������Ϣ
def reOrderSortList(sortType, sortList, languageType):
    sql = '''SELECT RESOURCE_ID,
                    RESOURCE_TYPE,
                    POSITION
             FROM GAME_LIST_CUSTOM_ADV
             WHERE LIST_TYPE = %d
             AND LANGUAGE_TYPE = %d
             ORDER BY POSITION ASC''' % (sortType, languageType)
    cursor.execute(sql)
    rows = cursor.fetchall()

    exclusion_ids = ''
    if not rows: 
        return exclusion_ids
    count = 0
    for row in rows:
        position = int(row[2])
        # ҵ����������б���ֻ�ܲ������ι��λ����Ϸ/������˵�
        if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_NETGAME) and (row[1] != RESOURCE_TYPE_NETGAME):
#             print "netgame resource list not allow insert the non netgame resource, custom resource:%d, language_type:%d"   %(row[0], languageType)
            continue

        #��ȡ���λ��Դ��Ϣ
        customResourceInfo = getResourceInfo(row[0], row[1])
        if not customResourceInfo:
#             print "resource not found, ignore custom resource, custom resource:%d, language_type:%d"   %(row[0], languageType)
            continue
        
        if GAME_FIVESTAR_LIST == sortType and customResourceInfo.getStars() != 5:
            continue
        # ���ù��λ��������
        customResourceInfo.setAdvLanguageType(languageType)
        tmpChannelTO = None
        tmpEntry = None
        index = position - 1
        if position > 0 and position < len(sortList):
            tmpEntry = sortList[index]
            tmpChannelTO = tmpEntry.data
            if not tmpChannelTO:
                continue
            if tmpChannelTO.getAdvLanguageType() == 0: # ����ýڵ��ֵΪ
                sortList.insert(index, Entry(customResourceInfo))
            else:
                tmpEntry.append(customResourceInfo)
            
            if LIST_RESOURCE_TYPE_DIC[sortType] ==  customResourceInfo.getResourceType():
                exclusion_ids = exclusion_ids + ',' + str(customResourceInfo.getId())
            count += 1
        
    print 'list reorder success, original len: %d, sortcount: %d, languageType :%d' % (len(rows), count, languageType)

    return exclusion_ids

#�����Ϸԭʼ������б�(exclusion_ids:�����Ѿ��ǹ��λ����Ҫ�ų���ID)
def getOriginalGameSortList(sortType, isEntry):
    orgSortList = []
    if sortType == GAME_HOTEST_LIST:  #����
        for channelTO in ORG_GAME_LIST:
            if isEntry:
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == GAME_NEWEST_LIST or sortType == GAME_ORIGINAL_LIST:
        for channelTO in ORG_GAME_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == GAME_FIVESTAR_LIST: #����
        for channelTO in ORG_GAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList
    
 #������ԭʼ������б�
def getOriginalSoftwareSortList(sortType, isEntry):
    orgSortList = []
    if sortType == SOFTWARE_HOTEST_LIST:  #����
        for channelTO in ORG_SOFTWARE_LIST:
            if (isEntry):
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == SOFTWARE_NEWEST_LIST or sortType == SOFTWARE_ORIGINAL_LIST:
        for channelTO in ORG_SOFTWARE_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == SOFTWARE_FIVESTAR_LIST: #����
        for channelTO in ORG_SOFTWARE_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList

#�������ԭʼ������б�
def getOriginalNetgameSortList(sortType, isEntry):
    orgSortList = []
    if sortType == NETGAME_HOTEST_LIST:  #����
        for channelTO in ORG_NETGAME_LIST:
            if (isEntry):
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == NETGAME_NEWEST_LIST or sortType == NETGAME_ORIGINAL_LIST:
        for channelTO in ORG_NETGAME_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == NETGAME_FIVESTAR_LIST: #����
        for channelTO in ORG_NETGAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList
#===============================================================================
# ����й��λ���롢�������б�
# 1.��Ҫ�ǳ�ע���һ���ǣ������advLanguaged ΪTrue��Ҳ���Ǳ��������������˵ģ�����Ҫ�������ģ���������һ����
# 2.���û��advLanguaged��ֻ��һ��
#===============================================================================
def getAdvertiseSortList(sortType, advLanguaged = False):
    
    sortList = getOriginalSortList(sortType, True)
    # ��Ӫ�Զ�������
    exclusion_ids = ','
    if(advLanguaged):
        exclusion_ids += reOrderSortList(sortType, sortList, 2)  # ��������
        exclusion_ids += reOrderSortList(sortType, sortList, 32)  # ��������
    else:
        exclusion_ids += reOrderSortList(sortType, sortList, 2)

    resultlist = []
    orginalChannelEntry = None
    # sortList
    for entry in sortList:
        orginalChannelEntry = entry.gettail()
        if (not orginalChannelEntry) or (not orginalChannelEntry.data):
            continue
        # �����Ҫ�޳�����id���ҵ���Ӧ��id,��entry�����һλ�������ÿ�,tolist�������������ȥ����
        if (orginalChannelEntry.data.getAdvLanguageType() == 0 and exclusion_ids.find(str(orginalChannelEntry.data.getId())) != -1):
            orginalChannelEntry.data = None
        for data in entry.tolist():
            resultlist.append(data)
           
    print 'get sort list, original len%d, final rows len: %d' % (len(sortList), len(resultlist))
    return resultlist

#��ȡԭʼ�����б�
def getOriginalSortList(sortType, isEntry = False):
    originalSortList = []
    
    #�������Ϸ���͵��������ԭʼ����Ϸ�б����޳�
    if LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_GAME:
        originalSortList = getOriginalGameSortList(sortType, isEntry)
    #�����������͵��������ԭʼ������б����޳�
    elif LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_SOFTWARE:
        originalSortList = getOriginalSoftwareSortList(sortType, isEntry)
    #�����ԭʼ���������޳�
    else:
        originalSortList = getOriginalNetgameSortList(sortType, isEntry)
    print 'orignal rows len: %d' % (len(originalSortList))

    return originalSortList

#�����������õ��б�
def getSortList(sortType, advLanguaged = False):
    if sortType in NOT_ADVERTISE_LIST:
        return getOriginalSortList(sortType)
    else:
        return getAdvertiseSortList(sortType, advLanguaged)

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

#===============================================================================
# #�����������б���Ϣ
# advLanguaged �Ƿ���Ҫ������λ�������ͣ� ��Ҫע�⣬Ŀǰֻ��Ҫ����Ϸ�ļ��ű�������ͬ�������������������
#===============================================================================
def insertResourceInfos(tableName, sortList, advLanguaged):
    sql = ''
    seq = 1
    if not sortList: 
        return
    datalist = []
    
    if(advLanguaged):
        for channelTO in sortList:
            sql = "INSERT INTO %s " % tableName
            sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, CATEGORY_TAB_FLAG_SET, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, COPYRIGHT_TYPE, GOOD_RATING_CNT, FILE_SIZE, SCREEN_SIZE_SET, MIN_SDK, LATEST_VERSION_NAME, CREATED_DATE, PKG_CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, PKG_CHANNEL_FLAG_SET, SCORE, DOWNS, OUTLINE, DESCRIPTION, IMAGE_410X250, URL, TIP_TYPE, COLLECT_CNT, PKG_FILE_SIZE_SCOPE, ONLINE_YEAR, TAG_IDS, STATUS, VENDOR_ID, CHANNEL_ID, ADV_LANGUAGE_TYPE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            datalist.append((seq,
                             channelTO.getId(),
                             channelTO.getName(),
                             channelTO.getEnName(),
                             channelTO.getPinyin(),
                             channelTO.getCategoryId(),
                             channelTO.getCategoryName(),
                             channelTO.getCategoryTabFlagSet(),
                             channelTO.getResourceType(),
                             channelTO.getComments(),
                             channelTO.getHotCnt(),
                             channelTO.getStars(),
                             channelTO.getPublishDate(),
                             channelTO.getIcon(),
                             channelTO.getBanner(),
                             channelTO.getCopyrightType(),
                             channelTO.getGoodRatingCnt(),
                             channelTO.getPkgFileSize(),
                             channelTO.getSreenSizeSet(),
                             channelTO.getMinSdk(),
                             channelTO.getLastestVerName(),
                             channelTO.getCreatedDate(),
                             channelTO.getPkgCreatedDate(),
                             channelTO.getDataType(),
                             channelTO.getLanguageType(),
                             channelTO.getPkgChannelFlagSet(),
                             channelTO.getScore(),
                             channelTO.getDowns(),
                             channelTO.getOutline(),
                             channelTO.getDescription(),
                             channelTO.getImage_410X250(),
                             channelTO.getUrl(),
                             channelTO.getTipType(),
                             channelTO.getCollectCnt(),
                             channelTO.getPkgFileSizeScope(),
                             channelTO.getOnlineYear(),
                             channelTO.getTagIds(),
                             channelTO.getStatus(),
                             channelTO.getVendorId(),
                             channelTO.getChannelId(),
                             channelTO.getAdvLanguageType()))
            seq += 1
            if len(datalist)>=1000:
                cursor.executemany(sql, tuple(datalist))
                conn.commit()
                datalist = []
                
        if datalist:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []                
    else:
        for channelTO in sortList:
            sql = "INSERT INTO %s " % tableName
            sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, CATEGORY_TAB_FLAG_SET, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, COPYRIGHT_TYPE, GOOD_RATING_CNT, FILE_SIZE, SCREEN_SIZE_SET, MIN_SDK, LATEST_VERSION_NAME, CREATED_DATE, PKG_CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, PKG_CHANNEL_FLAG_SET, SCORE, DOWNS, OUTLINE, DESCRIPTION, IMAGE_410X250, URL, TIP_TYPE, COLLECT_CNT, PKG_FILE_SIZE_SCOPE, ONLINE_YEAR, TAG_IDS, STATUS, VENDOR_ID, CHANNEL_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            datalist.append((seq,
                             channelTO.getId(),
                             channelTO.getName(),
                             channelTO.getEnName(),
                             channelTO.getPinyin(),
                             channelTO.getCategoryId(),
                             channelTO.getCategoryName(),
                             channelTO.getCategoryTabFlagSet(),
                             channelTO.getResourceType(),
                             channelTO.getComments(),
                             channelTO.getHotCnt(),
                             channelTO.getStars(),
                             channelTO.getPublishDate(),
                             channelTO.getIcon(),
                             channelTO.getBanner(),
                             channelTO.getCopyrightType(),
                             channelTO.getGoodRatingCnt(),
                             channelTO.getPkgFileSize(),
                             channelTO.getSreenSizeSet(),
                             channelTO.getMinSdk(),
                             channelTO.getLastestVerName(),
                             channelTO.getCreatedDate(),
                             channelTO.getPkgCreatedDate(),
                             channelTO.getDataType(),
                             channelTO.getLanguageType(),
                             channelTO.getPkgChannelFlagSet(),
                             channelTO.getScore(),
                             channelTO.getDowns(),
                             channelTO.getOutline(),
                             channelTO.getDescription(),
                             channelTO.getImage_410X250(),
                             channelTO.getUrl(),
                             channelTO.getTipType(),
                             channelTO.getCollectCnt(),
                             channelTO.getPkgFileSizeScope(),
                             channelTO.getOnlineYear(),
                             channelTO.getTagIds(),
                             channelTO.getStatus(),
                             channelTO.getVendorId(),
                             channelTO.getChannelId()))
            seq += 1
            if len(datalist)>=1000:
                cursor.executemany(sql, tuple(datalist))
                conn.commit()
                datalist = []
                
        if datalist:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []

    print "insert success, tableName:%s, count:%d" %(tableName, seq)
#���±������������б�ı���
def updateTableName(sortType, tableName):
    type2 = TYPE_DIC[sortType]
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),type2)
    cursor.execute(sql)
    conn.commit()

#�����������б���Ϣ�����ݿ���
def insertSortList(sortType, sortList, advLanguaged):
    #��ȡ����������
    tableName = ''
    tableName = getTableNameForInsert(sortType)
    print 'tableName: %s' % tableName

    #��մ�������
    clearTable(tableName)

    #��������
    print 'start insert'
    insertResourceInfos(tableName, sortList, advLanguaged)
    print 'end insert'

    #���±������������б�ı���
    updateTableName(sortType, tableName)

#����sortType����ĳ���б�
def handleBySortType(sortType, advLanguaged = False):
    #��ȡ�������б���Ϣ
    sortList = getSortList(sortType, advLanguaged)

    #�����������б���Ϣ�����ݿ���
    insertSortList(sortType, sortList, advLanguaged)
  
#ר��TO
class ChannelTO:
    def __init__(self):
        self.id = None
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
        self.pkgFileSizeScope = None
        self.onlineYear = None
        self.vendorId = None
        self.languageType = None
        self.comments = None
        self.goodRatingCnt = None
        self.minSdk = None
        self.sreenSizeSet = None
        self.copyrightType = None
        self.downs = None
        self.url = None
        self.status = None
        self.pkgChannelFlagSet = None
        self.advLanguageType = None
        
    def setId(self, id):
        self.id = id
        
    def getId(self):
        return self.id    
    
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
        
    def setComments(self, comments):
        self.comments = comments
        
    def getComments(self):
        return self.comments
        
    def setGoodRatingCnt(self, goodRatingCnt):
        self.goodRatingCnt = goodRatingCnt
        
    def getGoodRatingCnt(self):
        return self.goodRatingCnt
        
    def setMinSdk(self, minSdk):
        self.minSdk = minSdk
        
    def getMinSdk(self):
        return self.minSdk
        
    def setSreenSizeSet(self, sreenSizeSet):
        self.sreenSizeSet = sreenSizeSet
        
    def getSreenSizeSet(self):
        return self.sreenSizeSet
        
    def setCopyrightType(self, copyrightType):
        self.copyrightType = copyrightType
        
    def getCopyrightType(self):
        return self.copyrightType

    def setDowns(self, downs):
        self.downs = downs
        
    def getDowns(self):
        return self.downs
        
    def setUrl(self, url):
        self.url = url
        
    def getUrl(self):
        return self.url
    
    def setStatus(self, status):
        self.status = status
        
    def getStatus(self):
        return self.status
        
    def setPkgChannelFlagSet(self, pkgChannelFlagSet):
        self.pkgChannelFlagSet = pkgChannelFlagSet
        
    def getPkgChannelFlagSet(self):
        return self.pkgChannelFlagSet
    
    def setAdvLanguageType(self, advLanguageType):
        self.advLanguageType = advLanguageType
    
    def getAdvLanguageType(self):
        return self.advLanguageType
   
###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
        
        #��ʼ��
        initTag()
        print 'initTag success'
        
        initOrgGameList()
        print 'initOrgGameList success'
        
        initOrgSoftwareList()
        print 'initOrgSoftwareList success'
         
        initOrgNetgameList()
        print 'initOrgNetgameList success'
          
        #��Ϸԭʼ�б�
        print '��Ϸԭʼ�б�'
        sortType = GAME_ORIGINAL_LIST
        handleBySortType(sortType)
#           
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_HOTEST_LIST
        handleBySortType(sortType, True)
          
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_NEWEST_LIST
        handleBySortType(sortType, True)
           
        #��Ϸ�����б�
        print '��Ϸ�����б�'
        sortType = GAME_FIVESTAR_LIST
        handleBySortType(sortType, True)
           
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
        print traceback.format_exc()
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), "android ���ɹ��λ�б����,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")
        raise Exception

    finally:
        cursor.close()
        conn.close()
