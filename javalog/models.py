#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django.db.models import *
from django.contrib.auth.models import User

class Javalog(Model):
    username = CharField(max_length=50)
    name = CharField(max_length=100)
    process = CharField(max_length=100)
    idc = CharField(max_length=50)
    ip = CharField(max_length=100)
    dir = CharField(max_length=500)
    def __unicode__(self):
        return self.username
class Redis(Model):
    username = CharField(max_length=50)
    idc = CharField(max_length=50)
    ip = CharField(max_length=100)
    def __unicode__(self):
        return self.username
class Zookeeper(Model):
    username = CharField(max_length=50)
    idc = CharField(max_length=50)
    ip = CharField(max_length=100)
    def __unicode__(self):
        return self.username
class Passwd(Model):
    name = CharField(max_length=50)
    passwd = CharField(max_length=50)
    def __unicode__(self):
        return self.name
class Dblog(Model):
    username = CharField(max_length=50)
    dbname = CharField(max_length=100)
    ip = CharField(max_length=100)
    def __unicode__(self):
        return self.username
class Cdnlog(Model):
    username = CharField(max_length=50)
    name = CharField(max_length=100)
    cdn = CharField(max_length=100)
    pv = CharField(max_length=100)
    size = CharField(max_length=100)
    hit = CharField(max_length=100)
    bad = CharField(max_length=100)
    days = CharField(max_length=100)
    def __unicode__(self):
        return self.username
