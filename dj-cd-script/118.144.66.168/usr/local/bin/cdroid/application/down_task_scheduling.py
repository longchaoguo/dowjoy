#!/usr/bin/python
#-*-coding: cp936 -*-

from djutil.DBUtil import DBUtil
from djutil.DownloadDAO import DownloadTaskDAO
import datetime
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

todayDate = datetime.datetime.now()
#todayDate = datetime.date(2013,12,15)
createdDate = datetime.datetime.strftime(todayDate, '%Y-%m-%d')
y_m_d = datetime.datetime.strftime(todayDate - datetime.timedelta(days = 1), "%Y-%m-%d")
ymd = datetime.datetime.strftime(todayDate - datetime.timedelta(days = 1), "%y%m%d")
before_y_m_d = datetime.datetime.strftime(todayDate - datetime.timedelta(days = 2), "%Y-%m-%d")

dbUtil = DBUtil('stat_187')
execute = ScriptExecuteUtil(dbUtil = dbUtil, handleDate = todayDate)

def main():
    print "====download task start %s" % datetime.datetime.now()
    #createdDate='2012-06-15'
    taskDAO = DownloadTaskDAO()

    #安卓下载量 167
    
    taskId_ad_1 = taskDAO.addTask(dbUtil, 'ad_daily_187', 'python /usr/local/bin/cdroid/stat/android_download_daily_stat.py', '--FILE_DATE=' + y_m_d, None, '211.147.5.187', 103, createdDate)
    taskId_ad_2 = taskDAO.addTask(dbUtil, 'ad_wdj_187', 'python /usr/local/bin/cdroid/stat/android_wdj_download_stat.py', '--FILE_DATE=' + y_m_d, None, '211.147.5.187', 103, createdDate)
    temp_taskId_ad_3 = taskDAO.addTask(dbUtil, 'ad_cooperation_187', 'python /usr/local/bin/cdroid/stat/android_cooperation_download_stat.py', '--FILE_DATE=' + y_m_d, None, '211.147.5.187', 103, createdDate)
    taskId_ad_3 = taskDAO.addTask(dbUtil, 'ad_cooperation_187', 'python /usr/local/bin/cdroid/stat/android_cooperation_cdn_download_stat.py', '--FILE_DATE=' + y_m_d, None, '211.147.5.187', 103, createdDate)
    taskId_ad_4 = taskDAO.addTask(dbUtil, 'ad_digua_cdn_187', 'python /usr/local/bin/cdroid/stat/android_digua_cdn_download_stat.py', '--FILE_DATE=' + before_y_m_d, None, '211.147.5.187', 103, createdDate)
    taskId_ad_5 = taskDAO.addTask(dbUtil, 'ad_log_to_daily_187', 'python /usr/local/bin/cdroid/stat/android_download_log_to_daily_stat.py', '--FILE_DATE=' + y_m_d, str(taskId_ad_1) + ',' + str(taskId_ad_2)  + ',' + str(taskId_ad_4), '211.147.5.187', 100, createdDate)
    taskId_ad_6 = taskDAO.addTask(dbUtil, 'ad_daily_monitor_report_187', 'python /usr/local/bin/cdroid/stat/android_download_daily_monitor_report.py', '--FILE_DATE=' + y_m_d, str(taskId_ad_5), '211.147.5.187', 102, createdDate)
    taskId_ad_7=taskDAO.addTask(dbUtil, 'ad_netgame_187', 'python /usr/local/bin/cdroid/stat/android_netgame_download_daily_stat.py', '--FILE_DATE='+y_m_d, None, '211.147.5.187',103, createdDate)
    taskId_ad_8=taskDAO.addTask(dbUtil, 'ad_netgame_log_to_daily_187', 'python /usr/local/bin/cdroid/stat/android_netgame_download_log_to_daily_stat.py', '--FILE_DATE='+y_m_d, str(taskId_ad_7), '211.147.5.187',100, createdDate)
    taskId_ad_9=taskDAO.addTask(dbUtil, 'ad_netgame_daily_monitor_report_187', 'python /usr/local/bin/cdroid/stat/android_netgame_download_daily_monitor_report.py', '--FILE_DATE='+y_m_d, str(taskId_ad_7)+','+str(taskId_ad_8), '211.147.5.187',102, createdDate)
    taskId_ad_10=taskDAO.addTask(dbUtil, 'ad_cooperation_game_187', 'python /usr/local/bin/cdroid/stat/cooperation_game_download_stat.py', '--FILE_DATE=' + before_y_m_d, str(taskId_ad_6), '211.147.5.187', 103, createdDate)
    taskId_ad_11=taskDAO.addTask(dbUtil, 'ad_digua_stat_log_187', 'python /usr/local/bin/cdroid/temp/digua_stat_log_daily_stat.py', '--FILE_DATE=' + y_m_d, None, '211.147.5.187', 103, createdDate)
    taskId_ad_12=taskDAO.addTask(dbUtil, 'ad_digua_user_retention_187', 'python /usr/local/bin/cdroid/stat/digua_user_retention_stat.py', '--FILE_DATE=' + y_m_d, str(taskId_ad_11), '211.147.5.187', 103, createdDate)

    #187报表
    #move#report_mission=taskDAO.addTask(dbUtil, 'misson_daily_report_187', '/usr/local/bin/stat/report/mission_daily_report.py', '--STAT_DATE='+y_m_d, None, '211.147.5.187',100, createdDate)

    print "====download task end   %s" % datetime.datetime.now()

if __name__ == '__main__':

    try:
        execute.start(main)
    finally:
        if dbUtil: dbUtil.close()

