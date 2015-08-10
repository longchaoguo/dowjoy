#!/usr/bin/python
# -*- #coding:UTF-8
__author__ = "$Author: helin $"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/07/11 16:51:57 $"

from django.conf.urls.defaults import *
from resopt.views import getFileSize
from resopt.views import deleteFile
from resopt.views import flushImgAndroidDCnCdn

urlpatterns = patterns('',
    url(r'^file$', getFileSize),
    url(r'^delete$', deleteFile),
    url(r'^flushImgAndroidDCnCdn$', flushImgAndroidDCnCdn),
)