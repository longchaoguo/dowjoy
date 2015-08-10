#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/12/11 09:09:22 $"
###########################################
#����ع�7.2��ҳ���λ
###########################################
import datetime
import StringIO
import traceback
import httplib
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

#��ʼ������
dbUtil_35 = DBUtil('droid_game_10')

#���λ��������
SPECIAL_GROUP = 1           #ר���б�
ORIGINAL_GROUP = 2          #ԭ���б�
GAME_SOFTWARE_NETGAME_GROUP = 4  #��Ϸ������������б�
GAME_POPULAR = 8            #��Ϸ�ƹ�λ
ORIGINAL_POPULAR = 16       #ԭ���ƹ�λ
GIFT_POPULAR = 32           #����ƹ�λ
ACTIVITY_POPULAR = 64       #�Զ����ƹ�λ
COMMENT_RANGK = 128         #�������а�

#��ʶ�ع�7.2��ҳ�Ƽ��б�
INDEX_ADV_DIGUA_72_LIST_TYPE = 'INDEX_ADV_DIGUA_72'

#####�ʼ���������
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "bourne@8.3"
mailSubject = u"�ع�7.2��ҳ�Ƽ����λ������Ϣ��indexAdvForDigua.py��".encode("gbk")
mailTo = ['jiang.liu@downjoy.com']
mailContents = u'Hi: \n'


#��ȡ���λ�������(��̨��������)
def getOriginalAdvData():
    sql = "SELECT GROUP_TYPE, GROUP_ID, BACKGROUND_IMAGE, GROUP_ORDER, TITLE, RESOURCE_ID, RESOURCE_TYPE, URL, ID, ORIGINAL_TYPE, LANGUAGE FROM INDEX_ADV_DIGUA_72 WHERE GROUP_ORDER > 0"
    rows = dbUtil_35.queryList(sql)
    if not rows or len(rows) == 0:
        return []
    
    originalAdvList = []
    for row in rows:
        originalAdvTO = {}
        originalAdvTO['GROUP_TYPE'] = row[0]
        originalAdvTO['GROUP_ID'] = row[1]
        originalAdvTO['BACKGROUND_IMAGE'] = row[2]
        originalAdvTO['GROUP_ORDER'] = row[3]
        originalAdvTO['TITLE'] = row[4]
        originalAdvTO['RESOURCE_ID'] = row[5]
        originalAdvTO['RESOURCE_TYPE'] = row[6]
        originalAdvTO['URL'] = row[7]
        originalAdvTO['ID'] = row[8]
        originalAdvTO['ORIGINAL_TYPE'] = row[9]
        originalAdvTO['LANGUAGE'] = row[10]
        originalAdvList.append(originalAdvTO)
    
    return originalAdvList
    

#����ÿ�����λ����ȡ������Ϣ
def dealWithOriginalAdv(originalAdvTO):
    groupType = originalAdvTO['GROUP_TYPE'] #��ͬ����Ĺ��λ
    groupType = groupType >> 40 #����40λ
    dealedAdvList = []
    if groupType == GAME_SOFTWARE_NETGAME_GROUP: #��Ϸ������������б�
        if originalAdvTO['RESOURCE_TYPE'] != 5: #��Ϸ�����
            sql = '''SELECT G.ID,
                            G.NAME,
                            G.EN_NAME,
                            G.ICON,
                            G.STARS,
                            G.PUBLISH_DATE,
                            G.RESOURCE_TYPE,
                            G.DATA_TYPE,
                            G.CREATED_DATE,
                            G.HOT_CNT,
                            G.COMMENTS, 
                            C.ID,
                            C.NAME,
                            P.ID AS PKG_ID,
                            P.NAME AS PKG_NAME,
                            P.PACKAGE_NAME,
                            P.FILE_SIZE AS PKG_FILESIZE,
                            P.URL AS PKG_URL,
                            RIGHT(P.URL,3),
                            P.VERSION_NAME,
                            P.VERSION_CODE,
                            P.CPU_TYPE_SET,
                            P.MIN_SDK,
                            (CASE 
                                WHEN  G.DATA_TYPE & 64 = 64 THEN 1
                            ELSE 0 END) AS NEED_GOOGLE_FRAMEWORK,
                            P.CREATED_DATE,
                            G.OUTLINE
                    FROM GAME G
                    INNER JOIN GAME_CATEGORY C ON C.ID = G.GAME_CATEGORY_ID
                    INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
                    WHERE G.ID = %d
                    AND G.STATUS = 1 
                    AND P.CHANNEL_FLAG_SET & 4 = 4 
                    AND P.STATUS = 1 
                    AND P.SYNC_CHANNEL_FLAG_SET & 4 = 4''' % (originalAdvTO['RESOURCE_ID'])
            rows = dbUtil_35.queryList(sql)
            if not rows or len(rows) == 0:
                return []
            for row in rows:
                dealedAdvTO = DealedAdvTO()
                dealedAdvTO.setId(row[0])
                dealedAdvTO.setName(row[1])
                dealedAdvTO.setEnName(row[2])
                dealedAdvTO.setIcon(row[3])
                dealedAdvTO.setStars(row[4])
                dealedAdvTO.setPublishDate(row[5])
                dealedAdvTO.setResourceType(row[6])
                dealedAdvTO.setDataType(row[7])
                dealedAdvTO.setCreatedDate(row[8])
                dealedAdvTO.setHotCnt(row[9])
                dealedAdvTO.setComments(row[10])
                dealedAdvTO.setCategoryId(row[11])
                dealedAdvTO.setCategoryName(dealWithCategoryName(row[12]))
                dealedAdvTO.setPkgId(row[13])
                dealedAdvTO.setPkgName(row[14])
                dealedAdvTO.setPkgPackageName(row[15])
                dealedAdvTO.setPkgFileSize(row[16])
                dealedAdvTO.setPkgUrl(row[17])
                dealedAdvTO.setPkgUrlSuffix(row[18])
                dealedAdvTO.setPkgVersionName(row[19])
                dealedAdvTO.setPkgVersionCode(row[20])
                dealedAdvTO.setPkgCpuTypeSet(row[21])
                dealedAdvTO.setPkgMinSdk(row[22])
                dealedAdvTO.setPkgNeedGoogleFramework(row[23])
                dealedAdvTO.setPkgCreatedDate(row[24])
                dealedAdvTO.setOutline(row[25])
                dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
                dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
                dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
                dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
                dealedAdvTO.setTitle(originalAdvTO['TITLE'])
                dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
                dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
                dealedAdvList.append(dealedAdvTO)
        else: #����
            sql = '''SELECT C.ID,
                            C.NAME,
                            C.HDICON,
                            C.STARS,
                            P.CREATED_DATE,
                            C.CREATED_DATE,
                            C.HOT_CNT,
                            C.COMMENTS,
                            C.TAG_NAMES,
                            P.ID,
                            CONCAT(C.name,'-',G.name) AS PKG_NAME,
                            P.PACKAGE_NAME,
                            P.FILE_SIZE,
                            REPLACE(P.URL, "res5.d.cn", "res8.d.cn") AS PKG_URL,
                            RIGHT(P.URL,3) AS PKG_URL_SUFFIX,
                            G.LAST_VERSION_NUM,
                            P.VERSION_CODE,
                            P.created_date,
                            (case when C.OUTLET_LINE is null or length(C.OUTLET_LINE) = 0 then C.SLOGAN
                             else C.OUTLET_LINE
                            end)as outline
                    FROM NETGAME_CHANNEL C
                    INNER JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID
                    INNER JOIN NETGAME_GAME_PKG P ON G.ID = P.GAME_ID
                    WHERE C.ID = %d 
                    AND C.STATUS=1
                    AND C.NETGAME_SYNC_STATUS > 0
                    AND G.NETGAME_SYNC_STATUS > 0
                    AND P.NETGAME_SYNC_STATUS > 0
                    AND G.CHANNEL_FLAG & 8 = 8
                    AND P.ID = (SELECT MAX(ID) FROM NETGAME_GAME_PKG P2 WHERE P2.GAME_ID = G.ID) LIMIT 1''' % (originalAdvTO['RESOURCE_ID'])
            rows = dbUtil_35.queryList(sql)
            if not rows or len(rows) == 0:
                return []
            for row in rows:
                dealedAdvTO = DealedAdvTO()
                dealedAdvTO.setId(row[0])
                dealedAdvTO.setName(row[1])
                dealedAdvTO.setIcon(row[2])
                dealedAdvTO.setStars(row[3])
                dealedAdvTO.setPublishDate(row[4])
                dealedAdvTO.setResourceType(5)
                dealedAdvTO.setCreatedDate(row[5])
                dealedAdvTO.setHotCnt(row[6])
                dealedAdvTO.setComments(row[7])
                dealedAdvTO.setCategoryName(dealWithCategoryName(row[8]))
                dealedAdvTO.setPkgId(row[9])
                dealedAdvTO.setPkgName(row[10])
                dealedAdvTO.setPkgPackageName(row[11])
                dealedAdvTO.setPkgFileSize(row[12])
                dealedAdvTO.setPkgUrl(row[13])
                dealedAdvTO.setPkgUrlSuffix(row[14])
                dealedAdvTO.setPkgVersionName(row[15])
                dealedAdvTO.setPkgVersionCode(row[16])
                dealedAdvTO.setPkgCreatedDate(row[17])
                dealedAdvTO.setOutline(row[18])
                dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
                dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
                dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
                dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
                dealedAdvTO.setTitle(originalAdvTO['TITLE'])
                dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
                dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
                dealedAdvList.append(dealedAdvTO)
         
    elif groupType == SPECIAL_GROUP:
        sql = 'SELECT GAME_IDS, RESOURCE_TYPE, DESCRIPTION FROM ACTIVITY WHERE ID = %d' % (originalAdvTO['GROUP_ID'])
        row = dbUtil_35.queryRow(sql)
        if not row:
            return []
        gameIds = row[0]
        resourceType = row[1]
        description = row[2]
        gameIdList = gameIds.split(',')
        if resourceType == 5: #����
            for gameId in gameIdList:
                sql = 'SELECT ID, NAME, HDICON FROM NETGAME_CHANNEL WHERE ID = %s' % (gameId)
                row = dbUtil_35.queryRow(sql)
                if not row or len(row) == 0:
                    continue
                dealedAdvTO = DealedAdvTO()
                dealedAdvTO.setId(row[0])
                dealedAdvTO.setName(row[1])
                dealedAdvTO.setIcon(row[2])
                dealedAdvTO.setResourceType(5)
                dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
                dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
                dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
                dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
                dealedAdvTO.setTitle(originalAdvTO['TITLE'])
                dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
                dealedAdvTO.setGroupDescription(description)
                dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
                dealedAdvList.append(dealedAdvTO)
        else: #��Ϸ�����
            for gameId in gameIdList:
                sql = 'SELECT ID, NAME, EN_NAME, ICON, RESOURCE_TYPE FROM GAME WHERE ID = %s and RESOURCE_TYPE = %s' % (gameId, resourceType)
                row = dbUtil_35.queryRow(sql)
                if not row:
                    continue
                dealedAdvTO = DealedAdvTO()
                dealedAdvTO.setId(row[0])
                dealedAdvTO.setName(row[1])
                dealedAdvTO.setEnName(row[2])
                dealedAdvTO.setIcon(row[3])
                dealedAdvTO.setResourceType(row[4])
                dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
                dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
                dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
                dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
                dealedAdvTO.setTitle(originalAdvTO['TITLE'])
                dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
                dealedAdvTO.setGroupDescription(description)
                dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
                dealedAdvList.append(dealedAdvTO)
    elif groupType == ORIGINAL_GROUP:
        sql = 'SELECT GAME_IDS, DESCRIPTION FROM ORIGINAL WHERE ID = %d' % (originalAdvTO['GROUP_ID'])
        row = dbUtil_35.queryRow(sql)
        if not row:
            return []
        gameIds = row[0]
        description = row[1]
        gameIdList = gameIds.split(',')
        conn = httplib.HTTPConnection("api.news.d.cn")
        for gameId in gameIdList:
            #����ԭ���ӿڻ�ȡID, NAME,ICON,CateCode
            url = "/GetNewsBasicInfoByID.ashx?ids=%s" % gameId
            conn.request("GET", url)
            res = conn.getresponse()
            resData = res.read()
            resData = resData.replace('null', 'None')
            resData = resData.replace('false', 'False')
            resData = resData.replace('true', 'True')
            originalData = eval(resData)
            if not originalData or len(originalData) == 0:
                continue
            dealedAdvTO = DealedAdvTO()
            dealedAdvTO.setId(originalData[0]['ID'])
            dealedAdvTO.setName(originalData[0]['Title'])
            dealedAdvTO.setIcon(originalData[0]['IconUrl'])
            dealedAdvTO.setOriginalType(originalData[0]['CateCode'])
            dealedAdvTO.setResourceType(8)
            dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
            dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
            dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
            dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
            dealedAdvTO.setTitle(originalAdvTO['TITLE'])
            dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
            dealedAdvTO.setGroupDescription(description)
            dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
            dealedAdvList.append(dealedAdvTO)
        conn.close()
    elif (groupType == GAME_POPULAR) or (groupType == ORIGINAL_POPULAR) or (groupType == GIFT_POPULAR) or (groupType == ACTIVITY_POPULAR):
        dealedAdvTO = DealedAdvTO()
        dealedAdvTO.setId(originalAdvTO['RESOURCE_ID'])
        dealedAdvTO.setResourceType(originalAdvTO['RESOURCE_TYPE'])
        dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
        dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
        dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
        dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
        dealedAdvTO.setTitle(originalAdvTO['TITLE'])
        dealedAdvTO.setUrl(originalAdvTO['URL'])
        dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
        dealedAdvTO.setOriginalType(originalAdvTO['ORIGINAL_TYPE'])
        dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
        dealedAdvList.append(dealedAdvTO)
    elif groupType == COMMENT_RANGK:
        url = "/comment/dailyRank?rankType=1&ps=50"
        conn = httplib.HTTPConnection("comment.d.cn")
        conn.request("GET", url)
        res = conn.getresponse()
        commentRankList = eval(res.read())
        conn.close()
        if not commentRankList or len(commentRankList) == 0:
            return []
        for commentRank in commentRankList:
            try:
                dealedAdvTO = DealedAdvTO()
                dealedAdvTO.setId(commentRank['rid'])
                dealedAdvTO.setName(commentRank['rname'])
                dealedAdvTO.setCommentAvatarUrl(commentRank['avatarUrl'])
                dealedAdvTO.setCommentGoodrat(commentRank['goodRat'])
                dealedAdvTO.setCommentContent(commentRank['content'])
                dealedAdvTO.setCommentUserId(int(commentRank['user']))
                dealedAdvTO.setCommentUserName(commentRank['name'])
                dealedAdvTO.setCommentId(commentRank['id_'])
                dealedAdvTO.setCommentIpAddress(commentRank['ipAddress'])
                dealedAdvTO.setCommentDevice(commentRank['device'])
                dealedAdvTO.setCommentPubTime(commentRank['pubTime'])
                dealedAdvTO.setResourceType(commentRank['rtype'])
                dealedAdvTO.setGroupType(originalAdvTO['GROUP_TYPE'])
                dealedAdvTO.setGroupId(originalAdvTO['GROUP_ID'])
                dealedAdvTO.setBackgroundImage(originalAdvTO['BACKGROUND_IMAGE'])
                dealedAdvTO.setGroupOrder(originalAdvTO['GROUP_ORDER'])
                dealedAdvTO.setTitle(originalAdvTO['TITLE'])
                dealedAdvTO.setGroupInnerOrder(originalAdvTO['ID'])
                dealedAdvTO.setLanguage(originalAdvTO['LANGUAGE'])
                dealedAdvList.append(dealedAdvTO)
            except Exception, ex:
                continue
    
    return dealedAdvList
        
#��ȡ�������ı���
def getTableNameForInsert():
    tableName = ''
    sql = "select TABLE_NAME from GAME_LIST_TABLE_STATUS where TYPE = '%s'" % INDEX_ADV_DIGUA_72_LIST_TYPE
    row = dbUtil_35.queryRow(sql)
    if row:
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
    dbUtil_35.truncate(sql)

#�������Ĺ��λ���ݲ������ݿ⣨����        
def insertResourceInfos(tableName, dealedAdvList):
    #���ñ���
    dbUtil_35.update("set names utf8mb4")

    insertsql = "INSERT INTO %s " % tableName
    insertsql += "(ID, NAME, EN_NAME, ICON, STARS, OUTLINE, PUBLISH_DATE, RESOURCE_TYPE, DATA_TYPE, CREATED_DATE, HOT_CNT, COMMENTS, CATEGORY_ID, CATEGORY_NAME, PKG_ID, PKG_NAME, PKG_PACKAGE_NAME, PKG_FILE_SIZE, PKG_URL, PKG_URL_SUFFIX, PKG_VERSION_NAME, PKG_VERSION_CODE, PKG_CPU_TYPE_SET, PKG_MIN_SDK, PKG_NEED_GOOGLE_FRAMEWORK, PKG_CREATED_DATE, GROUP_TYPE, GROUP_ID, GROUP_DESCRIPTION, BACKGROUND_IMAGE, GROUP_ORDER, TITLE, URL, GROUP_INNER_ORDER, COMMENT_AVATAR_URL, COMMENT_GOODRAT, COMMENT_CONTENT, COMMENT_USER_ID, COMMENT_USER_NAME, ORIGINAL_TYPE, COMMENT_ID, COMMENT_DEVICE, COMMENT_IP_ADDRESS, COMMENT_PUBLISH_TIME,LANGUAGE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    
    dataList = []
    for dealedAdvTO in dealedAdvList:
        if not dealedAdvTO:
            continue
        #cpu��minsdk���⴦��
        if dealedAdvTO.getPkgCpuTypeSet() == None:
            dealedAdvTO.setPkgCpuTypeSet(15)
        if dealedAdvTO.getPkgMinSdk() == None:
            dealedAdvTO.setPkgMinSdk(0)
        dataList.append((dealedAdvTO.getId(), 
                        dealedAdvTO.getName(), 
                        dealedAdvTO.getEnName(), 
                        dealedAdvTO.getIcon(), 
                        dealedAdvTO.getStars(), 
                        dealedAdvTO.getOutline(), 
                        dealedAdvTO.getPublishDate(), 
                        dealedAdvTO.getResourceType(), 
                        dealedAdvTO.getDataType(), 
                        dealedAdvTO.getCreatedDate(), 
                        dealedAdvTO.getHotCnt(), 
                        dealedAdvTO.getComments(), 
                        dealedAdvTO.getCategoryId(), 
                        dealedAdvTO.getCategoryName(), 
                        dealedAdvTO.getPkgId(), 
                        dealedAdvTO.getPkgName(), 
                        dealedAdvTO.getPkgPackageName(), 
                        dealedAdvTO.getPkgFileSize(), 
                        dealedAdvTO.getPkgUrl(), 
                        dealedAdvTO.getPkgUrlSuffix(), 
                        dealedAdvTO.getPkgVersionName(), 
                        dealedAdvTO.getPkgVersionCode(), 
                        dealedAdvTO.getPkgCpuTypeSet(), 
                        dealedAdvTO.getPkgMinSdk(), 
                        dealedAdvTO.getPkgNeedGoogleFramework(), 
                        dealedAdvTO.getPkgCreatedDate(), 
                        dealedAdvTO.getGroupType(), 
                        dealedAdvTO.getGroupId(), 
                        dealedAdvTO.getGroupDescription(), 
                        dealedAdvTO.getBackgroundImage(), 
                        dealedAdvTO.getGroupOrder(), 
                        dealedAdvTO.getTitle(), 
                        dealedAdvTO.getUrl(),
                        dealedAdvTO.getGroupInnerOrder(),
                        dealedAdvTO.getCommentAvatarUrl(),
                        dealedAdvTO.getCommentGoodrat(),
                        dealedAdvTO.getCommentContent(),
                        dealedAdvTO.getCommentUserId(),
                        dealedAdvTO.getCommentUserName(),
                        dealedAdvTO.getOriginalType(),
                        dealedAdvTO.getCommentId(),
                        dealedAdvTO.getCommentDevice(),
                        dealedAdvTO.getCommentIpAddress(),
                        dealedAdvTO.getCommentPubTime(),
                        dealedAdvTO.getLanguage()))
        if len(dataList) >= 1000:
            insertData(dbUtil_35, insertsql, dataList)
            dataList = []
    if dataList:
        insertData(dbUtil_35, insertsql, dataList)
        dataList = []

def insertData(dbUtil, sql, dataList):
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass
    
#���±������������б�ı���
def updateTableName(tableName):
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(), INDEX_ADV_DIGUA_72_LIST_TYPE)
    dbUtil_35.alter(sql)

#�������Ĺ����Ϣ���뵽���ݿ���
def insertDealedAdvData(dealedAdvList):
    #��ȡ����������
    tableName = getTableNameForInsert()
    print tableName

    #��մ�������
    clearTable(tableName)

    #��������
    insertResourceInfos(tableName, dealedAdvList)

    #���±������������б�ı���
    updateTableName(tableName)

#���������������ֻȡ����ǰ�����ַ�������ȡǰ�������ÿ�����ȡǰ�����ַ�
def dealWithCategoryName(orignalCategoryName):
    if not orignalCategoryName:
        return None
    
    categoryName = None
    names = orignalCategoryName.split(',')
    if len(names) > 1:
        categoryName = (names[0][0:2] if len(names[0]) > 2 else names[0]) + ',' + (names[1][0:2] if len(names[1]) > 2 else names[1])
    else:
        categoryName = names[0][0:2] if len(names[0]) > 2 else names[0]
    
    return categoryName
 
def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

class DealedAdvTO:
    def __init__(self):
        self.id = None
        self.name = None
        self.enName = None
        self.icon = None
        self.stars = None
        self.publishDate = None
        self.resourceType = None
        self.dataType = None
        self.createdDate = None
        self.hotCnt = None
        self.comments = None
        self.categoryId = None
        self.categoryName = None
        self.pkgId = None
        self.pkgName = None
        self.pkgPackageName = None
        self.pkgFileSize = None
        self.pkgUrl = None
        self.pkgUrlSuffix = None
        self.pkgVersionName = None
        self.pkgVersionCode = None
        self.pkgCpuTypeSet = None
        self.pkgMinSdk = None
        self.pkgNeedGoogleFramework = None
        self.pkgCreatedDate = None
        self.outline = None
        self.groupType = None
        self.groupId = None
        self.backgroundImage = None
        self.groupOrder = None
        self.title = None
        self.url = None
        self.groupInnerOrder = None
        self.commentAvatarUrl = None
        self.commentGoodrat = None
        self.commentContent = None
        self.commentUserId = None
        self.commentUserName = None
        self.commentId = None
        self.commentDevice = None
        self.commentIpAddress = None
        self.commentPubTime = None
        self.originalType = None
        self.groupDescription = None
        self.language = None
        
    def setId(self, id):
        self.id = id
        
    def getId(self):
        return self.id
        
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def setEnName(self, enName):
        self.enName = enName
        
    def getEnName(self):
        return self.enName

    def setIcon(self, icon):
        self.icon = icon
        
    def getIcon(self):
        return self.icon

    def setStars(self, stars):
        self.stars = stars
        
    def getStars(self):
        return self.stars

    def setPublishDate(self, publishDate):
        self.publishDate = publishDate
        
    def getPublishDate(self):
        return self.publishDate

    def setResourceType(self, resourceType):
        self.resourceType = resourceType
        
    def getResourceType(self):
        return self.resourceType

    def setDataType(self, dataType):
        self.dataType = dataType
        
    def getDataType(self):
        return self.dataType

    def setCreatedDate(self, createdDate):
        self.createdDate = createdDate
        
    def getCreatedDate(self):
        return self.createdDate

    def setHotCnt(self, hotCnt):
        self.hotCnt = hotCnt
        
    def getHotCnt(self):
        return self.hotCnt

    def setComments(self, comments):
        self.comments = comments
        
    def getComments(self):
        return self.comments

    def setCategoryId(self, categoryId):
        self.categoryId = categoryId
        
    def getCategoryId(self):
        return self.categoryId

    def setCategoryName(self, categoryName):
        self.categoryName = categoryName
        
    def getCategoryName(self):
        return self.categoryName

    def setPkgId(self, pkgId):
        self.pkgId = pkgId
        
    def getPkgId(self):
        return self.pkgId

    def setPkgName(self, pkgName):
        self.pkgName = pkgName
        
    def getPkgName(self):
        return self.pkgName

    def setPkgPackageName(self, pkgPackageName):
        self.pkgPackageName = pkgPackageName
        
    def getPkgPackageName(self):
        return self.pkgPackageName

    def setPkgFileSize(self, pkgFileSize):
        self.pkgFileSize = pkgFileSize
        
    def getPkgFileSize(self):
        return self.pkgFileSize

    def setPkgUrl(self, pkgUrl):
        self.pkgUrl = pkgUrl
        
    def getPkgUrl(self):
        return self.pkgUrl

    def setPkgUrlSuffix(self, pkgUrlSuffix):
        self.pkgUrlSuffix = pkgUrlSuffix
        
    def getPkgUrlSuffix(self):
        return self.pkgUrlSuffix

    def setPkgVersionName(self, pkgVersionName):
        self.pkgVersionName = pkgVersionName
        
    def getPkgVersionName(self):
        return self.pkgVersionName

    def setPkgVersionCode(self, pkgVersionCode):
        self.pkgVersionCode = pkgVersionCode
        
    def getPkgVersionCode(self):
        return self.pkgVersionCode

    def setPkgCpuTypeSet(self, pkgCpuTypeSet):
        self.pkgCpuTypeSet = pkgCpuTypeSet
        
    def getPkgCpuTypeSet(self):
        return self.pkgCpuTypeSet

    def setPkgMinSdk(self, pkgMinSdk):
        self.pkgMinSdk = pkgMinSdk
        
    def getPkgMinSdk(self):
        return self.pkgMinSdk

    def setPkgNeedGoogleFramework(self, pkgNeedGoogleFramework):
        self.pkgNeedGoogleFramework = pkgNeedGoogleFramework
        
    def getPkgNeedGoogleFramework(self):
        return self.pkgNeedGoogleFramework

    def setPkgCreatedDate(self, pkgCreatedDate):
        self.pkgCreatedDate = pkgCreatedDate
        
    def getPkgCreatedDate(self):
        return self.pkgCreatedDate

    def setOutline(self, outline):
        self.outline = outline
        
    def getOutline(self):
        return self.outline

    def setGroupType(self, groupType):
        self.groupType = groupType
        
    def getGroupType(self):
        return self.groupType

    def setGroupId(self, groupId):
        self.groupId = groupId
        
    def getGroupId(self):
        return self.groupId

    def setBackgroundImage(self, backgroundImage):
        self.backgroundImage = backgroundImage
        
    def getBackgroundImage(self):
        return self.backgroundImage

    def setGroupOrder(self, groupOrder):
        self.groupOrder = groupOrder
        
    def getGroupOrder(self):
        return self.groupOrder

    def setTitle(self, title):
        self.title = title
        
    def getTitle(self):
        return self.title

    def setUrl(self, url):
        self.url = url
        
    def getUrl(self):
        return self.url
        
    def setGroupInnerOrder(self, groupInnerOrder):
        self.groupInnerOrder = groupInnerOrder
        
    def getGroupInnerOrder(self):
        return self.groupInnerOrder

    def setCommentAvatarUrl(self, commentAvatarUrl):
        self.commentAvatarUrl = commentAvatarUrl
        
    def getCommentAvatarUrl(self):
        return self.commentAvatarUrl

    def setCommentGoodrat(self, commentGoodrat):
        self.commentGoodrat = commentGoodrat
        
    def getCommentGoodrat(self):
        return self.commentGoodrat

    def setCommentContent(self, commentContent):
        self.commentContent = commentContent
        
    def getCommentContent(self):
        return self.commentContent

    def setCommentUserId(self, commentUserId):
        self.commentUserId = commentUserId
        
    def getCommentUserId(self):
        return self.commentUserId

    def setCommentUserName(self, commentUserName):
        self.commentUserName = commentUserName
        
    def getCommentUserName(self):
        return self.commentUserName
        
    def setOriginalType(self, originalType):
        self.originalType = originalType
        
    def getOriginalType(self):
        return self.originalType
        
    def setGroupDescription(self, groupDescription):
        self.groupDescription = groupDescription
    
    def getGroupDescription(self):
        return self.groupDescription
 
    def setCommentId(self, commentId):
        self.commentId = commentId
        
    def getCommentId(self):
        return self.commentId

    def setCommentDevice(self, commentDevice):
        self.commentDevice = commentDevice
        
    def getCommentDevice(self):
        return self.commentDevice
        
    def setCommentIpAddress(self, commentIpAddress):
        self.commentIpAddress = commentIpAddress
        
    def getCommentIpAddress(self):
        return self.commentIpAddress
        
    def setCommentPubTime(self, commentPubTime):
        self.commentPubTime = commentPubTime
    
    def getCommentPubTime(self):
        return self.commentPubTime
    
    def setLanguage(self, language):
        self.language = language
    
    def getLanguage(self):
        return self.language
    
###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
       
        #��ȡ���λ�������(��̨��������)
        originalAdvList = getOriginalAdvData()
        print "��ȡ��ҳ��ѡ���λԭʼ���ݣ����ȣ�"+ str(len(originalAdvList))
        
        #����ÿ�����λ����ȡ������Ϣ
        dealedAdvList = []
        for originalAdvTO in originalAdvList:
            curDealedAdvList = dealWithOriginalAdv(originalAdvTO)
            dealedAdvList.extend(curDealedAdvList)
        
        #�������ݿ�
        insertDealedAdvData(dealedAdvList)
        
        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        print spentTime
        
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG

    finally:
        if dbUtil_35: dbUtil_35.close()
        if ERROR_MSG:
            sendMail()
