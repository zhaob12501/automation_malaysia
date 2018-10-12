import json
import os
import re
import sys
from time import sleep

import pymysql
import requests
from DBUtils.PooledDB import PooledDB
from lxml import etree

from selenium import webdriver

# with open('settings.json', 'r') as f:
#     GLOBAL_DATA = json.load(f)

# POOL = PooledDB(
#     pymysql,
#     3,
#     host=GLOBAL_DATA[0],
#     user=GLOBAL_DATA[1],
#     passwd=GLOBAL_DATA[2],
#     db=GLOBAL_DATA[3],
#     port=3306,
#     charset="utf8"
# )


class GetEmail:
    def __init__(self, *args, **kwargs):
        self.req = requests.Session()
        self.req.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }
        self.emailUrl = 'https://10minutemail.net/?lang=zh'
        res = self.req.get(self.emailUrl)
        self.freeEmail = res.text.split('class="mailtext" value="')[1].split('" />')[0]
        print(self.freeEmail)

    def activate(self):
        print('in activate ...')
        res = self.req.get(self.emailUrl)
        malayUrl = res.text.split('">eVISA Malaysia')[0].split('<td><a href="')[-1]
        malayUrl = 'https://10minutemail.net/' + malayUrl
        print(malayUrl)
        res = self.req.get(malayUrl)
        activateUrl = res.text.split('<a href="https://www.windowmalaysia.my')[1].split('">click here')[0]
        self.req.get(activateUrl)
        print('激活成功...')

class Pipe():
    def __init__(self):
        self.con = POOL.connection()
        self.cur = self.con.cursor()

    # 查询
    def select_info(self):
        try:
            for n1, n2 in [(1, 1), (1, 0), (2, 1), (2, 0)]:
                # print(n1, n2)
                sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where id = 252'
                # sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid from dc_business_email where type = {n1} and urgent = {n2}'
                self.cur.execute(sql)
                res = self.cur.fetchone()
                # print(1, res)
                if res:
                    # print('--')
                    # if res[3] is 1 and res[4] is 1 and res[5] is 1 and res[6] is 1: 
                    #     url = 'http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question'
                    #     data = {'email': res[1], 'type': 3}
                    #     requests.post(url, data=data)
                    #     continue
                    sql_gongg = 'select * from dc_business_malaysia_group where tids =' + str(res[7])
                    self.cur.execute(sql_gongg)
                    sql_gongg = self.cur.fetchall()
                    # print('###', sql_gongg)
                    sql_reg = 'select * from dc_business_malaysia_visa where group_id =' + str(res[7])
                    self.cur.execute(sql_reg)
                    sql_geren = self.cur.fetchall()
                    # print('%%%%', sql_geren)
                    return res, sql_geren, sql_gongg
            print('\n未查询到数据...等待30s重新查询...\n')
            return 0, 0, 0
        except Exception as e:
            print(e)
            return 0, 0, 0

    def __del__(self):
        self.cur.close()
        self.con.close()

class Automation_malaysia():
    '''
    注册马来西亚账号
    '''

    def __init__(self, res, res_info, res_group, email=''):
        print('start...')
        self.res = res
        self.email = email
        self.password = res[2]
        self.res_info = res_info[0]
        self.res_group = res_group[0]
        print(len(self.res_group), len(self.res_info))
        print(self.email)
        self.req = requests.Session()
        self.req.timeout = 300
        self.path = sys.path[0] + '\\'
        
        self.req.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.10 Safari/537.36',
        }
        self.registe_url = 'https://www.windowmalaysia.my/evisa/vlno_register.jsp?type=register'

    def requ(self, url, data=None):
        print('in requ', data)
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
                sleep(1)
                self.req.get(f'https://www.windowmalaysia.my/evisa/resendVerification?email={self.email}')
            return 1
        elif 'You have entered an invalid email address' in res.text:
            print('邮箱无效，更换邮箱...')
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/replaceEmail"
            data_p = {"email": self.email}
            res = requests.post(url, data_p).json()
        print('注册失败!...')
        with open('xxx.html', 'wb') as f:
            f.write(res.content)
        return 0

    # 获取注册数据
    def get_data(self, res):
        print('in get_data')

        answer = self.get_answer(res)

        reg = r'<input name="session_id" id="session_id" type="hidden" value="(.*?)">'
        da0 = re.findall(reg, res.text)[0]
        print(da0)
        reg = r'<input name="ipAddress" id="ipAddress" type="hidden" value="(.*?)">'
        da1 = re.findall(reg, res.text)[0]
        print(da1)
        reg = r'<input name="fullPage" id="fullPage" type="hidden" value="(.*?)">'
        da2 = re.findall(reg, res.text)[0]
        print(da2)
        reg = r'<input name="locIPAddress" id="locIPAddress" type="hidden" value="(.*?)">'
        da3 = re.findall(reg, res.text)[0]
        print(da3)
        reg = r'<input name="refImg" id="refImg" type="hidden" value="(.*?)">'
        da4 = re.findall(reg, res.text)[0]
        print(da4)
        print(len(self.res_info), len(self.res_group))
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
        print(data)
        return data
        
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


def main():
    while 1:
        p = Pipe()
        res, res_info, res_group = p.select_info()
        print(res)
        if not res:
            sleep(30)
            continue
        e = GetEmail()
        r = Automation_malaysia(res, res_info, res_group, email=e.freeEmail)
        r.registe()
        while 1:
            try:
                e.activate()
                break
            except:
                sleep(5)
        # try:
        #     # 邮箱注册
        #     if (not res[3]) or (res[3] is 2):
        #         print('in reg')
        #         sleep(2)
        #         continue
        #     # 邮箱激活
        #     if res[3] is 1 and (not res[4] or res[4] is 2):
        #         print('in email')
        #         sleep(2)
        #         continue
            # # 邮箱登录
            # if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
            #     print('in login')
            #     r.login()
            #     sleep(2)
            #     continue
            # # 获取签证
            # if (not res[6] or res[6] is 2) and res[5] is 1:
            #     print('in visa')
            #     r.get_visa()
            #     sleep(2)

        # except Exception as e:
        #     print(e)
        # finally:
        #     sleep(2)
        #     try:
        #         os.remove('code_yunsu.png')
        #     except:
        #         pass

if __name__ == '__main__':
    g = GetEmail()
    
    res = g.req.get(g.emailUrl)
    freeEmail = res.text.split('class="mailtext" value="')[1].split('" />')[0]
    print(freeEmail)
