#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django.contrib import admin
from javalog.models import *

class JavalogAdmin(admin.ModelAdmin):
    list_display = ('username','name','process','idc','ip','dir')
class RedisAdmin(admin.ModelAdmin):
    list_display = ('username','idc','ip')
class ZookeeperAdmin(admin.ModelAdmin):
    list_display = ('username','idc','ip')
class PasswdAdmin(admin.ModelAdmin):
    list_display = ('name','passwd')
class DblogAdmin(admin.ModelAdmin):
    list_display = ('username','dbname','ip')
class CdnlogAdmin(admin.ModelAdmin):
    list_display = ('username','site','cdn','pv','size','hit','bad','day','detail')
admin.site.register(Javalog,JavalogAdmin)
admin.site.register(Redis,RedisAdmin)
admin.site.register(Zookeeper,ZookeeperAdmin)
admin.site.register(Passwd,PasswdAdmin)
admin.site.register(Dblog,DblogAdmin)
admin.site.register(Cdnlog,CdnlogAdmin)
