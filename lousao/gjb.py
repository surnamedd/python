#!/usr/bin/env python
#-*-coding:utf-8-*-
import httplib 
import urllib
import urllib2
import cookielib
import time
import os
import sys

tag = 1
domains= sys.argv[1]
domains = domains.split(',')

just_one = False

if len(sys.argv) == 3:
    just_one = True

while 1:
    try:
        for domain in domains:
            tag += 1
            print tag
            for url in open("20160830.txt"):
                test=open('result_404.txt','a+')
                test2=open('result_403.txt','a+')
                conn = httplib.HTTPConnection(domain)
                url = url.strip()
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
                conn.request("GET",url,headers=headers)
                res = conn.getresponse()
                #if(res.status==404):
                #    print >> test,url,"--------------",res.status,res.reason
                #else:
                #    print >> test2,url,"--------------",res.status,res.reason
                conn.close()
                test.close()
                test2.close()
                if just_one: break
            if just_one: break
    except:
        pass
    if just_one: break
