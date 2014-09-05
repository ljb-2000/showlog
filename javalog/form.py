#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django import forms

class upfileForm(forms.Form):
    file = forms.FileField(label='选择文件')

class downfileForm(forms.Form):
    file = forms.CharField(label = '选择文件')
