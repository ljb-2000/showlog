#!/usr/bin/env python
#coding=utf-8
import sys, os, datetime, time
import db_connector
from django.core.mail import send_mail
from javalog.models import *
from javalog.comm import *



#Cdnlog.objects.all().delete()
day = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d") 
d = day[-2:]
f = "/data/download/cdn/%s" % day
Cdnlog.objects.filter(day=day).delete()
ret = os.popen("grep '访问量' %s" % f).readlines()
for i in ret:
    cdn = i.split()[0]
    site = i.split()[1]
    pv = i.split()[3]
    size = i.split()[5]
    Cdnlog.objects.create(username='root',site=site,cdn=cdn,pv=pv,size=size,day=day,hit="0%",bad="0%")
    f1 = open('/data/download/cdn/%s_%s_%s_tmp' %(cdn,site,d))
    detail = f1.read()
    f1.close()
    Cdnlog.objects.filter(username='root',site=site,cdn=cdn,day=day).update(detail=detail)

ret = os.popen("grep '命中率' %s" % f).readlines()
for i in ret:
    cdn = i.split()[0]
    site = i.split()[1]
    hit = i.split()[-1]
    if not "%" in hit:
        hit = "0%"
    Cdnlog.objects.filter(username='root',site=site,cdn=cdn,day=day).update(hit=hit)

ret = os.popen("""grep '整体加速效果不佳的比例' %s |awk '$4!=""'""" % f).readlines()
for i in ret:
    cdn = i.split()[0]
    site = i.split()[1]
    bad = i.split()[-1]
    Cdnlog.objects.filter(username='root',site=site,cdn=cdn,day=day).update(bad=bad)

#删除30天前的详情日志
ds = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y%m%d")
Cdnlog.objects.filter(day__lt=ds).update(detail="")
