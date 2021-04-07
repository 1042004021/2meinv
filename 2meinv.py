
from urllib import request
from bs4 import BeautifulSoup
import re
import time
import _thread
import os
import threading

import sys
import requests



search = str(input('请输入你要爬取的图片（如少女）：'))
print('长在搜索'+search)
url = 'https://www.2meinv.com/search-'+search+'.html'
# url ='https://www.2meinv.com/tags-%E5%B0%91%E5%A5%B3%E6%98%A0%E7%94%BB.html'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36', 'Referer': 'https://www.2meinv.com/tags-%E5%B0%91%E5%A5%B3%E6%98%A0%E7%94%BB.html'}
page = request.Request(url,headers=headers)
page_info = requests.get(url, headers=headers)
links = page_info.text
links = re.findall('<a href="(.*?)"  target="_blank" class="dl-pic"><img src="(.*?)" alt="(.*?)"></a>',links)




def getImgs(threadName,url,lock):
    #爬取title用于创建文件目录
    page = requests.get(url, headers=headers)
    page_info = page.text
    # < span > (21 / 22) < / span >
    num = re.findall('<span>(.*?)</span>',page_info)
    num = num[0].replace(" ", "")

    #获取总页数
    all = re.findall('/(.*?)\)',num)


    #获取当前页数
    now = re.findall('\((.*?)/',num)


    # < title > 元气性感少女苏菲菲超短裙尽显蜜桃熟时_爱美女 < / title >
    title = re.findall('<title>(.*?)</title>',page_info)

    dir = title[0]

    # <a href="https://www.2meinv.com/article-1627.html"><img src="https://www.2meinv.com/a1503/2019-01-23/1548227325zp43.jpg" alt=
    img = re.findall('<a href="(.*?)"><img src="(.*?)" alt',page_info)[0][1]
    photo = requests.get(img, headers=headers)
    photo = photo.content
    # print(img)
    dirs = './'+search+'/'


    #创建目录
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    #判断图片是否爬取
    #下载当前页的图片
    if not os.path.exists(dirs + str(time.time()) + '.jpg'):
        with open(dirs + str(time.time()) + '.jpg', 'wb') as f:
            f.write(photo)
            print ('爬取'+threadName+"--"+dirs+'第'+now[0]+'/'+all[0])
            f.close()
        if now[0]==all[0]:
             print('爬取完毕')
             lock.release()
        else:
            # 获取下一页的链接
            # <a href="https://www.2meinv.com/article-1628-21.html">下一页</a>
            next = re.findall('<a href="(.*?)">下一页</a>',page_info)
            new_url = next[0]
            
            #将下一页的链接传入当前函数下载下一页的图片
            try:
                getImgs(threadName,new_url,lock)
            except:
                    print(threadName+"--"+now[0]+"---"+all[0])
                    print("服务器异常，正在重试")
                    getImgs(threadName,url,lockl)

    

i = 0
locks=[]
for link in links:
    lock = _thread.allocate_lock()   #创建锁对象
    lock.acquire()
    locks.append(lock)
    i+=1
    url = link[0]
    _thread.start_new_thread(getImgs, ('thread-'+str(i),url,lock))
    print('创建线程:thread'+str(i))
    print(lock)
for j in range(i):
    while locks[j].locked():
        time.sleep(1)
        
print('所有资源爬取完毕')