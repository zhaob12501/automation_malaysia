'''
@author: ZhaoBin
@file: automation_malaysia.py
Created on 2018/05/31
'''
from copy import copy
import json
import re
import sys
import time
from io import BytesIO
from random import random
from urllib import parse

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from Base import Base
from fateadm import Captcha
from pipelines import RedisQueue, Conn
from settings import ALIPAY_KEY, GLOBAL_DATA, NC, alipay_Keys, pool, redis, updateHttp

# from selenium.webdriver.support.ui import WebDriverWait

# 1-支付宝
alipay_user = GLOBAL_DATA[5]
alipay_pwd = GLOBAL_DATA[6]


class Automation_malaysia():
    '''
    注册马来西亚账号
    '''

    def __init__(self, res='', res_info='', res_group=''):
        print('start...')
        self.start_time = time.time()
        self.res = res
        self.email = res[1]
        self.password = res[2]
        self.res_info = res_info[0] if res_info else ""
        self.res_group = res_group[0] if res_group else ""
        print(self.email)
        self.req = requests.Session()

        # self.req.proxies = {
        #     "http": "127.0.0.1:8888",
        #     "https": "127.0.0.1:8888"
        # }
        # self.req.verify = False

        self.req.timeout = 300
        self.path = sys.path[0] + '\\'

        self.req.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        }
        self.registe_url = 'https://www.windowmalaysia.my/evisa/vlno_register.jsp?type=register'

    def application(self, filename=None):
        app = {
            "pdf": 'application/pdf',
            "jpg": 'image/jpg',
            "jpeg": 'image/jpeg',
            "png": 'image/png',
        }
        if filename:
            ex = filename.split(".")[-1]
            return app.get(ex, "image/jpg")
        return app

    def requ(self, url, data=None):
        print('in requ')  # , data)
        for _ in range(10):
            try:
                if not data:
                    print('in get')
                    res = self.req.get(url, timeout=10)
                    if res.status_code == 200:
                        # print(res.text)
                        break
                else:
                    print('in post')
                    res = self.req.post(url, data=data, timeout=10)
                    if res.status_code == 200:
                        # print(res.text)
                        break
            except Exception:
                continue
        # print(res)
        return res

    # 注册
    def registe(self):
        print('正在注册...')
        res = self.requ(self.registe_url)
        # 查询邮箱是否使用
        url = "https://www.windowmalaysia.my/evisa/vlno_ajax_checkUsername.jsp"
        email_res = self.req.post(url, data={"email": self.email}, timeout=10)
        if email_res.text.strip():
            # try:
            #     print('邮箱已被注册，更换邮箱...')
            #     url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/replaceEmail"
            #     data_p = {"email": self.email}
            #     res = requests.post(url, data_p, timeout=10).json()
            # except Exception:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data = {"email": self.email, "status": "1"}
            rs = requests.post(url, data=data, timeout=10)
            return 0

        data, _ = self.get_data(res)
        if not data.get("answer"):
            return
        re_url = 'https://www.windowmalaysia.my/evisa/register'
        res = self.requ(re_url, data=data)
        print('请求发送成功...进入判断...')
        if 'Resend Activation Email' in res.text:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data = {"email": self.email, "status": "1"}
            rs = requests.post(url, data=data, timeout=10)
            print(rs.json())
            print("注册成功...")
            # for _ in range(5):
            #     time.sleep(1)
            #     self.req.get(f'https://www.windowmalaysia.my/evisa/resendVerification?email={self.email}', timeout=10)
            return 1
        # Captcha(4, rsp=rsp)
        # print('注册失败!...')
        url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
        data = {"email": self.email, "status": "2"}
        rs = requests.post(url, data=data, timeout=10)
        print(rs.json())
        return 0

    def get_img(self, res=None):
        # url = "https://www.windowmalaysia.my/evisa/vlno_ajax_getToken.jsp"
        # img_tkn = parse.quote(self.requ(url).text)
        # url = "https://www.windowmalaysia.my/evisa/captchaImaging?tkn=%s&_=%s" % (img_tkn, int(time.time() * 1000))
        url = "https://www.windowmalaysia.my/evisa/captchaImaging?_=%s" % (int(time.time() * 1000))
        # answer = self.get_answer(res, timeout=10)
        # url = "https://www.windowmalaysia.my/evisa/captchaImaging"
        head = copy(self.req.headers)
        head["x-requested-with"] = "XMLHttpRequest"
        head["content-type"] = ""
        if res:
            head["referer"] = res.url
            head["accept"] = "*/*"
            head["accept-encoding"] = "gzip, deflate, br"
            head["accept-language"] = "zh-CN,zh;q=0.9"
        img = self.req.get(url, headers=head)
        # img.url
        imgs = img.content
        return imgs

    # 获取注册数据
    def get_data(self, res):
        print('in get_data')
        img = self.get_img(res)
        rsp = Captcha(1, img)
        # rsp = ""
        # answer = img
        answer = rsp.pred_rsp.value
        print("验证码为:", answer)

        reg = r'<input name="session_id" id="session_id" type="hidden" value="(.*?)">'
        da0 = re.findall(reg, res.text)[0]
        # print(da0)
        reg = r'<input name="ipAddress" id="ipAddress" type="hidden" value="(.*?)">'
        da1 = re.findall(reg, res.text)[0]
        # print(da1)
        reg = r'<input name="fullPage" id="fullPage" type="hidden" value="(.*?)">'
        da2 = re.findall(reg, res.text)[0]
        # print(da2)
        reg = r'<input name="locIPAddress" id="locIPAddress" type="hidden" value="(.*?)">'
        da3 = re.findall(reg, res.text)[0]
        # print(da3)
        reg = r'<input name="refImg" id="refImg" type="hidden" value="(.*?)">'
        da4 = re.findall(reg, res.text)[0]
        # print(da4)
        # print(len(self.res_info), len(self.res_group))
        data = {
            'session_id': da0,
            'ipAddress': da1,
            'fullPage': da2,
            'locIPAddress': da3,
            'refImg': da4,
            'firstName': self.res_info[31],
            'lastName': self.res_info[29],
            'nationality': '47',
            'nationalityhid': '47',
            'passportNo': str.lower(self.res_info[12]),
            'gender': 1 if self.res_info[3] == '男' else 2,
            'dob': f'{self.res_info[42]:0>2}/{self.res_info[41]:0>2}/{self.res_info[40]}',
            'dobDay': str(self.res_info[42]),
            'dobMonth': str(self.res_info[41]),
            'dobYear': str(self.res_info[40]),
            'address1': self.res_info[9],
            'address2': '',
            'postcode': self.res_info[26],
            'city': self.res_info[4],
            'country': '47',
            'phoneNumber': self.res_info[10],
            'email': self.email,
            'password': GLOBAL_DATA[4],
            'cPassword': GLOBAL_DATA[4],
            'answer': answer,
            'btnRegister': '注册',
        }
        print(3)
        # print(data)
        return data, rsp

    # 登录-填写信息-付款
    def login(self, cf=False):
        ri, rg = self.res_info, self.res_group
        if not rg[34]:
            updateHttp(where=f"gid={self.res[7]}", save={"ques": "航班未生成", "type": "0"})
            print("航班未生成")
            return "航班未生成"
        infos = ri[3] and ri[5] and ri[9] and ri[10] and ri[12] and ri[20] and ri[23] and \
            ri[24] and ri[25] and ri[26] and ri[29] and ri[31] and ri[32] and ri[33] and ri[34] and \
            ri[35] and ri[36] and ri[37] and rg[31] and rg[18] and rg[24] and rg[36]
        if not infos:
            updateHttp(where=f"gid={self.res[7]}", save={"type": 0, "ques": "信息不完整"})
            return "信息不完整"
        imgs = {i: f"{i}{self.res[7]}.png" for i in ["photo", "hz", "hb"]}
        try:
            # self.img_url(self.res, self.res_info, self.res_group)
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'

            res = self.req.get(index_url, timeout=10)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)"\s?/>'
            ipaddr = re.findall(reg, res.text)[0]
            # answer = self.get_answer(res)
            # url = "https://www.windowmalaysia.my/evisa/captchaImaging"
            # img = self.req.get(url, timeout=10).content

            img = self.get_img(res)
            rsp = Captcha(1, img)
            answer = rsp.pred_rsp.value
            # answer = upload(3060)
            print("验证码为:", answer)
            if not answer:
                return
            # ans = input(f"\n初次识别为: {answer}\n若无误, 请按回车\n若错误, 请在此输入新验证码：\n")
            # answer = ans if ans else answer

            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&txtEmail={self.email}&'\
                f'txtPassword={GLOBAL_DATA[4]}&answer={answer}&_={int(time.time()*1000)}'
            # print(url)
            res = self.req.get(url, timeout=10)
            print()
            print(res.json().get("status"))
            print()
            if res.json().get("status") == "conEstablished":
                return 0
            elif res.json().get("status") == "fail":
                url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                data_02 = {"email": self.email, "status": "4"}
                requests.post(url_02, data_02, timeout=10)
                # print("登录失败，重新激活！")
                return 0
            elif res.json().get("status") == "error":
                return 0
            # print(res.status_code)
            assert res.status_code == 200

            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url, timeout=10)

            reg = r"window\.location\.replace\('(.*?)'\);"
            join_evisa_url = re.findall(reg, res.text)

            if join_evisa_url == []:
                print('没有数据!...')
                return
            join_evisa_url = join_evisa_url[0]
            print('加入ENTRI计划')
            res = self.req.get(join_evisa_url, timeout=10)

            reg = r'<input type="hidden" name="checkAppNum\d" id="checkAppNum\d" value="(.*?)"\s?/>'
            uAppNumber = re.findall(reg, res.text)
            print(uAppNumber)
            # ======= 获取照片- 图片 ===========
            rsp_photo = requests.get(self.res_info[23], timeout=10).content

            if len(uAppNumber) == 1:
                uAppNumber = uAppNumber[0]
                if self.res[10] and uAppNumber != self.res[10]:
                    return
                print(uAppNumber)
                hisUrl = f'https://www.windowmalaysia.my/entri/check_payment_history.jsp?appNumber={uAppNumber}' \
                         f'&_={int(time.time()*1000)}'
                result = self.req.get(hisUrl, timeout=10).json()
                print(result)
                if result.get('tradeStatus') == 'success':
                    print(result.get('tradeStatus'))
                    visa_url = 'https://www.windowmalaysia.my/entri/note?appNumber=' + uAppNumber
                    pay_url = 'https://www.windowmalaysia.my/entri/jasperpayment?appNumber=' + uAppNumber
                    visa_data = {"email": self.email,
                                 "evisa": visa_url, "receipt": pay_url}
                    self.req.post(
                        "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data, timeout=10)
                    print("提取完成")
                    return 1
                print('in old visa')
                url = f'https://www.windowmalaysia.my/entri/registration.jsp?appNumber={uAppNumber}'
                # print(url)
                res = self.req.get(url, timeout=10)
                print('正在上传照片信息...')

                reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)"\s?/>'
                uUser = re.findall(reg, res.text)[0]

                _files = {
                    'uAppNumber': (None, uAppNumber),
                    'uUser': (None, uUser),
                    'uPhotoFile': ('photo.png', rsp_photo, 'image/png'),
                    'btnUploadPhoto': (None, '上传'),
                }
                res = self.req.post('https://www.windowmalaysia.my/entri/photo', files=_files, timeout=10)
                print('上传照片信息成功')
            elif len(uAppNumber) >= 2:
                url = "https://www.windowmalaysia.my/entri/historyServ"
                for i in range(len(uAppNumber)):
                    reg = fr'<input type="hidden" name="checkAppNum{i+1}" id="checkAppNum{i+1}" value="(.*?)"\s?/>'
                    data = {
                        "chkDel": "1",
                        "checkAppNum1": re.findall(reg, res.text)[0],
                    }
                    self.req.post(url, data=data)
                updateHttp(where=f"gid={self.res[7]}", save={"application": None})
                return
            else:
                print('in new visa')
                registe_url = 'https://www.windowmalaysia.my/entri/registration.jsp'
                res = self.req.get(registe_url, timeout=10)

                reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)"\s?/>'
                uAppNumber = re.findall(reg, res.text)[0]

                reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)"\s?/>'
                uUser = re.findall(reg, res.text)[0]

                print(
                    self.res[0] + '正在上传照片信息...time={}'.format(time.strftime('%H:%M:%S')))
                _files = {
                    'uAppNumber': (None, uAppNumber),
                    'uUser': (None, uUser),
                    'uPhotoFile': (
                        imgs["photo"], rsp_photo, 'image/png'),
                    'btnUploadPhoto': (None, '上传'),
                }
                # print(_files)
                res = self.req.post(
                    'https://www.windowmalaysia.my/entri/photo', files=_files, timeout=10)
                print('上传照片信息成功')

                reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)"\s?/>'
                uAppNumber = re.findall(reg, res.text)[0]

                # ======= 获取护照- 图片 ===========
                print(self.res[0] + '正在上传护照信息...time={}'.format(time.strftime('%H:%M:%S')))
                rsp_hz = requests.get(self.res_info[20], timeout=10).content
                _files1 = {
                    'uAppNumber': (None, uAppNumber),
                    'uUser': (None, uUser),
                    'uPassportFile': (imgs["hz"], rsp_hz, 'image/png'),
                    'btnUploadPassport': (None, '上传'),
                }
                res = self.req.post(
                    'https://www.windowmalaysia.my/entri/passport', files=_files1, timeout=10)
                print('上传护照信息成功')

                reg = r'<input type="hidden" name="appNumber" id="appNumber" value="(.*?)"\s?/>'
                uAppNumber = re.findall(reg, res.text)[0]
                time.sleep(1)

                # ======= 获取航班 图片 ===========
                print(
                    self.res[0] + '正在上传航班信息...time={}'.format(time.strftime('%H:%M:%S')))
                rsp_hb = requests.get(self.res_group[34], timeout=10).content
                _files = {
                    'uAppNumber': (None, uAppNumber),
                    'uUser': (None, uUser),
                    'uItineraryFile': ("hb.pdf", rsp_hb, self.application(self.res_group[34])),
                    'btnUploadItinerary': (None, '上传'),
                }
                res = self.req.post(
                    'https://www.windowmalaysia.my/entri/itinerary', files=_files, timeout=10)
                print('上传航班信息成功')

                if self.res_info[45]:
                    if self.res_info[45].split('.')[-1] == 'pdf':
                        print('正在上传其他信息...')
                        pdf = requests.get(self.res_info[45], timeout=10).content
                        _files1 = {
                            'uAppNumber': (None, uAppNumber),
                            'uUser': (None, uUser),
                            'uOtherFile': ('other.pdf', pdf, 'application/pdf'),
                            'btnUploadOtherDocument': (None, '上传'),
                        }
                        res = self.req.post(
                            'https://www.windowmalaysia.my/entri/itinerary', files=_files1, timeout=10)
                        print('上传其他信息成功')
                    else:
                        print('其他文件格式不正确')

            reg = r'<input type="hidden" name="appVisaNumber" id="appVisaNumber" value="(.*?)"\s?/>'
            appVisaNumber = re.findall(reg, res.text)[0]
            data = {
                'countryId': '47',
                'user': uUser,
                'appNumber': uAppNumber,
                'appVisaNumber': appVisaNumber,
                'appNationalityCode': 'CHN',
                'appNatCode': 'CHN',
                # 'appLastExitDt': '',
                # 'appLastExitDay': '0',
                # 'appLastExitMonth': '0',
                # 'appLastExitYear': '0',
                'appEmail': self.email,
                'appPurposeStay': '11',
                'expatCategory': '0',
                'principleName': '',
                'occupation': '',
                'expatRelationship': '0',
                'appFirstName': self.res_info[31],
                'appLastName': self.res_info[29],
                'appGender': 1 if self.res_info[3] == '男' else 2,
                'appDob': self.res_info[5],
                'appNationality': '47',
                'appPhoneNumber': self.res_info[10],
                'appDocType': '1',
                'appDocNumber': self.res_info[12],
                'appDocCountryIssued': '47',
                'appDocIssueDt': f'{self.res_info[34]:0>2}/{self.res_info[33]:0>2}/{self.res_info[32]}',
                'appDocIssuedDay': self.res_info[34],
                'appDocIssuedMonth': self.res_info[33],
                'appDocIssuedYear': self.res_info[32],
                'appDocExpiryDt': f'{self.res_info[37]:0>2}/{self.res_info[36]:0>2}/{self.res_info[35]}',
                'appDocExpiredDay': self.res_info[37],
                'appDocExpiredMonth': self.res_info[36],
                'appDocExpiredYear': self.res_info[35],
                'appTravelDtStart': f'{self.res_group[27]:0>2}/{self.res_group[26]:0>2}/{self.res_group[25]}',
                'appTravelDayStart': self.res_group[27],
                'appTravelMonthStart': self.res_group[26],
                'appTravelYearStart': self.res_group[25],
                'countryRouteMalaysia': '47',
                'countryTransitMalaysia': '0',
                'countryDestinationMalaysia': '131',
                'appEnterVia': 'Air',
                'appTravelDtEnd': f'{self.res_group[30]:0>2}/{self.res_group[29]:0>2}/{self.res_group[28]}',
                'appTravelDayEnd': self.res_group[30],
                'appTravelMonthEnd': self.res_group[29],
                'appTravelYearEnd': self.res_group[28],
                'countryRouteHome': '131',
                # 'countryTransitHome': '0',
                'countryDestinationHome': '47',
                # 'appExitVia': 'Air',
                'appAddress1': self.res_info[9],
                'appAddress2': '',
                'appPostcode': self.res_info[26],
                'appCity': self.res_info[25],
                'showProvince': 'true',
                'appProvince': self.res_info[24],
                'appMysAddress1': self.res_group[31].upper(),
                'appMysAddress2': self.res_group[18].upper(),
                'appMysPostcode': self.res_group[24],
                'appMysCity': self.res_group[36].upper(),
                'paymentMethod': 'alipay',
                'travelExceed': '0',
                'termCondition': 'on',
                'btnSave': 'AGREE'
            }
            # print(data)
            if self.timeout: return
            sql = "SELECT application From dc_business_email WHERE gid=%s" % self.res[7]
            con = Conn()
            application_in_mysql = con.select_one(sql)[0]
            if application_in_mysql and application_in_mysql != uAppNumber:
                return
            res = self.req.post(
                'https://www.windowmalaysia.my/entri/registration', data=data, timeout=10)
            if 'registration=alreadyExist' in res.url:
                res = self.req.get("https://www.windowmalaysia.my/entri/history.jsp")
                applications = re.findall(r'<td align="center">(\d+?)</td>', res.text)
                if len(applications):
                    return
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "重复提交", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo, timeout=10)
                print(_res.json())
                requests.get(
                    "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]), timeout=10)
                return
            elif 'registration=fail' in res.url:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "有效期内", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo, timeout=10)
                print(_res.json())
                requests.get(
                    "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]), timeout=10)
                return
            elif 'photo_editor' not in res.url:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "信息有误", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo, timeout=10)
                print(_res.json())
                requests.get(
                    "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]), timeout=10)
                return
            if not application_in_mysql:
                updateHttp(where=f"gid={self.res[7]}", save={"application": uAppNumber})
            # print(res)
            # 查看照片是否合格
            murl = 'https://www.windowmalaysia.my/entri/updatePhoto?appNumber=%s&dataX={0}&'\
                'dataY={1}&dataWidth={2}&dataHeight={3}&dataRotate=0&isEdit=true' % (uAppNumber)
            print(f'进入照片页--原照片')
            res = self.req.get(murl.format(0, 0, 213, 296), timeout=10)
            print('发送请求，进行照片判断')

            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if self.setPhoto(res, murl):
                    return -1

            time.sleep(3)
            # 支付宝付款
            print('准备进入支付宝付款')
            while True:
                res = self.req.get(
                    f'https://www.windowmalaysia.my/entri/payment.jsp?appNumber={uAppNumber}', timeout=10)
                # print(res.status_code)
                if res.status_code != 500:
                    break
                else:
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "2"}
                    self.req.post(url, data, timeout=10)
                    return -1

            ret = r'<input type="hidden" name="total_fee" id="total_fee" value="(.*?)">'
            total_fee = re.findall(ret, res.text)[0]

            ret = r'<input type="hidden" name="body" id="body" value="(.*?)">'
            body = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name="branchCode" id="branchCode" value="(.*?)">'
            branchCode = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name="keyOutTradeNo" id="keyOutTradeNo" value="(.*?)">'
            keyOutTradeNo = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name="user" id="user" value="(.*?)"\s?/>'
            user = re.findall(ret, res.text)[0]
            url = 'https://www.windowmalaysia.my/entri/split_alipayapi.jsp'
            data = {
                'subject': uAppNumber,
                'total_fee': total_fee,
                'body': body,
                'branchCode': branchCode,
                'keyOutTradeNo': keyOutTradeNo,
                'appNumber': uAppNumber,
                'user': user,
                'btnSubmit': '继续付款'
            }
            # print(data)

            res = self.req.post(url, data=data, timeout=10)
            subject = uAppNumber
            ret = r'<input type="hidden" name=\'sign\' value=\'(.*?)\'\s?/>'
            sign = re.findall(ret, res.text)[0]
            # print(sign)
            ret = r'<input type="hidden" name=\'split_fund_info\' value=\'(.*?)\'\s?/>'
            split_fund_info = re.findall(ret, res.text)[0]
            # print(split_fund_info)
            ret = r'<input type="hidden" name=\'notify_url\' value=\'(.*?)\'\s?/>'
            notify_url = re.findall(ret, res.text)[0]
            # print(notify_url)
            ret = r'<input type="hidden" name=\'body\' value=\'(.*?)\'\s?/>'
            body = re.findall(ret, res.text)[0]
            # print(body)
            ret = r'<input type="hidden" name=\'product_code\' value=\'(.*?)\'\s?/>'
            product_code = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'out_trade_no\' value=\'(.*?)\'\s?/>'
            out_trade_no = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'partner\' value=\'(.*?)\'\s?/>'
            partner = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'service\' value=\'(.*?)\'\s?/>'
            service = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'rmb_fee\' value=\'(.*?)\'\s?/>'
            rmb_fee = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'return_url\' value=\'(.*?)\'\s?/>'
            return_url = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'currency\' value=\'(.*?)\'\s?/>'
            currency = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'sign_type\' value=\'(.*?)\'\s?/>'
            sign_type = re.findall(ret, res.text)[0]
            apliay_url = f'https://mapi.alipay.com/gateway.do?subject={subject}&sign={sign}&split_fund_info={split_fund_info}&'\
                f'notify_url={notify_url}&body={body}&product_code={product_code}&out_trade_no={out_trade_no}&partner={partner}&'\
                f'service={service}&rmb_fee={rmb_fee}&return_url={return_url}&currency={currency}&sign_type={sign_type}'
            # 付款
            # self.pay(uAppNumber, apliay_url)
            # self.alipay(uAppNumber, apliay_url)
            if self.timeout: return
            red = RedisQueue(ALIPAY_KEY)
            print(red.hset(self.email, apliay_url))
            print(len(red.hgetall))
        except Exception as e:
            print(e)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "2"}
            requests.post(url, data, timeout=10)

    # 30天 登陆-付款
    def thLogin(self):
        ri, rg = self.res_info, self.res_group
        infos = ri[3] and ri[5] and ri[9] and ri[10] and ri[12] and ri[20] and ri[23] and \
            ri[24] and ri[25] and ri[26] and ri[29] and ri[31] and ri[32] and ri[33] and ri[34] and \
            ri[35] and ri[36] and ri[37] and rg[31] and rg[18] and rg[24] and rg[36]
        if not infos:
            updateHttp(where=f"gid={self.res[7]}", save={"type": 0, "ques": "信息不完整"})
            return "信息不完整"
        try:
            # self.img_url(self.res, self.res_info, self.res_group)
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'

            res = self.req.get(index_url, timeout=10)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)"\s?/>'
            ipaddr = re.findall(reg, res.text)[0]
            img = self.get_img(res)
            # img = self.req.get(url, timeout=10).content
            rsp = Captcha(1, img)
            answer = rsp.pred_rsp.value
            print("验证码为:", answer)
            if not answer:
                return
            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&'\
                f'txtEmail={self.email}&txtPassword={GLOBAL_DATA[4]}&answer={answer}&_={int(time.time()*1000)}'
            res = self.req.get(url, timeout=10)
            print(res.json())
            assert res.status_code == 200

            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url, timeout=10)

            # 30天签证
            print("点击 30 天签证")
            res = self.req.get(
                "https://www.windowmalaysia.my/evisa/vlno_center.jsp", timeout=10)

            reg = r'<input type="hidden" name="checkAppNum1" id="checkAppNum1" value="(.*?)"\s?/>'
            checkAppNum1 = re.findall(reg, res.text)
            if checkAppNum1:
                print("有旧记录")
                delurl = "https://www.windowmalaysia.my/evisa/center"
                data = {
                    "chkDel": "1",
                    "checkAppNum1": checkAppNum1[0],
                    "btnDel": "",
                }
                self.req.post(delurl, data=data, timeout=10)

            # 新建 旅游签证
            res = self.req.get("https://www.windowmalaysia.my/evisa/locations?evisaType=1", timeout=10)

            reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)"\s?/>'
            uUser = re.findall(reg, res.text)[0]
            # reg = r' <input type="hidden" name="uIndicator" id="uIndicator" value="(.*?)"\s?/>'
            # uIndicator = re.findall(reg, res.text)[0]
            reg = r'<input type="hidden" name="uApplicantId" id="uApplicantId" value="(.*?)"\s?/>'
            uApplicantId = re.findall(reg, res.text)[0]
            reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)"\s?/>'
            uAppNumber = re.findall(reg, res.text)[0]

            dobY, dobM, dobD = self.res_info[5].split("-")
            # print(self.res_info[12], self.res_info[5], uAppNumber)
            alertUrl = f"https://www.windowmalaysia.my/evisa/vlno_ajax_checkPassportNo.jsp?passportNo={self.res_info[12]}&"\
                f"nationality=CHN&dobDay={int(dobD)}&dobMonth={int(dobM)}&dobYear={dobY}&appNumber={uAppNumber.replace('/', '%2F')}"
            alert = self.req.get(alertUrl, timeout=10).text.strip()
            print("----\n", alert, "\n----")
            if alert:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "重复提交", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo, timeout=10)
                print(_res.json())
                requests.get("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]), timeout=10)
                return

            # -------------------------------------------------------------- #
            # ======= 获取照片 图片 ======================================= #
            rsp_photo = requests.get(self.res_info[23], timeout=10).content
            # ======= 获取护照 图片 ======================================= #
            rsp_hz = requests.get(self.res_info[20], timeout=10).content
            # ======= 获取航班 图片 ======================================== #
            rsp_hb = requests.get(self.res_group[34], timeout=10).content
            # -------------------------------------------------------------- #
            files = {
                "uUser": (None, uUser),
                "uIndicator": (None, "update"),
                "uApplicantId": (None, uApplicantId),
                "uAppNumber": (None, uAppNumber),
                "photo": ("photo.png", rsp_photo, 'image/png'),
                "passportphoto": ("hz.png", rsp_hz, 'image/png'),
                "passportphotoLast": ("hz.png", rsp_hz, 'image/png'),
                "itenaryDoc": ("hb.png", rsp_hb, 'image/png'),
                "bookingDoc": (None, ""),
                "otherDoc": (None, ""),
                "invitationDoc": (None, ""),
                "inventorDoc": (None, ""),
                "eclDoc": "",
                "cdlDoc": "",
                "invitationDocName": (None, ""),
                "itenaryDocName": (None, r"C:\fakepath\hb.png"),
                "bookingDocName": (None, ""),
                "otherDocName": (None, ""),
                "photoFileName": (None, r"C:\fakepath\photo.png"),
                "passportFileName": (None, r"C:\fakepath\hz.png"),
                "passportFileNameLast": (None, r"C:\fakepath\hz.png"),
                "inventorDocName": (None, ""),
                "eclDocName": "",
                "cdlDocName": "",
                "rowIdSelect": (None, ""),
                "appVisaType": (None, "1"),
                "appPurposeStay": (None, "20"),
                "appDurStay": (None, "1"),
                "appLastName": (None, self.res_info[29]),
                "appFirstName": (None, self.res_info[31]),
                "appDob": (None, f"{dobD}/{dobM}/{dobY}"),
                "dobDay": (None, f"{int(dobD)}"),
                "dobMonth": (None, f"{int(dobM)}"),
                "dobYear": (None, dobY),
                "nationality": (None, "47"),
                "appNationality": (None, "47"),
                "gender": (None, "1" if self.res_info[3] == "男" else "2"),
                "appPhoneNumber": (None, self.res_info[10]),
                "appEmailHid": (None, self.email),
                "underageDoc": (None, ""),
                "underageDocName": (None, ""),
                "appDocType": (None, "1"),
                "appDocNumber": (None, self.res_info[12]),
                "appDocCountryIssued": (None, "47"),
                "appDocNumberOld": (None, self.res_info[12]),
                "appDocIssuedDt": (None, f"{self.res_info[34]:0>2}/{self.res_info[33]:0>2}/{self.res_info[32]}"),
                "appDocIssuedDay": (None, str(self.res_info[34])),
                "appDocIssuedMonth": (None, str(self.res_info[33])),
                "appDocIssuedYear": (None, self.res_info[32]),
                "appDocExpiredDt": (None, f"{self.res_info[37]:0>2}/{self.res_info[36]:0>2}/{self.res_info[35]}"),
                "appDocExpiredDay": (None, str(self.res_info[37])),
                "appDocExpiredMonth": (None, str(self.res_info[36])),
                "appDocExpiredYear": (None, self.res_info[35]),
                "appMysAddress1": (None, self.res_group[31]),
                "appMysAddress2": (None, self.res_group[18]),
                "appAddress1": (None, self.res_info[9]),
                "appAddress2": (None, ""),
                "appMysPostcode": (None, self.res_group[24]),
                "appPostcode": (None, self.res_info[26]),
                "appMysCity": (None, self.res_group[36]),
                "appCity": (None, self.res_info[25]),
                "appProvince2": (None, self.res_info[24]),
                "country": (None, "47"),
                "appUnderageStatusHid": (None, "0"),
                "lastPagePhotoStatus": (None, "1"),
                "appDocNumberOldStatus": (None, "1"),
                "currUserCountry": (None, "CHINA"),
                "reasonToReapply": (None, "0"),
                "hdtPassportNoHitMultiple": (None, "0"),
                "firstDe": (None, "0"),
            }

            if self.res_info[45]:
                files["otherDoc"] = ("other.pdf", requests.get(self.res_info[45]).content, self.application(self.res_info[45]))
                files["otherDocName"] = (None, r"C:\fakepath\other.pdf")
            if self.res_info[47]:
                files["underageDoc"] = ("other.pdf", requests.get(self.res_info[47]).content, self.application(self.res_info[47]))
                files["underageDocName"] = (None, r"C:\fakepath\other.pdf")
            if self.res_group[44]:
                files["bookingDoc"] = ("jd.pdf", requests.get(self.res_group[44]).content, self.application(self.res_group[44]))
                files["bookingDocName"] = (None, r"C:\fakepath\jd.pdf")

            url = "https://www.windowmalaysia.my/evisa/applications"
            # res = self.req.post(url, data=data, files=file, timeout=10)
            res = self.req.post(url, files=files, timeout=10)
            print("\n信息上传完成，进入照片判断\n")

            reg = f"appNumber={uAppNumber}&appId=(.*?)['\\\"]"
            appId = re.findall(reg, res.text)[0]
            # """ with open("a.html", "wb") as f: f.write(res.content) """
            # 查看照片是否合格
            # """ https://www.windowmalaysia.my/evisa/updatePhoto?appNumber=%s&appId=%s&dataX={}&dataY={}&dataWidth={}&dataHeight={}&dataRotate=0&idKeyProc=0&isEdit=true&evisaType=1
            # """
            size = Image.open(BytesIO(rsp_photo)).size
            murl = "https://www.windowmalaysia.my/evisa/updatePhoto?appNumber=%s&appId=%s&dataX={}&dataY={}"\
                "&dataWidth={}&dataHeight={}&dataRotate=0&idKeyProc=0&isEdit=true&evisaType=1" % (
                    uAppNumber, appId
                )
            print(f'进入照片页--原照片')
            res = self.req.get(murl.format(0, 0, *size), timeout=10)
            print('发送请求，进行照片判断')

            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if self.setPhoto(res, murl, size):
                    return -1
            if "照片可以接受" in res.text:
                print("照片上传成功")
            else:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.email, "status": "2"}
                requests.post(url, data, timeout=10)

                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "照片不合格"}
                print('123s')
                print(data_photo)
                requests.post(url, data_photo, timeout=10)
                return -1

            okurl = f"https://www.windowmalaysia.my/evisa/updateRotation?rotPhotoP=0&rotPpt=0&rotPptL=0&"\
                f"applicantId={uApplicantId}&appNumber={uAppNumber}"
            res = self.req.get(okurl, timeout=10)

            r"""
                <input type="hidden" name="appTotal" id="appTotal" value="1"\s?/>
                <input type="hidden" name="ccNumber" id="ccNumber" value=""\s?/>
                <input type="hidden" name="expiryDate" id="expiryDate" value=""\s?/>
                <input type="hidden" name="branchCurrency" id="branchCurrency" value="RMB"\s?/>
                <input type="hidden" name="branchCode" id="branchCode" value="1034121"\s?/>
                <input type="hidden" name="appDocNumber" id="appDocNumber" value="G59897649"\s?/>
                <input type="hidden" name="appDocNationality" id="appDocNationality" value="CHN"\s?/>
                <input type="hidden" name="visaFee" id="visaFee" value="80.0"\s?/>
                <input type="hidden" name="convenienceFee" id="convenienceFee" value="0.0"\s?/>
                <input type="hidden" name="courierFee" id="courierFee" value="0.0"\s?/>
                <input type="hidden" name="processingFee" id="processingFee" value="200.0"\s?/>
                <input type="hidden" name="totalFee" id="totalFee" value="280.0"\s?/>
                <input type='hidden' id='payMethodId' name='payMethodId' value='21'\s?/>
                <input type="radio" name="paymentType" class="cpaytype" id="paymentType" value="alipaysplit">
            """

            reg = r'<input type="hidden" name="branchCode" id="branchCode" value="(.*?)"\s?/>'
            branchCode = re.findall(reg, res.text)
            branchCode = branchCode[0]
            reg = r'<input type=\'hidden\' id=\'payMethodId\' name=\'payMethodId\' value=\'(.*?)\'\s?/>'
            payMethodId = re.findall(reg, res.text)
            payMethodId = payMethodId[0]

            alpayurl = f'https://www.windowmalaysia.my/evisa/previews?appNumber={uAppNumber.replace("/", "%2F")}&appTotal=1&ccNumber=&'\
                f'expiryDate=%2F&branchCurrency=RMB&branchCode={branchCode}&appDocNumber={self.res_info[12]}&appDocNationality=CHN&'\
                f'visaFee=80.0&convenienceFee=0.0&courierFee=0.0&processingFee=200.0&totalFee=280.0&payMethodId={payMethodId}&'\
                f'paymentType=alipaysplit&cc_no1=&cc_no2=&cc_no3=&cc_no4=&ccv=&cc_mm=&cc_yy=&cc_name=&confirmDetail=on&btnNext2='
            res = self.req.get(alpayurl, timeout=10)
            reg = r'<input type="hidden" name="out_trade_no" id="out_trade_no" value="(.*?)">'
            out_trade_no = re.findall(reg, res.text)
            reg = r'<input type="hidden" name="branchId" id="branchId" value="(.*?)">'
            branchId = re.findall(reg, res.text)
            reg = r'<input type="hidden" name="appNumberAP" id="appNumberAP" value="(.*?)">'
            appNumberAP = re.findall(reg, res.text)

            aurl = "https://www.windowmalaysia.my/evisa/split_alipayapi.jsp"
            data = {
                "out_trade_no": out_trade_no,
                "branchId": branchId,
                "appNumberAP": appNumberAP,
            }
            res = self.req.post(aurl, data=data, timeout=10)
            subject = uAppNumber
            ret = r'<input type="hidden" name=\'sign\' value=\'(.*?)\'\s?/>'
            sign = re.findall(ret, res.text)[0]
            # print(sign)
            ret = r'<input type="hidden" name=\'split_fund_info\' value=\'(.*?)\'\s?/>'
            split_fund_info = re.findall(ret, res.text)[0]
            # print(split_fund_info)
            ret = r'<input type="hidden" name=\'notify_url\' value=\'(.*?)\'\s?/>'
            notify_url = re.findall(ret, res.text)[0]
            # print(notify_url)
            ret = r'<input type="hidden" name=\'body\' value=\'(.*?)\'\s?/>'
            body = re.findall(ret, res.text)[0]
            # print(body)
            ret = r'<input type="hidden" name=\'product_code\' value=\'(.*?)\'\s?/>'
            product_code = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'out_trade_no\' value=\'(.*?)\'\s?/>'
            out_trade_no = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'partner\' value=\'(.*?)\'\s?/>'
            partner = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'service\' value=\'(.*?)\'\s?/>'
            service = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'rmb_fee\' value=\'(.*?)\'\s?/>'
            rmb_fee = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'return_url\' value=\'(.*?)\'\s?/>'
            return_url = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'currency\' value=\'(.*?)\'\s?/>'
            currency = re.findall(ret, res.text)[0]
            ret = r'<input type="hidden" name=\'sign_type\' value=\'(.*?)\'\s?/>'
            sign_type = re.findall(ret, res.text)[0]
            apliay_url = f'https://mapi.alipay.com/gateway.do?subject={subject}&sign={sign}&split_fund_info={split_fund_info}&'\
                f'notify_url={notify_url}&body={body}&product_code={product_code}&out_trade_no={out_trade_no}&partner={partner}&'\
                f'service={service}&rmb_fee={rmb_fee}&return_url={return_url}&currency={currency}&sign_type={sign_type}'
            # 付款
            # self.pay(uAppNumber, apliay_url)
            # self.alipay(uAppNumber, apliay_url)
            red = RedisQueue(ALIPAY_KEY)
            print(red.hset(self.email, apliay_url))
            print(len(red.hgetall))
        except Exception as e:
            print(e)
            time.sleep(10)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "2"}
            requests.post(url, data, timeout=10)

    # 获取电子签模块
    def get_visa(self):
        try:
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'

            res = self.req.get(index_url, timeout=10)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)"\s?/>'
            ipaddr = re.findall(reg, res.text)[0]
            # answer = self.get_answer(res)
            img = self.get_img(res)
            # img = self.req.get(url, timeout=10).content
            rsp = Captcha(1, img)
            answer = rsp.pred_rsp.value
            print("验证码为:", answer)
            if not answer:
                return
            # ans = input(f"\n初次识别为: {answer}\n若无误, 请按回车\n若错误, 请在此输入新验证码：\n")

            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&txtEmail={self.email}&txtPassword={GLOBAL_DATA[4]}&'\
                f'answer={answer}&_={int(time.time()*1000)}'
            # print(url)
            res = self.req.get(url, timeout=10)
            # print(self.req.headers)
            print(res.text)
            if res.json().get("status") != "success":
                # Captcha(4, rsp=rsp)
                # print("登录失败，重新登陆！")
                return 0
            assert res.status_code == 200
            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url, timeout=10)

            reg = r"window\.location\.replace\('(.*?)'\);"
            join_evisa_url = re.findall(reg, res.text)

            if join_evisa_url == []:
                print('没有数据!...')
                return
            join_evisa_url = join_evisa_url[0]
            print('加入ENTRI计划')
            res = self.req.get(join_evisa_url, timeout=10)
            try:
                appnumber = res.text.split('appNumber=')[1].split('">')[0]
            except Exception:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.res[1], "status": "2"}
                requests.post(url, data, timeout=10)
                return
            print(appnumber)
            if '繼續' not in res.text:
                print('签证已出，正在提取...')

            else:
                print('签证未出，执行查询后提取...')
                payUrl = 'https://www.windowmalaysia.my/entri/payment.jsp?appNumber=' + appnumber
                hisUrl = f'https://www.windowmalaysia.my/entri/check_payment_history.jsp?appNumber={appnumber}&_={int(time.time()*1000)}'
                self.req.get(payUrl, timeout=10)
                result = self.req.get(hisUrl, timeout=10).json()
                print(result)
                if result.get('tradeStatus') == 'success':
                    print('签证已出，正在提取...')
                elif result == {}:
                    print('未付款,重新付款...')
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "2"}
                    requests.post(url, data, timeout=10)
                    return 2
                else:
                    visa_data = {"email": self.email}
                    self.req.post(
                        "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
                    # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                    return 1
            visa_url = 'https://www.windowmalaysia.my/entri/note?appNumber=' + appnumber
            pay_url = 'https://www.windowmalaysia.my/entri/jasperpayment?appNumber=' + appnumber
            visa_data = {"email": self.email,
                         "evisa": visa_url, "receipt": pay_url}
            self.req.post(
                "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data, timeout=10)
            print('提取完成')
            with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                json.dump(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 电子签获取成功!", f)
                f.write('\n],\n')
                time.sleep(1)
            return 0

        except Exception:
            visa_data = {"email": self.email}
            self.req.post(
                "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data, timeout=10)
            # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"

    # 照片判断
    def setPhoto(self, res, murl, size=None):
        if size:
            width, height = size
        else:
            width = 141.84
            height = 200
        i = 20
        while i >= -20:
            print(f'进入照片页， 控制1: {i}')
            url = murl.format(i, i, width - i, height - i * 1.41)
            res = self.req.get(url, timeout=10)
            print('发送请求，进行照片判断')

            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if i != 2:
                    i -= 2
                else:
                    i = -2
                continue
            print('照片通过')
            time.sleep(5)
            break
        if i < -20:
            i = 2
            while i <= 20:
                print(f'进入照片页， 控制2: {i}')
                url = murl.format(i, 0, width - i, height - i * 1.41 * 2)
                res = self.req.get(url, timeout=10)
                print('发送请求，进行照片判断')

                if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                    i += 2
                    continue
                print('照片通过')
                time.sleep(5)
                break
        if i > 20:
            i = 24
            while i >= -24:
                print(f'进入照片页， 控制3: {-i}')
                url = murl.format(0, -i, width, height - i * 1.41)
                res = self.req.get(url, timeout=10)
                print('发送请求，进行照片判断')

                if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                    i -= 3
                    continue
                print('照片通过')
                time.sleep(5)
                break
            else:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.email, "status": "2"}
                requests.post(url, data, timeout=10)

                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "照片不合格"}
                print('123s')
                print(data_photo)
                requests.post(url, data_photo, timeout=10)
                # updateHttp(where=f"email={self.res[1]}", save={"ques": "照片不合格", "type": "0"})
                return 1
        return 0

    #判断任务是否超时
    @property
    def timeout(self):
        return time.time() - self.start_time > 300
