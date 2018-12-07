import vk_requests
import requests
import logging
import json
import time
import random
import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
#from vk_requests.auth import InteractiveVKSession


lister = []
tag = 'springveiv'
enterend = 2
end = enterend * 42

def getImageList():
    pid = 0
    maxPid = 84
    try:
        while pid != maxPid:
            url = "http://gelbooru.com/index.php?page=post&s=list&tags=%s&pid=%d" % (tag,pid)
            html = urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')
            imgs = soup.findAll("span", {"class":"thumb"})
            for img in imgs:
                apto = img.a['href'].split("imgurl=")
                lister.append(apto)

            pid += 42
            time.sleep(1)
            print ('Собрал страницу под номером %d' % (pid/42))
    except:
        print ('Что-то пошло не так')
    getimage()

def getimage():
    counter = 0
    while counter != end:
        uls = []
        lis = []
        finalimage = []
        for cleanlink in lister[counter]:
            siteurl = 'http://gelbooru.com/%s' % cleanlink
        html = urlopen(siteurl)
        soup = BeautifulSoup(html, 'html.parser')
        src = soup.findAll('img')[0]
        re1='.*?'	# Non-greedy match on filler
        re2='((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'
        rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
        m = rg.search(str(src))
        if m:
            httpurl1=m.group(1)
            print(httpurl1)
            finalimage.append(httpurl1)
            print('added')
            for image in finalimage[0]:
                print (image)
                saveimage = image
                req = requests.get(saveimage)
                out = open('D:/delete/%d.jpg' %(counter), 'wb')
                out.write(req.content)
                out.close()
                counter += 1
                time.sleep(1)
        else:
            print ('something wrong')

def getPid():
    pid = 0
    while True:
        url = "http://gelbooru.com/index.php?page=post&s=list&tags=%s&pid=%d" % (tag,pid)
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        findh1 = soup.findAll('h1')
        re1='.*?'
        re2='(Unable to search this deep in temporarily)'
        rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
        m = rg.search(str(findh1))
        if m:
            #word=m.group(1)
            pid -= 42 #goin' back for 1 step
            print("1st Limit found: #%d" % (pid))
            while True: #going down
                url = "http://gelbooru.com/index.php?page=post&s=list&tags=%s&pid=%d" % (tag,pid)
                html = urlopen(url)
                soup = BeautifulSoup(html, 'html.parser')
                findh1 = soup.findAll('h1')
                re1='.*?'
                re2='(Unable to search this deep in temporarily)'
                rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
                m = rg.search(str(findh1))
                if m:
                    pid -= 42
                    print ("pid substracted, now: #%d" % (pid))
                else:
                    print("2nd Limit found: #%d" % (pid))
                    return pid
        else:
            if pid == 0:
                pid += 42
            else:
                pid *= 2
            print ("pid added, now: #%d" % (pid))


getImageList()













        
