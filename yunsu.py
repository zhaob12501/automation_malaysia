#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, hashlib, os, random, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
from datetime import *
import operator
import json


with open('settings.json') as f:
    USER = json.load(f)

class APIClient(object):
    def http_request(self, url, paramDict):
        post_content = ''
        for key in paramDict:
            post_content = post_content + '%s=%s&'%(key,paramDict[key])
        post_content = post_content[0:-1]
        #print post_content
        req = urllib.request.Request(url, data=post_content)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())  
        response = opener.open(req, post_content)  
        return response.read()

    def http_upload_image(self, url, paramKeys, paramDict, filebytes):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        boundary = '------------' + hashlib.md5(timestr.encode('utf8')).hexdigest().lower()
        boundarystr = '\r\n--%s\r\n'%(boundary)
        
        bs = b''
        for key in paramKeys:
            bs = bs + boundarystr.encode('ascii')
            param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s"%(key, paramDict[key])
            #print param
            bs = bs + param.encode('utf8')
        bs = bs + boundarystr.encode('ascii')
        
        header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n'%('sample')
        bs = bs + header.encode('utf8')
        
        bs = bs + filebytes
        tailer = '\r\n--%s--\r\n'%(boundary)
        bs = bs + tailer.encode('ascii')
        
        import requests
        headers = {'Content-Type':'multipart/form-data; boundary=%s'%boundary,
                   'Connection':'Keep-Alive',
                   'Expect':'100-continue',
                   }
        response = requests.post(url, params='', data=bs, headers=headers)
        return response.text


    


def arguments_to_dict(args):
    argDict = {}
    if args is None:
        return argDict
    
    count = len(args)
    if count <= 1:
        print('exit:need arguments.')
        return argDict
    
    for i in [1,count-1]:
        pair = args[i].split('=')
        if len(pair) < 2:
            continue
        else:
            argDict[pair[0]] = pair[1]

    return argDict
    
 
def upload(typeid=7111, t=60):
    client = APIClient()
    paramDict = {}
    result = ''
    while 1:
        paramDict['username'] = USER[3]
        paramDict['password'] = USER[4]
        paramDict['typeid'] = typeid
        paramDict['timeout'] = t
        paramDict['softid'] = '72395'
        paramDict['softkey'] = 'd9c016640d33412ca0dacd23a0091f5c'
        paramKeys = ['username',
             'password',
             'typeid',
             'timeout',
             'softid',
             'softkey'
            ]
        from PIL import Image
        imagePath = 'code_yunsu.png'
        img = Image.open(imagePath)
        if img is None:
            print('get file error!')
            continue
        img.save("upload.gif", format="gif")
        filebytes = open("upload.gif", "rb").read()
        result = client.http_upload_image("http://api.ysdm.net/create.xml", paramKeys, paramDict, filebytes)

        if "10301" in result:
            print("余额不足")
            time.sleep(5)
            return -1
        result = result.split('<Result>')[1].split('</Result>')[0]
        if typeid == 6903:
            result = result.split('.')
        #os.remove('code_yunsu.png')
        os.remove('upload.gif')
        
        return result

if __name__ == '__main__':
    res = upload()
    print(res)
