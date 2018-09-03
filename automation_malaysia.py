'''
@author: ZhaoBin
@file: automation_malaysia.py 
Created on 2018/05/31
'''
import datetime
import hashlib
import json
import sys
import os
import re
import time
import pymysql
import requests
from pymysql import connect
from PIL import Image
from yunsu import upload
from pymouse import PyMouse
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from DBUtils.PooledDB import PooledDB
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC


with open('settings.json', 'r') as f:
    GLOBAL_DATA = json.load(f)

POOL = PooledDB(
    pymysql,
    3,
    host=GLOBAL_DATA[0],
    user=GLOBAL_DATA[1],
    passwd=GLOBAL_DATA[2],
    db=GLOBAL_DATA[3],
    port=3306,
    charset="utf8"
)

class Automation_malaysia():
    '''
    注册马来西亚账号
    '''

    def __init__(self, res='', res_info='', res_group=''):
        print('start...')
        self.res = res
        self.email = res[1]
        self.password = res[2]
        self.res_info = res_info
        self.res_group = res_group
        print(self.email)
        self.req = requests.Session()

        # self.req.proxies = {"http": "127.0.0.1:8888", "https": "127.0.0.1:8888"}
        # self.req.verify = False
        
        self.req.timeout = 300
        self.path = sys.path[0] + '\\'
        
        self.req.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.10 Safari/537.36',
        }
        self.registe_url = 'https://www.windowmalaysia.my/evisa/vlno_register.jsp?type=register'

    def requ(self, url, data=None):
        print('in requ')#, data)
        while 1:
            try:
                if not data:
                    print('in get')
                    res = self.req.get(url)
                    if res.status_code == 200:
                        # print(res.text)
                        break
                else:
                    print('in post')
                    res = self.req.post(url, data=data)
                    if res.status_code == 200:
                        # print(res.text)
                        break
            except:
                continue
        # print(res)
        return res

    # 注册
    def registe(self):
        print('正在注册...')
        res = self.requ(self.registe_url)
        data = self.get_data(res)
        # print(data)
        re_url = 'https://www.windowmalaysia.my/evisa/register'
        res = self.requ(re_url, data=data)
        print('请求发送成功...进入判断...')
        if 'Resend Activation Email' in res.text:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data = {"email": self.email, "status": "1"}
            rs = requests.post(url, data=data)
            print(rs.json())
            print("注册成功...")
            for _ in range(5):
                time.sleep(1)
                self.req.get(f'https://www.windowmalaysia.my/evisa/resendVerification?email={self.email}')
            return 1
        elif 'You have entered an invalid email address' in res.text:
            print('邮箱无效，更换邮箱...')
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/replaceEmail"
            data_p = {"email": self.email}
            res = requests.post(url, data_p).json()
        print('注册失败!...')
        url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
        data = {"email": self.email, "status": "2"}
        rs = requests.post(url, data=data)
        print(rs.json())
        with open('xxx.html', 'wb') as f:
            f.write(res.content)
        return 0

    # 获取注册数据
    def get_data(self, res):
        print('in get_data')

        answer = self.get_answer(res)

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
        return data

    # 邮箱激活
    def email_163(self, no_win=None):
        M = PyMouse()
        try:
            chrome_options =  webdriver.ChromeOptions()
            if not no_win:
                print('no window')
                chrome_options.add_argument('blink-settings=imagesEnabled=false')
                chrome_options.add_argument('--headless')
            # chrome_options.add_argument('window-size=1920x3000')
            path = sys.path[0] + '\\'
            self.driver = webdriver.Chrome(executable_path=path + 'chromedriver', chrome_options=chrome_options)
            # self.driver.implicitly_wait(30)
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.maximize_window()
            print('163邮箱账号框的选择和输入')
            self.driver.get("http://mail.163.com") #/index_alternate.htm")
            # self.driver.delete_all_cookies()
            # try:
            #     self.wait.until(EC.presence_of_element_located(("xpath", '//*[@id="normalLoginFormMask"]/p/a')))
            #     self.driver.find_element_by_xpath('//*[@id="normalLoginFormMask"]/p/a').click()
            # except:
            #     pass
            # 163邮箱账号框的选择和输入
            # time.sleep(200)
            self.wait.until(EC.presence_of_element_located(('id', 'x-URS-iframe')))
            f1 = self.driver.find_element_by_id("x-URS-iframe")
            self.driver.switch_to.frame(f1)
            self.driver.find_element_by_xpath('//div[@id = "account-box"]/div[2]/input').send_keys(
                self.res[1])  # "suxun941103"
            self.driver.find_element_by_xpath('//form[@id ="login-form"]/div/div[3]/div[2]/input[2]').send_keys(
                self.res[2])  # "739489696"

            # self.wait.until(EC.presence_of_element_located(('id', 'idInputLine')))
            # self.driver.find_element_by_id('idPlaceholder').send_keys(self.res[1])

            # self.wait.until(EC.presence_of_element_located(('id', 'pwdInput')))
            # self.driver.find_element_by_id('pwdInput').send_keys(self.res[2])
            
            time.sleep(2)

            try:
                self.driver.find_element_by_id("dologin").click()
            except:
                pass
            time.sleep(1)
            txt = '网易邮箱'
            title = self.driver.title
            try:
                self.driver.find_element_by_xpath('//a[@class="u-btn u-btn-middle3 f-ib bgcolor f-fl"]').click()
                print('-----------------------------')
            except:
                if txt not in title:
                    try:
                        self.driver.save_screenshot('code_yunsu.png')
                    except:
                        self.driver.save_screenshot('code_yunsu.png')

                    print('= = ' * 20)
                    crop_img = (685, 500, 1000, 650)
                    w = 685
                    h = 500
                    im = Image.open("code_yunsu.png")
                    # 图片的宽度和高度
                    print("正在识别验证码...")

                    region = im.crop(crop_img)
                    region.save("code_yunsu.png")
                    result = upload(6903, 90)
                    yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                    data = {'type': '3', 'num': '40'}
                    requests.post(yunsu_url, data=data)
                    print(result)
                    if type(result) is list and not no_win:
                        url_02 = 'http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus'
                        # url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                        data_02 = {"email": self.email, "status": "4"}
                        requests.post(url_02, data_02)
                        return
                    for i in result:
                        w_m = w + int(i.split(',')[0])
                        h_m = h + 90 + int(i.split(',')[1]) + 20
                        print(i, w_m, h_m)
                        M.click(w_m, h_m)
                        w_m = h_m = 0
                        time.sleep(0.5)
                    try:
                        time.sleep(2)
                        self.driver.find_element_by_id("dologin").click()
                    except:
                        pass

            try:
                time.sleep(1)
                self.driver.find_element_by_xpath('//a[@class="u-btn u-btn-middle3 f-ib bgcolor f-fl"]').click()
            except:
                print('...')

            time.sleep(2)

            try:
                self.driver.find_element_by_id('_mail_tabitem_3_51text').click()
            except:
                self.driver.find_element_by_xpath('//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
            time.sleep(2) 

            if 'VisaMalaysia' not in self.driver.page_source:
                # 点击收件箱
                # print('点击垃圾邮箱')
                try:
                    self.driver.find_element_by_xpath('//li[@class="js-component-tree nui-tree-item nui-tree-item-isFold"]/div[@class="js-component-component nui-tree-item-label"]').click()
                    # time.sleep(10)
                    # self.driver.find_element_by_id('_mail_component_109_109').click()
                    print('点击其他文件夹')
                    time.sleep(2)
                    tree = self.driver.find_elements_by_xpath('//div[@class="js-component-component nui-tree-item-label"]')
                    print(f'tree 有 {len(tree)} 个')
                    for i in range(len(tree)):
                        if '垃圾' in tree[i].text:
                            # print('点击垃圾箱')
                            print(i, tree[i].text)
                            tree[i].click()
                            print('√')
                            break
                except Exception as e:
                    print(e)
                    time.sleep(10)
                    url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                    data_02 = {"email":  self.email, "status": "4"}
                    requests.post(url_02, data_02)
                    print('=' * 30)

                    # self.driver.find_element_by_xpath('//li[@id="_mail_component_72_72"]/span[@class="oz0"]').click()
                    # self.driver.find_element_by_xpath(
                    #     '//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
            
            try:
                # self.driver.find_element_by_xpath('//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
                time.sleep(2)
                print('点击第一封邮件')
                dps = self.driver.find_elements_by_class_name('dP0')
                for i in range(len(dps)):
                    if 'VisaMalaysia' in dps[i].text:
                        dps[i].click()
                        break

                # time.sleep(1000)



                if 'VisaMalaysia' in self.driver.page_source:
                    # 点击未读邮件的第一封邮件
                    # self.driver.find_element_by_xpath('//div[@class = "nl0 hA0 ck0"]/div[@class = "gB0"]').click()
                    print('点击第一封邮件')
                    time.sleep(2)
                    f2 = self.driver.find_element_by_class_name("oD0")
                    time.sleep(3)
                    self.driver.switch_to.frame(f2)
                    print('获取链接地址')
                    content = self.driver.find_element_by_xpath('//body/div/div[4]/p[2]/a')
                    # print(content)
                    em_url = content.get_attribute('href')
                    print(em_url)
                    res = self.req.get(em_url)
                    print("激活成功")
                    act_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                    act_data = {"email":  self.email, "status": "3"}
                    requests.post(act_url, data=act_data)
                    time.sleep(3)
                else:
                    url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                    data_02 = {"email":  self.email, "status": "4"}
                    requests.post(url_02, data_02)
            except Exception as e:
                print(e)
                time.sleep(10)
                url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                data_02 = {"email":  self.email, "status": "4"}
                requests.post(url_02, data_02)
                    
        except Exception as e:
            print(e, '-' * 20, sep='\n')
            url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data_02 = {"email":  self.email, "status": "4"}
            requests.post(url_02, data_02)
        finally:
            try:
                self.driver.quit()
            except:
                pass

    # 登录-填写信息-付款
    def login(self):
        try:
            self.img_url(self.res, self.res_info, self.res_group)
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'
            
            res = self.req.get(index_url)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)" />'
            ipaddr = re.findall(reg, res.text)[0]
            # print(ipaddr)
            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&txtEmail={self.email}&txtPassword={GLOBAL_DATA[4]}&answer={self.get_answer(res)}&_={int(time.time()*1000)}'
            # print(url)
            res = self.req.get(url)
            # print(self.req.headers)
            if res.json().get("status") != "success":
                url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                data_02 = {"email":  self.email, "status": "4"}
                requests.post(url_02, data_02)
                print("登录失败，重新激活！")
                return 
            # print(res.status_code)
            assert res.status_code == 200

            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url)

            reg = r"window\.location\.replace\('(.*?)'\);"
            join_evisa_url = re.findall(reg, res.text)

            if join_evisa_url == []:
                print('没有数据!...')
                return
            join_evisa_url = join_evisa_url[0]
            print('加入ENTRI计划')
            res = self.req.get(join_evisa_url)
            print('添加新的')

            reg = r'<input type="hidden" name="checkAppNum1" id="checkAppNum1" value="(.*?)" />'
            uAppNumber = re.findall(reg, res.text)
            print(uAppNumber)
            if len(uAppNumber) > 0:
                uAppNumber = uAppNumber[0]
                print('in old visa')
                url = f'https://www.windowmalaysia.my/entri/registration.jsp?appNumber={uAppNumber}'
                # print(url)
                res = self.req.get(url)
                print('正在上传人脸信息...')

                reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)" />'
                uUser = re.findall(reg, res.text)[0]

                _files = {
                    'uAppNumber': (None, uAppNumber), 
                    'uUser': (None, uUser), 
                    'uPhotoFile': ('photo.png', open(r'visa_photo\photo.png', 'rb'), 'image/png'), 
                    'btnUploadPhoto': (None, '上传'), 
                }
                res = self.req.post('https://www.windowmalaysia.my/entri/photo', files=_files)
                print('上传信息成功')
            else:
                print('in new visa')
                registe_url = 'https://www.windowmalaysia.my/entri/registration.jsp'
                res = self.req.get(registe_url)

                reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)" />'
                uAppNumber = re.findall(reg, res.text)[0]

                reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)" />'
                uUser = re.findall(reg, res.text)[0]

                print('正在上传人脸信息...', time.strftime('%H:%M:%S'))
                _files = {
                    'uAppNumber': (None, uAppNumber), 
                    'uUser': (None, uUser), 
                    'uPhotoFile': ('photo.png', open(r'visa_photo\photo.png', 'rb'), 'image/png'), 
                    'btnUploadPhoto': (None, '上传'), 
                }
                res = self.req.post('https://www.windowmalaysia.my/entri/photo', files=_files)
                print('上传信息成功')

                print('正在上传护照信息...', time.strftime('%H:%M:%S'))
                reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)" />'
                uAppNumber = re.findall(reg, res.text)[0]

                _files1 = {
                    'uAppNumber': (None, uAppNumber), 
                    'uUser': (None, uUser), 
                    'uPassportFile': ('hz.png', open(r'visa_photo\hz.png', 'rb'), 'image/png'), 
                    'btnUploadPassport': (None, '上传'), 
                }

                res = self.req.post( 'https://www.windowmalaysia.my/entri/passport', files=_files1)
                print('上传信息成功')


                reg = r'<input type="hidden" name="appNumber" id="appNumber" value="(.*?)" />'
                uAppNumber = re.findall(reg, res.text)[0]

                print('正在上传航班信息...', time.strftime('%H:%M:%S'))
                _files = {
                    'uAppNumber': (None, uAppNumber), 
                    'uUser': (None, uUser), 
                    'uItineraryFile': ('hb.png', open(r'visa_photo\hb.png', 'rb'), 'image/png'), 
                    'btnUploadItinerary': (None, '上传'), 
                }
                res = self.req.post('https://www.windowmalaysia.my/entri/itinerary', files=_files)
                print('上传信息成功')


                if self.res_info[45]:
                    if url.split('.')[-1] != 'pdf':
                        print('正在上传其他信息...')
                        _files1 = {
                            'uAppNumber': (None, uAppNumber), 
                            'uUser': (None, uUser), 
                            'uOtherFile': ('other.pdf', open(r'visa_photo\other.pdf', 'rb'), 'application/pdf'), 
                            'btnUploadOtherDocument': (None, '上传'), 
                        }
                        res = self.req.post('https://www.windowmalaysia.my/entri/itinerary', files=_files1)
                        print('上传信息成功')
                    else:
                        print('其他文件格式不正确')


            reg = r'<input type="hidden" name="appVisaNumber" id="appVisaNumber" value="(.*?)" />'
            appVisaNumber = re.findall(reg, res.text)
            data = {
                'countryId': '47',
                'user': uUser,
                'appNumber': uAppNumber,
                'appVisaNumber': appVisaNumber,
                'appEmail': self.email,
                'appPurposeStay': '11',
                'expatCategory': '0',
                'principleName': '',
                'occupation':'',
                'expatRelationship': '0',
                'appFirstName': self.res_info[31],
                'appLastName': self.res_info[29],
                'appGender':1 if self.res_info[3] == '男' else 2,
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
                'countryTransitHome': '0',
                'countryDestinationHome': '47',
                'appExitVia': 'Air',
                'appAddress1': self.res_info[9],
                'appAddress2': '',
                'appPostcode': self.res_info[26],
                'appCity': self.res_info[25],
                'showProvince': 'true',
                'appProvince': self.res_info[24],
                'appMysAddress1': self.res_group[31],
                'appMysAddress2': self.res_group[18],
                'appMysPostcode': self.res_group[24],
                'appMysCity': self.res_group[36],
                'paymentMethod': 'alipay',
                'travelExceed': '0',
                'termCondition': 'on',
                'btnSave': 'AGREE'
            }
            # print(data)
            res = self.req.post('https://www.windowmalaysia.my/entri/registration', data=data)
            if 'egistration=alreadyExist' in res.url:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "重复提交", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo)
                print(_res.json())
                requests.get("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]))
                return
            elif 'registration=fail' in res.url:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "有效期内", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo)
                print(_res.json())
                requests.get("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]))
                return
            elif 'photo_editor' not in res.url:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "护照过期", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo)
                print(_res.json())
                requests.get("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]))
                return
            # print(res)
            # 查看照片是否合格
            murl = 'https://www.windowmalaysia.my/entri/updatePhoto?appNumber=%s&dataX={0}&dataY={1}&dataWidth={2}&dataHeight={3}&dataRotate=0&isEdit=true' % (uAppNumber)
            print(f'进入照片页--原照片')
            res = self.req.get(murl.format(0, 0, 213, 296))
            print('发送请求，进行照片判断')

            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if self.setPhoto(res, murl):
                    return -1
            
            time.sleep(3)
            #支付宝付款
            print('准备进入支付宝付款')
            while True:
                res = self.req.get(f'https://www.windowmalaysia.my/entri/payment.jsp?appNumber={uAppNumber}')
                # print(res.status_code)
                time.sleep(2)
                if res.status_code != 500:
                    break
                else:
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "2"}
                    self.req.post(url, data)
                    return -1

            ret = r'<input type="hidden" name="total_fee" id="total_fee" value="(.*?)">'
            total_fee = re.findall(ret,res.text)[0]

            ret = r'<input type="hidden" name="body" id="body" value="(.*?)">'
            body = re.findall(ret,res.text)[0]
            ret = r'<input type="hidden" name="branchCode" id="branchCode" value="(.*?)">'
            branchCode = re.findall(ret,res.text)[0]
            ret = r'<input type="hidden" name="keyOutTradeNo" id="keyOutTradeNo" value="(.*?)">'
            keyOutTradeNo = re.findall(ret,res.text)[0]
            ret = '<input type="hidden" name="user" id="user" value="(.*?)" />'
            user = re.findall(ret,res.text)[0]
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

            res = self.req.post(url,data=data)
            # 付款
            self.pay(uAppNumber, res)
        except:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "2"}
            requests.post(url, data)

    # 30天 登陆-付款
    def thLogin(self):
        try:
            self.img_url(self.res, self.res_info, self.res_group)
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'
            
            res = self.req.get(index_url)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)" />'
            ipaddr = re.findall(reg, res.text)[0]
            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&txtEmail={self.email}&txtPassword={GLOBAL_DATA[4]}&answer={self.get_answer(res)}&_={int(time.time()*1000)}'
            res = self.req.get(url)
            print(res.json())
            assert res.status_code == 200

            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url)

            # 30天签证
            print("点击 30 天签证")
            res = self.req.get("https://www.windowmalaysia.my/evisa/vlno_center.jsp")

            reg = r'<input type="hidden" name="checkAppNum1" id="checkAppNum1" value="(.*?)" />'
            checkAppNum1 = re.findall(reg, res.text)
            if checkAppNum1:
                print("有旧记录")
                delurl = "https://www.windowmalaysia.my/evisa/center"
                data = {
                    "chkDel": "1",
                    "checkAppNum1": checkAppNum1[0],
                    "btnDel": "",
                }
                self.req.post(delurl, data=data)

            # 新建 旅游签证
            res = self.req.get("https://www.windowmalaysia.my/evisa/locations?evisaType=1")


            reg = r'<input type="hidden" name="uUser" id="uUser" value="(.*?)" />'
            uUser = re.findall(reg, res.text)[0]
            # reg = r' <input type="hidden" name="uIndicator" id="uIndicator" value="(.*?)" />'
            # uIndicator = re.findall(reg, res.text)[0]
            reg = r'<input type="hidden" name="uApplicantId" id="uApplicantId" value="(.*?)" />'
            uApplicantId = re.findall(reg, res.text)[0]
            reg = r'<input type="hidden" name="uAppNumber" id="uAppNumber" value="(.*?)" />'
            uAppNumber = re.findall(reg, res.text)[0]

            dobY, dobM, dobD = self.res_info[5].split("-")
            # print(self.res_info[12], self.res_info[5], uAppNumber)
            alertUrl = f"https://www.windowmalaysia.my/evisa/vlno_ajax_checkPassportNo.jsp?passportNo={self.res_info[12]}&nationality=CHN&dobDay={int(dobD)}&dobMonth={int(dobM)}&dobYear={dobY}&appNumber={uAppNumber.replace('/', '%2F')}"
            alert = self.req.get(alertUrl).text.strip()
            print("----\n", alert, "\n----")
            if alert:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.email, "text": "重复提交", "type": "3"}
                print(data_photo)
                _res = requests.post(url, data_photo)
                print(_res.json())
                requests.get("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7]))
                return

            files = {
                "uUser": (None, uUser),
                "uIndicator": (None, "update"),
                "uApplicantId": (None, uApplicantId),
                "uAppNumber": (None, uAppNumber),
                "photo": ("photo.png", open('visa_photo\\photo.png', 'rb'), 'image/png'),
                "passportphoto": ("hz.png", open('visa_photo\\hz.png', 'rb'), 'image/png'),
                "passportphotoLast": ("hz.png", open('visa_photo\\hz.png', 'rb'), 'image/png'),
                "itenaryDoc": ("hb.png", open('visa_photo\\hb.png', 'rb'), 'image/png'),
                "bookingDoc": (None, ""),
                "otherDoc": (None, ""),
                "invitationDoc": (None, ""),
                "inventorDoc": (None, ""),
                "invitationDocName": (None, ""),
                "itenaryDocName": (None, r"C:\fakepath\hb.png"),
                "bookingDocName": (None, ""),
                "otherDocName": (None, ""),
                "photoFileName": (None, r"C:\fakepath\photo.png"),
                "passportFileName": (None, r"C:\fakepath\hz.png"),
                "passportFileNameLast": (None, r"C:\fakepath\hz.png"),
                "inventorDocName": (None, ""),
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
                files["otherDoc"] = ("other.pdf", open("visa_photo/other.pdf", "rb"), "application/pdf")
                files["otherDocName"] = (None, r"C:\fakepath\other.pdf")
            if self.res_info[47]:
                files["underageDoc"] = ("other.pdf", open("visa_photo/other.pdf", "rb"), "application/pdf")
                files["underageDocName"] = (None, r"C:\fakepath\other.pdf")
            if self.res_group[44]:
                files["bookingDoc"] = ("jd.pdf", open('visa_photo\\jd.pdf', 'rb'), 'application/pdf')
                files["bookingDocName"] = (None, r"C:\fakepath\jd.pdf")

            url = "https://www.windowmalaysia.my:443/evisa/applications"
            # res = self.req.post(url, data=data, files=file)
            res = self.req.post(url, files=files)
            print("\n信息上传完成，进入照片判断\n")

            # 查看照片是否合格
            murl = "https://www.windowmalaysia.my/evisa/updatePhoto?%s&dataX={}&dataY={}&dataWidth={}&dataHeight={}&dataRotate=0&idKeyProc=0&isEdit=true&evisaType=1" % (res.url.split("?")[1])
            fmurl = "https://www.windowmalaysia.my/evisa/updatePhoto?%s&dataX={}&dataY={}&dataWidth={}&dataHeight={}&dataRotate=0&idKeyProc=0&isEdit=false&evisaType=1" % (res.url.split("?")[1])
            print(f'进入照片页--原照片')
            # res = self.req.get(murl.format(0, 0, 170, 238))
            res = self.req.get(fmurl.format(0, 0, 213, 296))
            print('发送请求，进行照片判断')
            
            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if self.setPhoto(res, murl):
                    return -1
            if "照片可以接受" in res.text:
                print("照片上传成功")
            else:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.email, "status": "2"}
                requests.post(url, data)
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "照片不合格"}
                print('123s')
                print(data_photo)
                requests.post(url, data_photo)
                
            okurl = f"https://www.windowmalaysia.my/evisa/updateRotation?rotPhotoP=0&rotPpt=0&rotPptL=0&applicantId={uApplicantId}&appNumber={uAppNumber}"
            res = self.req.get(okurl)
            
            """ 
            <input type="hidden" name="appTotal" id="appTotal" value="1" />
            <input type="hidden" name="ccNumber" id="ccNumber" value="" />
            <input type="hidden" name="expiryDate" id="expiryDate" value="" />
            <input type="hidden" name="branchCurrency" id="branchCurrency" value="RMB" />
            <input type="hidden" name="branchCode" id="branchCode" value="1034121" />
            <input type="hidden" name="appDocNumber" id="appDocNumber" value="G59897649" />
            <input type="hidden" name="appDocNationality" id="appDocNationality" value="CHN" />
            <input type="hidden" name="visaFee" id="visaFee" value="80.0" />
            <input type="hidden" name="convenienceFee" id="convenienceFee" value="0.0" />
            <input type="hidden" name="courierFee" id="courierFee" value="0.0" />
            <input type="hidden" name="processingFee" id="processingFee" value="200.0" />
            <input type="hidden" name="totalFee" id="totalFee" value="280.0" />
            <input type='hidden' id='payMethodId' name='payMethodId' value='21' />
            <input type="radio" name="paymentType" class="cpaytype" id="paymentType" value="alipaysplit">
            """

            reg = r'<input type="hidden" name="branchCode" id="branchCode" value="(.*?)" />'
            branchCode = re.findall(reg, res.text)
            branchCode = branchCode[0]
            reg = r'<input type=\'hidden\' id=\'payMethodId\' name=\'payMethodId\' value=\'(.*?)\' />'
            payMethodId = re.findall(reg, res.text)
            payMethodId = payMethodId[0]

            alpayurl = f'https://www.windowmalaysia.my/evisa/previews?appNumber={uAppNumber.replace("/", "%2F")}&appTotal=1&ccNumber=&expiryDate=%2F&branchCurrency=RMB&branchCode={branchCode}&appDocNumber={self.res_info[12]}&appDocNationality=CHN&visaFee=80.0&convenienceFee=0.0&courierFee=0.0&processingFee=200.0&totalFee=280.0&payMethodId={payMethodId}&paymentType=alipaysplit&cc_no1=&cc_no2=&cc_no3=&cc_no4=&ccv=&cc_mm=&cc_yy=&cc_name=&confirmDetail=on&btnNext2='
            res = self.req.get(alpayurl)
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
            res = self.req.post(aurl, data=data)
            self.pay(uAppNumber, res)
        except Exception as e:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "2"}
            requests.post(url, data)            

    # 获取电子签模块
    def get_visa(self):
        try:
            print('正在执行登录...')
            index_url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'
            
            res = self.req.get(index_url)
            print('请求主页...')

            reg = r'<input type="hidden" id="ipAddress" name="ipAddress" value="(.*?)" />'
            ipaddr = re.findall(reg, res.text)[0]
            # print(ipaddr)
            url = f'https://www.windowmalaysia.my/evisa/login?ipAddress={ipaddr}&txtEmail={self.email}&txtPassword={GLOBAL_DATA[4]}&answer={self.get_answer(res)}&_={int(time.time()*1000)}'
            # print(url)
            res = self.req.get(url)
            # print(self.req.headers)
            print(res.text)
            # print(res.status_code)
            assert res.status_code == 200
            welcome_url = 'https://www.windowmalaysia.my/evisa/welcome.jsp'
            res = self.req.get(welcome_url)

            reg = r"window\.location\.replace\('(.*?)'\);"
            join_evisa_url = re.findall(reg, res.text)

            if join_evisa_url == []:
                print('没有数据!...')
                return
            join_evisa_url = join_evisa_url[0]
            print('加入ENTRI计划')
            res = self.req.get(join_evisa_url)
            appnumber = res.text.split('appNumber=')[1].split('">')[0]
            print(appnumber)
            if '繼續' not in res.text:
                print('签证已出，正在提取...')
                
            else:
                print('签证未出，执行查询后提取...')
                payUrl = 'https://www.windowmalaysia.my/entri/payment.jsp?appNumber=' + appnumber
                hisUrl = f'https://www.windowmalaysia.my/entri/check_payment_history.jsp?appNumber={appnumber}&_={int(time.time()*1000)}'
                self.req.get(payUrl)
                result = self.req.get(hisUrl).json()
                print(result)
                if result.get('tradeStatus') == 'success':
                    print('签证已出，正在提取...')
                elif result == {}:
                    print('未付款,重新付款...')
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "2"}
                    requests.post(url, data)
                    return 2
                else:
                    visa_data = {"email": self.email}
                    self.req.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                    return 1
            visa_url = 'https://www.windowmalaysia.my/entri/note?appNumber=' + appnumber
            pay_url = 'https://www.windowmalaysia.my/entri/jasperpayment?appNumber=' + appnumber
            visa_data = {"email": self.email, "evisa": visa_url, "receipt": pay_url}
            self.req.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
            print('提取完成')
            with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 电子签获取成功!", f)
                f.write('\n],\n')
                time.sleep(1)
            return 0

        except:
            visa_data = {"email": self.email}
            self.req.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"

    def pay(self, uAppNumber, res):
        subject = uAppNumber
        ret = r'<input type="hidden" name=\'sign\' value=\'(.*?)\' />'
        sign = re.findall(ret,res.text)[0]
        # print(sign)
        ret = r'<input type="hidden" name=\'split_fund_info\' value=\'(.*?)\' />'
        split_fund_info = re.findall(ret, res.text)[0]
        # print(split_fund_info)
        ret = r'<input type="hidden" name=\'notify_url\' value=\'(.*?)\' />'
        notify_url = re.findall(ret,res.text)[0]
        # print(notify_url)
        ret = r'<input type="hidden" name=\'body\' value=\'(.*?)\' />'
        body = re.findall(ret, res.text)[0]
        # print(body)
        ret = r'<input type="hidden" name=\'product_code\' value=\'(.*?)\' />'
        product_code = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'out_trade_no\' value=\'(.*?)\' />'
        out_trade_no = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'partner\' value=\'(.*?)\' />'
        partner = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'service\' value=\'(.*?)\' />'
        service = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'rmb_fee\' value=\'(.*?)\' />'
        rmb_fee = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'return_url\' value=\'(.*?)\' />'
        return_url = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'currency\' value=\'(.*?)\' />'
        currency = re.findall(ret, res.text)[0]
        ret = r'<input type="hidden" name=\'sign_type\' value=\'(.*?)\' />'
        sign_type = re.findall(ret, res.text)[0]
        self.apliay_url = f'https://mapi.alipay.com/gateway.do?subject={subject}&sign={sign}&split_fund_info={split_fund_info}&notify_url={notify_url}&body={body}&product_code={product_code}&out_trade_no={out_trade_no}&partner={partner}&service={service}&rmb_fee={rmb_fee}&return_url={return_url}&currency={currency}&sign_type={sign_type}'


        # ========================================
        print('打开支付宝， 进行付款...')

        REQ = requests.Session()
        REQ.timeout = 30

        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('window-size=1920x3000')
        path = sys.path[0] + '\\'
        self.driver = webdriver.Chrome(executable_path=path + 'chromedriver', chrome_options=options)
        self.wait = WebDriverWait(self.driver, 20)
        # self.driver.maximize_window()
        
        self.driver.get(self.apliay_url)
        try:
            try:
                # 点击账号密码付款
                print('点击账号密码付款')
                time.sleep(2)
                self.driver.find_element_by_id("J_tip_qr").click()
                time.sleep(1)

            except Exception as e:
                pass

            print('准备输入用户名密码！')
            try:
                print('输入用户名...')
                self.driver.find_element_by_id("J_tLoginId").click()
                time.sleep(2)
                self.driver.find_element_by_id("J_tLoginId").send_keys(GLOBAL_DATA[5])
                time.sleep(2)
                print('输入密码...')
                self.driver.find_element_by_id("payPasswd_rsainput").click()
                time.sleep(2)
                self.driver.find_element_by_id("payPasswd_rsainput").send_keys(GLOBAL_DATA[6])
                print('检查是否有验证码')
                self.driver.save_screenshot("visa_photo/captcha.png")
                time.sleep(1)
                
                time.sleep(1)

                if '验证码' in self.driver.page_source:
                    print('- *' * 10, '\n', '有验证码， 正在识别...')
                    try:
                        captcha_element = self.driver.find_element_by_xpath(
                            '//img[@class="checkCodeImg"]')
                        self.driver.find_element_by_xpath(
                            '//input[@class="ui-input ui-input-checkcode"]').click()
                        captcha_left = captcha_element.location['x']
                        captcha_top = captcha_element.location['y']
                        captcha_right = captcha_left + captcha_element.size['width']
                        captcha_bottom = captcha_element.location['y'] + captcha_element.size['height']
                        # print(captcha_left, captcha_top, captcha_right)
                        img = Image.open('visa_photo/captcha.png')
                        img = img.crop((captcha_left, captcha_top, captcha_right, captcha_bottom))
                        img.save('code_yunsu.png')
                        time.sleep(0.5)
                        # 获取验证码结果
                        result2 = upload(3040)
                        yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                        data = {'type': '3', 'num': '25'}
                        REQ.post(yunsu_url, data=data)
                        print(result2)
                        self.driver.find_element_by_xpath(
                            '//input[@class="ui-input ui-input-checkcode"]').send_keys(
                            result2)
                    except Exception as e:
                        print(e)

                # 点击付款
                print('点击付款...')
                time.sleep(2)
                self.driver.find_element_by_id("J_newBtn").click()
                time.sleep(2)
                while True:
                    if '验证码错误' in self.driver.page_source:
                        self.driver.find_element_by_xpath(
                            '//img[@class="checkCodeImg"]').click()
                        time.sleep(1)
                        self.driver.save_screenshot("visa_photo/captcha.png")
                        print('验证码错误, 重新识别...')
                        print('输入密码...')
                        self.driver.find_element_by_id("payPasswd_rsainput").click()
                        time.sleep(1)
                        self.driver.find_element_by_id("payPasswd_rsainput").send_keys(GLOBAL_DATA[6])
                        img = Image.open('visa_photo/captcha.png')
                        img = img.crop((captcha_left, captcha_top, captcha_right, captcha_bottom ))
                        img.save('code_yunsu.png')
                        # 获取验证码结果
                        result2 = upload(3040)
                        yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                        data = {'type': '3', 'num': '20'}
                        REQ.post(yunsu_url, data=data)
                        self.driver.find_element_by_xpath(
                            '//input[@class="ui-input ui-input-checkcode"]').click()
                        self.driver.find_element_by_xpath(
                            '//input[@class="ui-input ui-input-checkcode"]').clear()
                        print(result2)
                        self.driver.find_element_by_xpath(
                            '//input[@class="ui-input ui-input-checkcode"]').send_keys(
                            result2)
                        # 点击付款
                        print('点击付款...')
                        time.sleep(1)
                        self.driver.find_element_by_id("J_newBtn").click()
                        time.sleep(1)
                    else:
                        break
            except Exception as e:
                print(e)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.res[1], "status": "2"}
                REQ.post(url, data)
                print(data)
                return 0
            print('输入付款账号结束，进入确认付款')
            time.sleep(3)
            try:
                for i in range(2, 10):
                    try:
                        self.driver.find_element_by_id("payPassword_container").click()
                        time.sleep(1)
                        print('输入支付密码！...')
                        
                        ActionChains(self.driver).send_keys(Keys.NUMPAD1, Keys.NUMPAD8, Keys.NUMPAD5, Keys.NUMPAD8,
                                                            Keys.NUMPAD8,
                                                            Keys.NUMPAD8).perform()
                        time.sleep(1)
                        self.driver.find_element_by_xpath('//*[@id="J_authSubmit"]').click()
                        time.sleep(5)
                    except:
                        pass
                    if '您已成功付款' in self.driver.page_source:
                        print('付款成功！,..')
                        self.driver.save_screenshot('successful.png')
                        print('申请成功，付款成功！')
                        with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                            json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 付款成功!", f)
                            f.write('\n],\n')
                        url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                        data = {"email": self.res[1], "status": "1"}
                        REQ.post(url, data)
                        data_photo = {"email": self.email, "type": 1, "text": "等待电子签"}
                        print(data_photo)
                        REQ.post('http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question', data_photo)
                        time.sleep(12)
                        return 1
                    else:
                        try:
                            self.driver.find_element_by_xpath('//*[@id="J_GoBack_nobodyknows"]').click()
                            time.sleep(2)
                            self.driver.find_element_by_xpath('//div[@id="J-rcChannels"]/div/div/a[1]').click()
                            time.sleep(2)
                            self.driver.find_element_by_xpath(f'//*[@id="J_SavecardList"]/li[{i}]').click()
                            time.sleep(2)
                        except:
                            pass
                else:
                    print('付款成功！,..')
                    self.driver.save_screenshot('successful.png')
                    print('申请成功，付款成功！')
                    with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                        json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 付款成功!", f)
                        f.write('\n],\n')
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "1"}
                    REQ.post(url, data)
                    data_photo = {"email": self.email, "type": 1, "text": "等待电子签"}
                    print(data_photo)
                    REQ.post('http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question', data_photo)
                    return 1
            except Exception as e:
                print('出现错误', e)
                time.sleep(5)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.res[1], "status": "2"}
                REQ.post(url, data)
                return 0
        finally:
            try:
                self.driver.quit()
            except:
                pass

    # 照片判断
    def setPhoto(self, res, murl):
        i = 20
        while i >= -20:
            print(f'进入照片页， 控制1: {i}')
            url = murl.format(i, i, 213-i, 296-i)
            res = self.req.get(url)
            print('发送请求，进行照片判断')

            if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                if i != 5:
                    i -= 5
                else:
                    i = -5
                continue
            print('照片通过')
            time.sleep(5)
            break
        if i < -20:
            i = 2
            while i <= 20:
                print(f'进入照片页， 控制2: {i}')
                url = murl.format(i, 0, 213 - i, 296 - i * 2)
                res = self.req.get(url)
                print('发送请求，进行照片判断')

                if '系统检测到您的照片不符合规格。它可能是以下之一：' in res.text:
                    i += 2
                    continue
                print('照片通过')
                time.sleep(5)
                break
        if i > 20:
            i = 24
            while i >= 24:
                print(f'进入照片页， 控制3: {i}')
                url = murl.format(0, -i, 213, 296 - i)
                res = self.req.get(url)
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
                requests.post(url, data)
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "照片不合格"}
                print('123s')
                print(data_photo)
                requests.post(url, data_photo)
                return 1    
        return 0 

    # 验证码
    def get_answer(self, res):
        # 1 + 1 = ?
        reg = r'<b>(.*?) = \?</b></p>'
        if type(res) is not str:
            code = re.findall(reg, res.text)[0]
        else:
            code = res
        print(code)

        s = code.split(' ')
        a = int(s[0])
        b = int(s[2])
        ys = {
            '+': a + b,
            '-': a - b,
            'X': a * b,
        }
        answer = str(ys[s[1]])
        print(answer)
        return answer

    # 获取照片
    def img_url(self, res, sql_geren, sql_gongg):
        # cur.fetchall() ((a, a),)
        print(
            '照片：', sql_geren[23], 
            "护照：", sql_geren[20], 
            '航班：', sql_gongg[34], 
            '其他文件：', sql_geren[45], 
            sep='\n'
            )

        for i in ['photo', 'hz', 'hb']:
            try:
                os.remove(os.path.join(os.getcwd(), f"visa_photo\\{i}.png"))
            except:
                print('删除失败...')

        try:
            os.remove(os.path.join(os.getcwd(), r"visa_photo\other.pdf"))
        except:
            pass

        if not sql_geren[23]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": res[1], "status": "3", "ques": "照片未上传！"}
            requests.post(url, data)
            print('照片未上传')
            return -1
        if not sql_geren[20]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": res[1], "status": "3", "ques": "护照未上传！"}
            requests.post(url, data)
            print('护照未上传')
            return -1
        if not sql_gongg[34]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": res[1], "status": "3", "ques": "航班未生成！"}
            requests.post(url, data)
            print('航班未生成')
            return -1
        rsp_phone = requests.get(sql_geren[23])
        with open(os.path.join(os.getcwd(), r"visa_photo\photo.png"), "wb") as f:
            f.write(rsp_phone.content)
        rsp_hz = requests.get(sql_geren[20])
        with open(os.path.join(os.getcwd(), r"visa_photo\hz.png"), 'wb') as f:
            f.write(rsp_hz.content)
        rsp_hb = requests.get(sql_gongg[34])
        with open(os.path.join(os.getcwd(), r"visa_photo\hb.png"), 'wb') as f:
            f.write(rsp_hb.content)

        # 判断照片规格
        path = os.path.join('./visa_photo', "hb.png")
        img = Image.open(path)
        a = img.size
        size = (a[0] * a[1] * 24 / 1024 / 1024 / 8) * 1024
        path = os.path.join('./visa_photo', "hb.png")
        img = Image.open(path)
        a = img.size
        size1 = (a[0] * a[1] * 24 / 1024 / 1024 / 8) * 1024
        path = os.path.join('./visa_photo', "hb.png")
        img = Image.open(path)
        a = img.size
        size2 = (a[0] * a[1] * 24 / 1024 / 1024 / 8) * 1024
        if size > 2048 or size1 > 2048 or size2 > 2048:
            print('照片大小不合格')
            return -1

        # 判断other文件的格式
        if sql_geren[45]:
            # print(sql_geren[0][45])
            url = sql_geren[45]
            if url.split('.')[-1] != 'pdf':
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": res[1], "status": "2"}
                requests.post(url, data)
                print('其他文件格式不正确（必须为pdf）')
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": res[1], "text": "其他文件格式不正确（必须为pdf）"}
                resaa = requests.post(url, data_photo)
                print(resaa.status_code, resaa.text)
                return -1
            rsp_pdf = requests.get(url)
            with open(os.path.join(os.getcwd(), r"visa_photo\other.pdf"), 'wb')as f:
                f.write(rsp_pdf.content)


class Pipe():
    def __init__(self):
        self.con = POOL.connection()
        self.cur = self.con.cursor()

    # 查询
    def select_info(self):
        try:
            for n1, n2 in [(1, 1), (1, 0), (2, 1), (2, 0)]:
                # print(n1, n2)
                # sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where id = 1562'
                sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where id = 1653'
                # sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type from dc_business_email where type = {n1} and urgent = {n2}'
                self.cur.execute(sql)
                res = self.cur.fetchone()
                # print(1, res)
                if res:
                    if res[3] is 1 and res[4] is 1 and res[5] is 1 and res[6] is 1: 
                        url = 'http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question'
                        data = {'email': res[1], 'type': 3}
                        requests.post(url, data=data)
                        continue
                    sql_gongg = 'select * from dc_business_malaysia_group where tids =' + str(res[7])
                    self.cur.execute(sql_gongg)
                    sql_gongg = self.cur.fetchone()
                    # print('###', sql_gongg)
                    sql_reg = 'select * from dc_business_malaysia_visa where group_id =' + str(res[7])
                    self.cur.execute(sql_reg)
                    sql_geren = self.cur.fetchone()
                    if sql_geren and sql_gongg:
                        return res, sql_geren, sql_gongg
                    else:
                        print("数据库查询出现空值")
                        return res, 0, 0
            print('\n未查询到数据...等待5s重新查询...\n')
            return 0, 0, 0
        except:
            return 0, 0, 0

    def __del__(self):
        self.cur.close()
        self.con.close()


def main():
    while 1:
        try:
            print('-' * 50)
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print('-' * 50)
            p = Pipe()
            res, res_info, res_group = p.select_info()
            
            print(res)
            for i in range(48):
                if i < 46:
                    print(i, res_info[i], res_group[i], sep=" | ")
                else:
                    print(i, res_info[i], sep=" | ")
            exit()
            if not (res and res_info and res_group):
                time.sleep(5)
                continue
            
            r = Automation_malaysia(res, res_info, res_group)
            
            try:
                # 邮箱注册
                if (not res[3]) or (res[3] is 2):
                    print('in reg')
                    r.registe()
                    time.sleep(2)
                    continue
                # 邮箱激活
                if res[3] is 1 and (not res[4] or res[4] is 2):
                    print('in email')
                    r.email_163(res[4])
                    time.sleep(2)
                    continue
                if "eNTRI" in res_group[9]:
                    print('\n--- 15天 ----\n')
                    # 邮箱登录
                    if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
                        print('in login')
                        r.login()
                        time.sleep(2)
                        continue
                    
                    # 获取签证
                    if not res[6] and res[5] is 1:
                        print('in visa')
                        r.get_visa()
                        continue
                        
                    if res[8] is 2 and res[6] is 2:
                        print('\n==============\n开始获取电子签\n==============')
                        r.get_visa()
                elif "eVISA" in res_group[9]:
                    print('\n--- 30天 ----\n')
                    # 邮箱登录
                    if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
                        print('in login')
                        r.thLogin()
                        time.sleep(2)
                        continue
                    # 获取签证
                    if not res[6] and res[5] is 1:
                        print('in visa')
                        # r.get_visa()
                        print("获取签证「30 天」")
                        time.sleep(10)
                        continue
            except Exception as e:
                print('==')
                print(e)
            finally:
                time.sleep(2)
                try:
                    os.remove('code_yunsu.png')
                except:
                    pass
        except Exception as e:
            with open("error.log", 'a') as f:
                f.write(repr(e)+'\n')
            time.sleep(5)


if __name__ == '__main__':
    main()
