#python /usr/local/bin/cdroid/stat/android_download_daily_stat.py
#python /usr/local/bin/cdroid/stat/android_wdj_download_stat.py
#python /usr/local/bin/cdroid/stat/android_cooperation_download_stat.py
#python /usr/local/bin/cdroid/stat/android_cooperation_cdn_download_stat.py
#python /usr/local/bin/cdroid/stat/android_digua_cdn_download_stat.py
python /usr/local/bin/cdroid/stat/android_download_log_analysis.py --downloadFile=no --FILE_DATE=2014-06-01 
python /usr/local/bin/cdroid/stat/android_download_log_to_daily_stat.py --FILE_DATE=2014-06-01
python /usr/local/bin/cdroid/stat/android_download_daily_monitor_report.py --FILE_DATE=2014-06-01
#python /usr/local/bin/cdroid/stat/android_netgame_download_daily_stat.py
#python /usr/local/bin/cdroid/stat/android_netgame_download_log_to_daily_stat.py
#python /usr/local/bin/cdroid/stat/android_netgame_download_daily_monitor_report.py
python /usr/local/bin/cdroid/stat/netgame_download_stat.py --FILE_DATE=2014-06-01
python /usr/local/bin/cdroid/stat/cooperation_game_download_stat.py  --FILE_DATE=2014-06-01
python /usr/local/bin/cdroid/report/android_paid_game_down_report.py --FILE_DATE=2014-06-01
#python /usr/local/bin/cdroid/report/game_save_downs_top100_daily_report.py
#python /usr/local/bin/cdroid/report/android_top100_for_channel_flag_day_stat.py
#python /usr/local/bin/cdroid/report/android_web_down_top50_dayly_report.py
