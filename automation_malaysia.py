# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: automation_malaysia.py
"""
import json
import os
import re
import sys
import time

import pymysql
import requests
from DBUtils.PooledDB import PooledDB
from PIL import Image
from pymouse import PyMouse
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from yunsu import upload

with open('settings.json', 'r') as f:
    GLOBAL_DATA = json.load(f)

POOL = PooledDB(
    pymysql,
    10,
    host=GLOBAL_DATA[0],
    user=GLOBAL_DATA[1],
    passwd=GLOBAL_DATA[2],
    db=GLOBAL_DATA[3],
    port=3306,
    charset="utf8"
)

M = PyMouse()


class Base():
    '''
    邮箱激活: email_163()
    申请签证: login()
    电子签证获取: get_visa()
    '''
    def __init__(self, NO_WINDOW=True, _res='', _res_info='', _res_gruop=''):     # True 无窗口模式;  False 有窗口模式
        self.url = 'https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh'
        
        self.res = _res
        self.res_info = _res_info
        self.res_group = _res_gruop
        
        self.chrome_options = webdriver.ChromeOptions()
        # 指定浏览器分辨率
        self.chrome_options.add_argument('window-size=1920x3000')
        # 谷歌文档提到需要加上这个属性来规避bug
        self.chrome_options.add_argument('--disable-gpu')
        # 隐藏滚动条, 应对一些特殊页面
        self.chrome_options.add_argument('--hide-scrollbars')
        # 不加载图片, 提升速度
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        no_windows = NO_WINDOW
        if no_windows:
            self.chrome_options.add_argument('--headless')
        # 手动指定使用的浏览器位置
        # chrome_options.binary_location = r"C:\Users\tianheguoyun\AppData\Local\Google\Chrome SxS\Application\chrome"

        self.path = sys.path[0] + '\\'
        webdriver.ChromeOptions
        
    # 邮箱激活
    def email_163(self, no_win=None):
        try:
            chrome_options = self.chrome_options
            if not no_win:
                chrome_options.add_argument('blink-settings=imagesEnabled=false')
                self.chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(executable_path=self.path + 'chromedriver', chrome_options=chrome_options)

            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 30)

            self.driver.get("https://mail.163.com/")
            print(time.strftime('%H:%M:%S'))
            self.driver.delete_all_cookies()
            print(0, time.strftime('%H:%M:%S'))
            # 163邮箱账号框的选择和输入
            time.sleep(2)

            f1 = self.driver.find_element_by_id("x-URS-iframe")
            print(1, time.strftime('%H:%M:%S'))
            self.driver.switch_to.frame(f1)
            print(2, time.strftime('%H:%M:%S'))
            self.driver.find_element_by_xpath('//div[@id = "account-box"]/div[2]/input').send_keys(self.res[1]) #"suxun941103"
            time.sleep(2)
            print(3, time.strftime('%H:%M:%S'))
            self.driver.find_element_by_xpath('//form[@id ="login-form"]/div/div[3]/div[2]/input[2]').send_keys(self.res[2]) # "739489696"
            time.sleep(2)
            print(4, time.strftime('%H:%M:%S'))
            try:
                self.driver.find_element_by_id("dologin").click()
            except:
                pass
            time.sleep(1)
            print(5, time.strftime('%H:%M:%S'))
            
            print(6, time.strftime('%H:%M:%S'))
            txt = '网易邮箱'
            title = self.driver.title
            try:
                self.driver.find_element_by_xpath('//a[@class="u-btn u-btn-middle3 f-ib bgcolor f-fl"]').click()
                print('-----------------------------')
                print(7, time.strftime('%H:%M:%S'))
                # time.sleep(3)
            except:    
                if txt not in title:
                    try:
                        self.driver.save_screenshot('code_yunsu.png')
                    except:
                        self.driver.save_screenshot('code_yunsu.png')

                    print('= = ' * 20)
                    # 360, 460, 1160, 1160
                    crop_img = (685, 500, 1000, 650)
                    w = 685
                    h = 500
                    im = Image.open("code_yunsu.png")
                    # 图片的宽度和高度
                    # img_size = im.size
                    print("正在识别验证码...")
                    
                    region = im.crop(crop_img)
                    region.save("code_yunsu.png")
                    result = upload(6903, 90)
                    yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                    data = {'type': '3', 'num': '40'}
                    requests.post(yunsu_url, data=data)
                    print(result)
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
                print(8, time.strftime('%H:%M:%S'))
            except:
                # time.sleep(3)
                pass
                
            time.sleep(2)
            print(9, time.strftime('%H:%M:%S'))
            # 点击收件箱
            try:
                self.driver.find_element_by_id('//div[@id="_mail_tabitem_3_51text"]').click()
                # self.driver.find_element_by_xpath('//li[@id="_mail_component_72_72"]/span[@class="oz0"]').click()
                # self.driver.find_element_by_xpath('//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
            except:
                time.sleep(2)
                # self.driver.find_element_by_xpath('//li[@id="_mail_component_72_72"]/span[@class="oz0"]').click()
                self.driver.find_element_by_xpath('//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
            time.sleep(2) 
            print(10, time.strftime('%H:%M:%S'))
            
            try:
                print('准备点击收件箱')
                # self.driver.find_element_by_xpath('//li[@class = "js-component-component gWel-mailInfo-item gWel-mailInfo-unread"]/div[2]').click()
                time.sleep(2)
                # 点击未读邮件的第一封邮件
                self.driver.find_element_by_xpath('//div[@class = "nl0 hA0 ck0"]/div[@class="gB0"]/div[2]').click()
                print(11, time.strftime('%H:%M:%S'))
                print('点击未读邮件的第一封邮件')
                time.sleep(2)
                print(12, time.strftime('%H:%M:%S'))
                f2 = self.driver.find_element_by_class_name("oD0")
                time.sleep(3)
                print(13, time.strftime('%H:%M:%S'))
                self.driver.switch_to.frame(f2)
                print(14, time.strftime('%H:%M:%S'))
                self.driver.find_element_by_xpath('//body/div/div[4]/p[2]/a').click()
                print("激活成功")
                with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                    json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 激活成功!", f)
                    f.write('\n],\n')
                # self.all_h = self.driver.window_handles
                # self.driver.switch_to_window(self.all_h[0])
                # self.driver.close()
                print(15, time.strftime('%H:%M:%S'))
                time.sleep(10)
                act_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                act_data = {"email": self.res[1], "status": "3"}
                #print(act_data)
                #print("111"* 20)
                print(16, time.strftime('%H:%M:%S'))
                requests.post(act_url, data=act_data)
                print(17, time.strftime('%H:%M:%S'))
                time.sleep(3)
            except Exception as e:
                print(e)
                url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                data_02 = {"email": self.res[1], "status": "4"}
                requests.post(url_02, data_02)
                self.driver.quit()
            finally:
                time.sleep(5)
        except:
            url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data_02 = {"email": self.res[1], "status": "4"}
            requests.post(url_02, data_02)


    def login(self):
 
        print(os.getcwd(),'照片:', self.res_info[0][23], "护照： ", self.res_info[0][20], '航班：', self.res_group[0][34], sep='\n')

        try:
            os.remove(os.path.join(os.getcwd(), r"visa_photo\photo.png"))
            os.remove(os.path.join(os.getcwd(), r"visa_photo\hz.png"))
            os.remove(os.path.join(os.getcwd(), r"visa_photo\hb.png"))
        except:
            print('删除失败...')

        if not self.res_info[0][23]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "3", "ques": "照片未上传！"}
            requests.post(url, data)
            print('照片未上传')
            return -1
        if not self.res_info[0][20]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "3", "ques": "护照未上传！"}
            requests.post(url, data)
            print('护照未上传')
            return -1
        if not self.res_group[0][34]:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "3", "ques": "航班未生成！"}
            requests.post(url, data)
            print('航班未生成')
            return -1
        rsp_phone = requests.get(self.res_info[0][23])
        with open(os.path.join(os.getcwd(), r"visa_photo\photo.png"),"wb") as f:
            f.write(rsp_phone.content)
        rsp_hz = requests.get(self.res_info[0][20])
        with open(os.path.join(os.getcwd(), r"visa_photo\hz.png"),'wb') as f:
            f.write(rsp_hz.content)
        rsp_hb = requests.get(self.res_group[0][34])
        with open(os.path.join(os.getcwd(), r"visa_photo\hb.png"),'wb') as f:
            f.write(rsp_hb.content)
        if self.res_info[0][45]:
            print(self.res_info[0][45])
            url = self.res_info[0][45]
            # print(self.res_info[0])
            # print(len(self.res_info[0]))
            if url.split('.')[-1] != 'pdf':
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email": self.res[1], "status": "2"}
                requests.post(url, data)
                print('其他文件格式不正确（必须为pdf）')
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "其他文件格式不正确（必须为pdf）"}
                resaa = requests.post(url, data_photo)
                print(resaa.status_code, resaa.text)
                return -1
            rsp_pdf = requests.get(url)
            with open(os.path.join(os.getcwd(), r"visa_photo\other.pdf"), 'wb')as f:
                f.write(rsp_pdf.content)


        # st = time.time()
        time.sleep(0.1)
        print('正在登陆，请稍后...')
        try:
            al_h = self.driver.window_handles
            print(al_h)
            self.driver.switch_to_window(al_h[0])
            self.driver.close()
            self.driver.switch_to_window(al_h[1])
        except AttributeError:
            print('new')
            options = self.chrome_options
            # options.add_argument('blink-settings=imagesEnabled=false')
            self.driver = webdriver.Chrome(executable_path=self.path + 'chromedriver', chrome_options=options)
            self.driver.maximize_window()
            self.driver.get("https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh")
            print('get')
            self.wait = WebDriverWait(self.driver, 30)
            time.sleep(10)
        print('sleep')
        try:
            self.driver.find_element_by_id('lz_overlay_eyecatcher_close').click()
            time.sleep(1)
        except:
            pass
        try:
            self.driver.find_element_by_class_name('ev-opt-2').click()
            print('点击登录')
            time.sleep(1)
        except:
            pass
        try:
            time.sleep(1)
            self.driver.find_element_by_id('lz_overlay_eyecatcher_close').click()
            print('点击关闭红框')
            time.sleep(1)
        except:
            pass
        time.sleep(1)
       
        password = GLOBAL_DATA[4]
        print('输入用户名...')
        self.driver.find_element_by_id("txtEmail").click()

        self.driver.find_element_by_id("txtEmail").send_keys(self.res[1])
        time.sleep(0.5)
        try:
            self.driver.switch_to_alert().accept()
        except:
            pass
        time.sleep(0.5)
        print('输入密码...')
        self.driver.find_element_by_id('txtPassword').click()

        self.driver.find_element_by_id('txtPassword').send_keys(password)
        time.sleep(0.5)
        # element = self.driver.find_element_by_xpath('//div[@class="col-sm-4"]/img')
        # img_url = self.driver.find_element_by_xpath('//div[@class = "form-group"]/div/img').get_attribute("src")
        # print(img_url)
        element = self.driver.find_element_by_xpath('//*[@id="txtQuestion"]')
        print(element.text)

        s = element.text.split(' ')
        a = int(s[0])
        b = int(s[2])
        ys = {
            '+': a + b,
            '-': a - b,
            'X': a * b,
        }
        result = str(ys[s[1]])
        print(result)
        time.sleep(0.5)
        self.driver.find_element_by_id("answer").click()

        self.driver.find_element_by_id("answer").send_keys(result)
        time.sleep(2)
        # 点击登录
        # os.remove(salt)
        self.driver.find_element_by_id("btnSubmit").click()
        time.sleep(5)
        print(self.driver.title)
        # sreach_window = self.driver.current_window_handle
        if self.driver.title != "Malaysia Electronic Visa Application":
            print("登录失败，即将重新申请")
            time.sleep(5)
            return -1

        # 点击加入ent计划
        self.driver.maximize_window()
        time.sleep(3)
        try:
            self.driver.find_element_by_id("lz_overlay_eyecatcher_close").click()
            time.sleep(1)
        except:
            pass

        self.driver.find_element_by_xpath('//div[@class = "col-lg-4 col-md-4 text-right"]/div[@class = "avenir"]/button').click()
        time.sleep(1)
        # 点击前往按钮
        self.driver.find_element_by_id("confirmNotice").click()
        time.sleep(1)
        # 如有有历史申请,继续下一步操作
        visa_url = self.driver.current_url

        try:
            self.driver.find_element_by_xpath('//a[@onclick="fnContinue()"]').click()
            print('上传照片')
            # 点击上传照片
            self.driver.find_element_by_id("btnOvewrite").click()
            # photo_url = "C:\\Users\Administrator\Desktop\DSC_1339.JPG"
            time.sleep(1)
            # 上传2寸照片
            self.driver.find_element_by_id("uPhotoFile").send_keys(os.path.join(os.getcwd(), r"visa_photo\photo.png"))
            time.sleep(1)
            self.driver.find_element_by_id("btnUploadPhoto").click()
            time.sleep(2)
            print('上传完成')

            if '覆改申请人照片' not in self.driver.page_source or 'ATTENTION' in self.driver.page_source:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "照片不合格"}
                print('123s')
                print(data_photo)
                _res = requests.post(url, data_photo)
                return -1
        except:
            self.driver.find_element_by_id("applyNew").click()
            time.sleep(1)
            try:
                print(self.driver.title)
                print('上传照片')
                # 点击上传照片
                self.driver.find_element_by_id("btnUpload").click()
                # photo_url = "C:\\Users\Administrator\Desktop\DSC_1339.JPG"
                time.sleep(1)

                # 上传2寸照片
                self.driver.find_element_by_id("uPhotoFile").send_keys(os.path.join(os.getcwd(), r"visa_photo\photo.png"))
                time.sleep(1)
                self.driver.find_element_by_id("btnUploadPhoto").click()
                time.sleep(2)
                # print(self.driver.title.split("https://www.windowmalaysia.my/entri/registration.jsp?appNumber=ENT/OH503/"))
                # appnumber = self.driver.title.split("https://www.windowmalaysia.my/entri/registration.jsp?appNumber=ENT/OH503/")
                print('上传完成')

                if '覆改申请人照片' not in self.driver.page_source or 'ATTENTION' in self.driver.page_source:
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                    data_photo = {"email": self.res[1], "text": "照片不合格"}
                    print('123s')
                    print(data_photo)
                    _res = requests.post(url, data_photo)
                    return -1

                print('上传航班行程')
                # 上传航班行程
                self.driver.find_element_by_xpath('//a[@data-target = "#flightItineraryModal"]').click()
                time.sleep(1)
                self.driver.find_element_by_id("uItineraryFile").send_keys(os.path.join(os.getcwd(), r"visa_photo\hb.png"))
                time.sleep(2)
                self.driver.find_element_by_id("btnUploadItinerary").click()
                print('上传完成')

                
                
                time.sleep(3)
                # 上传其他文件
                if self.res_info[0][45]:

                    self.driver.find_element_by_xpath('//a[@data-target = "#otherDocumentModal"]').click()
                    time.sleep(1)
                    self.driver.find_element_by_id("uOtherFile").send_keys(os.path.join(os.getcwd(), r"visa_photo\other.pdf"))
                    time.sleep(1)
                    self.driver.find_element_by_id("btnUploadOtherDocument").click()

                print('上传护照')
                # 点击上传护照
                self.driver.find_element_by_xpath('//a[@data-target = "#passportPhotoModal"]').click()
                time.sleep(1)
                # hz_url = "C:\\Users\Administrator\Desktop\HZ.jpg"
                self.driver.find_element_by_id("uPassportFile").send_keys(os.path.join(os.getcwd(), r"visa_photo\hz.png"))
                time.sleep(2)
                self.driver.find_element_by_id("btnUploadPassport").click()
                print('上传完成')
                time.sleep(2)


            except:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                data = {"email":self.res[1],"status":"2","text":"请检查照片，护照和航班照片，按规范提交"}
                requests.post(url,data)
                
                return -1

            
            time.sleep(2)
            try:
                print('填写护照签发日期')
                # 护照签发日期
                h_start_data = Select(self.driver.find_element_by_id("appDocIssuedDay"))
                h_start_data.select_by_value(str(self.res_info[0][34]))
                # time.sleep(0.5)

                h__start_month = Select(self.driver.find_element_by_id("appDocIssuedMonth"))
                h__start_month.select_by_value(str(self.res_info[0][33]))
                # time.sleep(0.5)
                h_start_year = Select(self.driver.find_element_by_id("appDocIssuedYear"))
                h_start_year.select_by_value(str(self.res_info[0][32]))
                time.sleep(0.5)
                print('填写护照到期日期')
                # 护照到期日期
                h_end_data = Select(self.driver.find_element_by_id("appDocExpiredDay"))
                h_end_data.select_by_value(str(self.res_info[0][37]))
                # time.sleep(0.5)
                h_end_month = Select(self.driver.find_element_by_id("appDocExpiredMonth"))
                h_end_month.select_by_value(str(self.res_info[0][36]))
                # time.sleep(0.5)
                h_end_year = Select(self.driver.find_element_by_id("appDocExpiredYear"))
                h_end_year.select_by_value(str(self.res_info[0][35]))
                # time.sleep(0.5)
                print('填写航班抵达信息')
                # 航班抵达信息
                print(self.res_group[0][25], self.res_group[0][26], self.res_group[0][27], )
                hb_arrive_data = Select(self.driver.find_element_by_id("appTravelDayStart"))

                # hb_arrive_data.select_by_value(data_i(16))
                
                hb_arrive_data.select_by_value(self.data_i(self.res_group[0][27]))
                # time.sleep(0.5)
                hb_arrive_month = Select(self.driver.find_element_by_id("appTravelMonthStart"))
                hb_arrive_month.select_by_value(str(self.res_group[0][26]))
                # time.sleep(0.5)
                hb_arrive_year = Select(self.driver.find_element_by_id("appTravelYearStart"))
                hb_arrive_year.select_by_value(str(self.res_group[0][25]))
                # 中转的国家
                Transit_countries = Select(self.driver.find_element_by_id("countryTransitMalaysia"))
                Transit_countries.select_by_index(1)
                # time.sleep(0.5)
                # 入境通过
                pass_by = Select(self.driver.find_element_by_id("appEnterVia"))
                pass_by.select_by_index(2)
                # 航班返程信息
                # time.sleep(0.5)
                hb_end_data = Select(self.driver.find_element_by_id("appTravelDayEnd"))
                hb_end_data.select_by_value(self.data_i(self.res_group[0][30]))
                # time.sleep(0.5)
                hb_end_month = Select(self.driver.find_element_by_id("appTravelMonthEnd"))
                hb_end_month.select_by_value(str(self.res_group[0][29]))
                # time.sleep(0.5)
                hb_end_year = Select(self.driver.find_element_by_id("appTravelYearEnd"))
                hb_end_year.select_by_value(str(self.res_group[0][28]))
                # time.sleep(0.5)
                # 目的地国家
                arrive_country = Select(self.driver.find_element_by_id("countryDestinationHome"))
                arrive_country.select_by_index(1)
                # 返回中转的国家
                # time.sleep(0.5)
                end_Transit_countries = Select(self.driver.find_element_by_id("countryTransitHome"))
                end_Transit_countries.select_by_index(1)
                # 离镜通过
                end_pass_by = Select(self.driver.find_element_by_id("appExitVia"))
                end_pass_by.select_by_index(2)
                # time.sleep(0.5)
                # 中国地址
                self.driver.find_element_by_id("appAddress1").clear()
                self.driver.find_element_by_id("appAddress1").send_keys(self.res_info[0][9])
                self.driver.find_element_by_id("appAddress2").send_keys()
                # time.sleep(0.5)
                # 邮编
                self.driver.find_element_by_id("appPostcode").clear()
                self.driver.find_element_by_id("appPostcode").send_keys(self.res_info[0][26])
                # time.sleep(0.5)
                # 城市
                self.driver.find_element_by_id("appCity").clear()
                self.driver.find_element_by_id("appCity").send_keys(self.res_info[0][25])
                # time.sleep(0.5)
                # 省
                city = Select(self.driver.find_element_by_id("appProvince"))
                city.select_by_value(str(self.res_info[0][24]))
                # time.sleep(0.5)
                # 马来西亚地址
                self.driver.find_element_by_id("appMysAddress1").send_keys(self.res_group[0][31])
                # time.sleep(0.5)
                self.driver.find_element_by_id("appMysAddress2").send_keys(self.res_group[0][18])
                # 邮编
                self.driver.find_element_by_id("appMysPostcode").send_keys(self.res_group[0][24])
                # time.sleep(0.5)
                # 城市
                self.driver.find_element_by_id("appMysCity").send_keys(self.res_group[0][36])
                # time.sleep(0.5)
            except:
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email":self.res[1],"status":"2","text":"请检查提交信息是否正确"}
                # requests.post(url,data)
                # 
                # return -1
                pass


        try:
            # 保险
            print('保险')
            self.driver.find_element_by_id("iNo").click()
            time.sleep(0.5)
        except :
            pass
        try:
            # 支付方式
            print('支付方式')
            self.driver.find_element_by_id("paymentMethod").click()
            time.sleep(0.5)
        except:
            pass
        try:
            # 点击下一步
            print('点击下一步')
            self.driver.find_element_by_id("btnNext").click()
            time.sleep(1)
        except:
            pass

        try:
            a = self.driver.switch_to_alert().text
            print('==============\n', a, '\n==============')
            if '个月' in a:
                print('in alert 个月')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "有效期内", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)
            elif '有效日期' in a:
                print('in alert 有效日期')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "有效期过期", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)  
            elif 'You are not allowed to apply a new eNTRI' in a:
                print('in alert    You are not allowed to apply a new eNTRI')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "重复提交", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)
                print(self.res.json())       
            return -1
        except:
            print('no alert one')
        
        # 勾选同意协议的选择框
        print('勾选同意协议的选择框')
        self.driver.find_element_by_id("termCondition").click()
        time.sleep(0.5)
        # 点击同意按钮
        print('点击同意按钮')
        self.driver.find_element_by_id("btnSave").click()
        time.sleep(2)


        try:
            a = self.driver.switch_to_alert().text
            print('==============\n', a, '\n==============')
            if '个月' in a:
                print('in alert 3个月')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "有效期内", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)
            elif '有效日期' in a:
                print('in alert 有效日期')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "有效期过期", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)  
            elif 'You are not allowed to apply a new eNTRI' in a:
                print('in alert    You are not allowed to apply a new eNTRI')
                # url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                # data = {"email": self.res[1], "status": "2"}
                # requests.post(url, data)
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data_photo = {"email": self.res[1], "text": "重复提交", "type": "3"}
                _res = requests.post(url, data=data_photo)
                
                
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/malaysia_refund/gid/{}".format(self.res[7])
                _res = requests.get(url)
                print(self.res.json())       
            return -1
        except:
            print('no alert two')

        time.sleep(2)
        

        try:
            # 点击使用照片原件----改为确认
            print('点击确认')
            self.driver.find_element_by_id("btnConfirm").click()
            time.sleep(1)

            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "4"}
            requests.post(url, data)

            # 在弹出的选择框中点击确认
            self.driver.switch_to_alert().accept()
            # time.sleep(5) 
        except:
            pass

        # try:
        time.sleep(5)
        
        print('-----------------------------------------')
        if '系统检测到您的照片不符合规格' in self.driver.page_source:
            # 点击使用照片原件
            self.driver.find_element_by_id("btnConfirmNoEdit").click()
            time.sleep(1)
            # 在弹出的选择框中点击确认
            self.driver.switch_to_alert().accept()
            time.sleep(5)

        time.sleep(5)

        if '系统检测到您的照片不符合规格' in self.driver.page_source:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": self.res[1], "status": "2"}
            requests.post(url, data)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
            data_photo = {"email": self.res[1], "text": "照片不合格"}
            print('123s')
            print(data_photo)
            _res = requests.post(url, data_photo)
            # print(self.res.status_code, self.res.text)
            with open(r'{}\visa_photo\{}_log.json'.format(os.getcwd(), time.strftime('%Y%m%d')), 'a+')as f:
                json.dump(f"{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 照片不符合规格", f)
                f.write('\n]\n')
            
            return -2
        print('-----------------------------------------')
        try:
            print('点击弹框')
            # 将弹出的确认信息框关闭
            self.driver.find_element_by_xpath('//div[@id = "addBookDialogX"]/div/div/div[2]/div/div/div/div/button').click()
            print('---')
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//div[@id = "addBookDialogX"]/div/div/div/button').click()
            # self.driver.switch_to_alert().dismiss()
        except Exception as e:
            pass

        try:
            time.sleep(2)
            # 点击继续付款
            self.driver.find_element_by_id("btnSubmit").click()
        except Exception as e:
            pass

        try:
            # 点击账号密码付款
            time.sleep(2)
            self.driver.find_element_by_id("J_tip_qr").click()
            time.sleep(1)

        except Exception as e :
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
            # print(self.driver.page_source)
            time.sleep(1)

            # with open('visa_photo/zfb_code.html', 'w') as f:
            #     f.write(self.driver.page_source)
            print('- - ' * 50)
            if '验证码' in self.driver.page_source:
                print('- *' * 10)
                try:
                    # checkCodeImg1526628428404
                    # checkCodeImg1526629233305
                    captcha_element = self.driver.find_element_by_xpath(
                        '//img[@class="checkCodeImg"]')
                    self.driver.find_element_by_xpath(
                        '//input[@class="ui-input ui-input-checkcode"]').click()
                    print('* ' * 50)
                    # print(element)
                    captcha_left = captcha_element.location['x']
                    captcha_top = captcha_element.location['y']
                    captcha_right = captcha_element.location['x'] + captcha_element.size['width']
                    captcha_bottom = captcha_element.location['y'] + captcha_element.size['height']
                    print(captcha_left, captcha_top,captcha_right)
                    img = Image.open('visa_photo/captcha.png')
                    img = img.crop((captcha_left, captcha_top, captcha_right, captcha_bottom))
                    img.save('code_yunsu.png')
                    time.sleep(0.5)
                    # 获取验证码结果
                    result2 = upload(3040)
                    yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                    data = {'type': '3', 'num': '25'}
                    requests.post(yunsu_url, data=data)
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

            if '验证码错误' in self.driver.page_source:
                print('输入密码...')
                self.driver.find_element_by_id("payPasswd_rsainput").click()
                time.sleep(1)
                self.driver.find_element_by_id("payPasswd_rsainput").send_keys(GLOBAL_DATA[6])
                img = Image.open('visa_photo/captcha.png')
                img = img.crop((captcha_left, captcha_top-1, captcha_right, captcha_bottom))
                img.save('code_yunsu.png')
                # 获取验证码结果
                result2 = upload(3040)
                yunsu_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface"
                data = {'type': '3', 'num': '20'}
                requests.post(yunsu_url, data=data)
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
        except Exception as e:
            print(e)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email":self.res[1],"status":"2"}
            requests.post(url,data)
            print('00000000')
            
            return -1
        print('输入付款账号结束，进入确认付款')
        # try:
        #     self.driver.find_element_by_xpath('//span[@id = "payPassword_container"]/div').click()
        #     time.sleep(2)
        # except Exception as e:
        #     print(e)
        try:
            for i in range(2, 10):
                self.driver.find_element_by_id("payPassword_container").click()
                time.sleep(3)
                print('输入支付密码！...')
                ActionChains(self.driver).send_keys(Keys.NUMPAD1, Keys.NUMPAD8, Keys.NUMPAD5, Keys.NUMPAD8, Keys.NUMPAD8,
                                               Keys.NUMPAD8).perform()
                time.sleep(3)
                self.driver.find_element_by_xpath('//*[@id="J_authSubmit"]').click()
                time.sleep(5)
                if '您已成功付款' in self.driver.page_source:
                    print('付款成功！,..')
                    self.driver.save_screenshot('successful.png')
                    print('申请成功，付款成功！')
                    with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                        json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 付款成功!", f)
                        f.write('\n],\n')
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
                    data = {"email": self.res[1], "status": "1"}
                    requests.post(url, data)
                    time.sleep(10)
                    break
                else :
                    self.driver.find_element_by_xpath('//*[@id="J_GoBack_nobodyknows"]').click()
                    time.sleep(2)
                    self.driver.find_element_by_xpath('//div[@id="J-rcChannels"]/div/div/a[1]').click()
                    time.sleep(2)
                    self.driver.find_element_by_xpath(f'//*[@id="J_SavecardList"]/li[{i}]').click()


        except Exception as e:
            print('出现错误', e)
            time.sleep(5)
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email":self.res[1],"status":"2"}
            requests.post(url,data)
            
            
            return -1
        try:
            # 点击打印按钮
            self.driver.find_element_by_id("btnPrint").click()
            time.sleep(5)
            num = self.driver.window_handles
            # 获取当前页句柄
            self.driver.switch_to_window(num[1])
            url = self.driver.current_url.split("jasper")
            time.sleep(3)
            visa_url = url[0] + "note" + url[1]
            print(visa_url)
            pay_url = url[0] + "jasperpayment" + url[1]
            print(pay_url)
            print(self.res_info[0][38])
            visa_data = {"email": self.res_info[0][38], "evisa": visa_url, "receipt": pay_url}
            requests.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
            with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 电子签获取成功!", f)
                f.write('\n],\n')
            time.sleep(3)

        except:
            pass
        self.driver.quit()

    # 获取电子签模块
    def get_visa(self):
        # 不加载图片, 提升速度
        chrome_options = self.chrome_options
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=self.path + 'chromedriver', chrome_options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 30)
        try:
            res, sql_geren, sql_gongg = self.res, self.res_info, self.res_group
            
            print('打开网站')
            self.driver.get("https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh")
            # num = self.driver.window_handles
            # 获取当前页句柄
            # self.driver.switch_to_window(num[1])

            self.driver.find_element_by_class_name('ev-opt-2').click()

            time.sleep(3)

            # salt = "code_yunsu.png"
            # self.driver.save_screenshot(salt)
            # user = "csy518@icloud.com"
            password = '5678tyui'
            print('sleep')
            try:
                self.driver.find_element_by_id('lz_overlay_eyecatcher_close').click()
                time.sleep(1)
            except:
                pass
            try:
                self.driver.find_element_by_class_name('ev-opt-2').click()
                print('点击登录')
                time.sleep(1)
            except:
                pass
            try:
                time.sleep(1)
                self.driver.find_element_by_id('lz_overlay_eyecatcher_close').click()
                print('点击关闭红框')
                time.sleep(1)
            except:
                pass
            time.sleep(1)
           
            
            print('输入用户名...')
            print(self.res[1])
            self.driver.find_element_by_id("txtEmail").click()
            self.driver.find_element_by_id("txtEmail").send_keys(self.res[1])
            time.sleep(0.5)
            try:
                self.driver.switch_to_alert().accept()
            except:
                pass
            time.sleep(0.5)
            print('输入密码...')
            self.driver.find_element_by_id('txtPassword').click()
            self.driver.find_element_by_id('txtPassword').send_keys(password)
            time.sleep(0.5)

            # element = self.driver.find_element_by_xpath('//div[@class="col-sm-4"]/img')
            # img_url = self.driver.find_element_by_xpath('//div[@class = "form-group"]/div/img').get_attribute("src")
            # print(img_url)
            element = self.driver.find_element_by_xpath('//*[@id="txtQuestion"]')
            s = element.text.split(' ')
            a = int(s[0])
            b = int(s[2])
            ys = {
                '+': a + b,
                '-': a - b,
                'X': a * b,
            }
            result = str(ys[s[1]])
            print(result)
            self.driver.find_element_by_id("answer").click()
            self.driver.find_element_by_id("answer").send_keys(result)
            time.sleep(2)
            # 点击登录
            self.driver.find_element_by_id("btnSubmit").click()
            time.sleep(5)
            if self.driver.title != "Malaysia Electronic Visa Application":
                print("登录失败，即将重新申请")
                # time.sleep(3)
                return

            if int(sql_gongg[0][7]) <= 15:
                try:
                    self.driver.find_element_by_id("lz_overlay_eyecatcher_close").click()
                except:
                    pass
                time.sleep(3)
                # 点击加入免签计划
                self.driver.find_element_by_xpath(
                    '//div[@class = "col-lg-4 col-md-4 text-right"]/div[@class = "avenir"]/button').click()
                time.sleep(2)
                # 点击前往按钮
                self.driver.find_element_by_id("confirmNotice").click()
                time.sleep(2)
                appnumber = self.driver.find_element_by_xpath('//*[@id="historyServ"]/div[2]/div/div/table/tbody/tr/td[3]/div/a').text
                print(appnumber)
                visa_url = 'https://www.windowmalaysia.my/entri/note?appNumber=' + appnumber
                pay_url = 'https://www.windowmalaysia.my/entri/jasperpayment?appNumber=' + appnumber
                visa_data = {"email": sql_geren[0][38], "evisa": visa_url, "receipt": pay_url}
                requests.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getVisaStatus", data=visa_data)
                with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                    json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 电子签获取成功!", f)
                    f.write('\n],\n')
                print(visa_data)
                print('激活完成')
                self.driver.quit()
        except:
            print('= = = = = = = =')
            self.driver.quit()

    @staticmethod 
    def data_i(d):
        if type(d) is int:
            return str(d)
        return str(int(d))


class Registe:
    '''
    注册马来西亚账号
    '''

    def __init__(self, res, res_info, res_group):
        print('start...')
        self.res = res
        self.email = res[1]
        self.res_info = res_info[0]
        self.res_group = res_group[0]
        print(self.email)
        self.req = requests.Session()
        self.req.timeout = 60
        # self.req.proxies = {'http': '114.229.36.173:26236', 'https': '114.229.36.173:26236'}
        # self.req.proxies = {'http': '127.0.0.1:8888', 'https': '127.0.0.1:8888'}
        # self.req.verify = False
        self.req.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.10 Safari/537.36',
            # 'Cookie': 'JSESSIONID=F5F37F0A0403A6A3E22CE78B1E83E013; __cfduid=d08cfebc4cf65cc147d5a2cc36940edc01528342323; _ga=GA1.2.1523851791.1528442846; JSESSIONID=140CE94CB66813A49EFD0D3D4115631B; _gid=GA1.2.1105562878.1528680539; Hm_lvt_f299593a4267ae0229ba7d6a31a782d4=1528442846,1528680539; Hm_lpvt_f299593a4267ae0229ba7d6a31a782d4=1528680539'
        }
        # ip = self.proxy
        # self.req.proxies = {'http': ip, 'https': ip}
        self.registe_url = 'https://www.windowmalaysia.my/evisa/vlno_register.jsp?type=register'

        # self.registe_num = 0
        # self.email_num = 0

    @property
    def proxy(self):
        print('in proxy')
        ip = requests.get(
            'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=eb2ef3ba6a47461abd79a5fa9d5f964d&orderno=YZ20185159470jNDY4L&returnType=1&count=1').text.strip()
        if ip in ['10038', '10055', '10036']:
            time.sleep(5)
            ip = requests.get(
                'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=eb2ef3ba6a47461abd79a5fa9d5f964d&orderno=YZ20185159470jNDY4L&returnType=1&count=1').text.strip()
        print(f'正在切换ip: {ip}')
        return ip

    def requ(self, url, data=None):
        print('in requ', data)
        while 1:
            try:
                if not data:
                    print('in get')
                    res = self.req.get(url)
                    if res.status_code == 200:
                        print('in get over...')
                        break
                else:
                    print('in post')
                    res = self.req.post(url, data=data)
                    if res.status_code == 200:
                        print('in post over...')
                        break
                self.req.proxies = {'http': self.proxy, 'https': self.proxy}
            except:
                self.req.proxies = {'http': self.proxy, 'https': self.proxy}
                continue
        # print(res)
        return res

    # 注册
    @property
    def registe(self):
        print('正在注册...')
        # if self.registe_num > 5:
        #     return 2
        res = self.requ(self.registe_url)
        # yz_em_url = 'https://www.windowmalaysia.my/evisa/vlno_ajax_checkUsername.jsp'
        # em = {'email': self.email}
        # res_em = self.requ(yz_em_url, data=em).text
        # if 'Email address already exist!' in res_em:

        data = self.get_data(res)
        # print(data)
        # return
        re_url = 'https://www.windowmalaysia.my/evisa/register'
        res = self.requ(re_url, data=data)
        print('请求发送成功...进入判断...')
        if 'Resend Activation Email' in res.text:
            for _ in range(5):
                time.sleep(1)
                self.req.get(f'https://www.windowmalaysia.my/evisa/resendVerification?email={self.email}')
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data = {"email": self.email, "status": "1"}
            rs = requests.post(url, data=data)
            print(rs.json())
            print("注册成功...")
            with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
                json.dump(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{self.res}, 注册成功!", f)
                f.write('\n],\n')
            return 1
        # self.registe_num += 1
        print('注册失败!...')
        with open('xxx.html', 'wb') as f:
            f.write(res.content)
        return 0

    # 验证码
    def get_answer(self, res):
        reg = r'<b>(.*?) = \?</b></p>'
        code = re.findall(reg, res.text)[0]
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
        return answer

    # 获取注册数据
    def get_data(self, res):
        print('in get_data')

        answer = self.get_answer(res)

        reg = r'<input name="session_id" id="session_id" type="hidden" value="(.*?)">'
        da0 = re.findall(reg, res.text)[0]
        reg = r'<input name="ipAddress" id="ipAddress" type="hidden" value="(.*?)">'
        da1 = re.findall(reg, res.text)[0]
        reg = r'<input name="fullPage" id="fullPage" type="hidden" value="(.*?)">'
        da2 = re.findall(reg, res.text)[0]
        reg = r'<input name="locIPAddress" id="locIPAddress" type="hidden" value="(.*?)">'
        da3 = re.findall(reg, res.text)[0]
        reg = r'<input name="refImg" id="refImg" type="hidden" value="(.*?)">'
        da4 = re.findall(reg, res.text)[0]

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
            'password': '5678tyui',
            'cPassword': '5678tyui',
            'answer': answer,
            'btnRegister':  '注册',
        }
        print(data)
        return data


class Pipe:
    '''
    数据库查询
    '''
    def __init__(self):
        self.con = POOL.connection()
        # 获取数据库操作对象 cursor 游标
        self.cur = self.con.cursor()
        
    # 查询
    @property
    def select_info(self):
        try:
            for n1, n2 in [(1, 1), (1, 0), (2, 1), (2, 0)]:
                # print(n1, n2)
                # sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where id = 584'
                sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where type = {n1} and urgent = {n2}'
                # print(sql)
                self.cur.execute(sql)
                res = self.cur.fetchone()
                # print(res)
                if res:
                    self.res_group = 'select * from dc_business_malaysia_group where tids =' + str(res[7])
                    self.cur.execute(self.res_group)
                    self.res_group = self.cur.fetchall()
                   
                    sql_reg = 'select * from dc_business_malaysia_visa where group_id =' + str(res[7])
                    self.cur.execute(sql_reg)
                    self.res_info = self.cur.fetchall()
                    
                    return res, self.res_info, self.res_group
            print('\n未查询到数据...等待30s重新查询...\n')
            return 0, 0, 0
        except:
            return 0, 0, 0
        finally:
            self.cur.close()
            self.con.close()


def main():
    while 1:
        p = Pipe()
        res, res_info, res_group = p.select_info
        print(res)
        
        # res, res_info, res_group = 1, 0, 0
        if not res: 
            time.sleep(30)
            continue
        try:
            r = Registe(res, res_info, res_group)
            if (not res[3]) or (res[3] is 2):
                print('in reg')
                r.registe
                time.sleep(2)
                continue

            b = Base(False, res, res_info, res_group)
            if res[3] is 1 and (not res[4] or res[4] is 2):
                print('in email')
                b.email_163(res[4])
                time.sleep(2)
                if res[4]:
                    b.login()
                continue

            if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
                print('in login')
                b.login()
                time.sleep(2)
                continue

            if (not res[6] or res[6] is 2) and res[5] is 1:
                print('in visa')
                b.get_visa()
                time.sleep(2)

        except Exception as e:
            print('main error')
            print(e)
        finally:
            time.sleep(2)
            try:
                os.remove('code_yunsu.png')
            except:
                pass
            try:
                b.driver.quit()
                # pass
            except:
                pass


if __name__ == '__main__':
    main()
