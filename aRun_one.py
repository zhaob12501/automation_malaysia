import os
import time

import requests

from automation_malaysia import Automation_malaysia
from email163 import Email
from pipelines import Conn, RedisQueue
from settings import ALIPAY_KEY, MALAYSIA_KEY, POOL


class Pipe():
    def __init__(self):
        self.con = POOL.connection()
        self.cur = self.con.cursor()
        self.red = RedisQueue(MALAYSIA_KEY)
        self.red_a = RedisQueue(ALIPAY_KEY)

    # 查询
    def select_info(self):
        try:
            # for n1, n2 in [(1, 1), (1, 0), (2, 1), (2, 0)]:
                # print(n1, n2)
            sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type ' \
                'from dc_business_email where (type=1 or type=2)'   # and mpid=151'and act_status=1 and sub_status!=1'
            sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type '\
                f'from dc_business_email where gid = 10675'
            self.cur.execute(sql)
            res = self.cur.fetchone()
            for _ in range(10):
                if not res or not self.red_a.hexists(res[1]):
                    break
                res = self.cur.fetchone()
            print(1, res)
            if res:
                if res[6] == 1:
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                    requests.post(url, data={"email": res[1], "type": "3"})
                    return
                if self.red.hexists(res[1]):
                    return
                sql_gongg = 'select * from dc_business_malaysia_group where tids =' + \
                    str(res[7])
                self.cur.execute(sql_gongg)
                sql_gongg = self.cur.fetchall()
                # print('###', sql_gongg)
                sql_reg = 'select * from dc_business_malaysia_visa where group_id =' + \
                    str(res[7])
                self.cur.execute(sql_reg)
                sql_geren = self.cur.fetchall()
                if sql_geren and sql_gongg:
                    return res, sql_geren, sql_gongg
                else:
                    print("数据库查询出现空值")
                    return res, 0, 0
            print('\n未查询到数据...等待5s重新查询...\n')
            return 0, 0, 0
        except Exception:
            return 0, 0, 0

    def __del__(self):
        self.cur.close()
        self.con.close()


def main():
    while 1:
        try:
            print('-' * 30)
            print("马来西亚电子签", time.strftime('%Y-%m-%d %H:%M:%S'))
            print('-' * 30)
            p = Pipe()
            res, res_info, res_group = p.select_info()

            print(res)
            if not (res and res_info and res_group):
                time.sleep(5)
                continue

            if res[6] == 1:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data = {
                    "email": res[1],
                    "type": "3"
                }
                requests.post(url, data=data)
                continue

            r = Automation_malaysia(res, res_info, res_group)

            try:
                # 邮箱注册
                if (not res[3]) or (res[3] is 2):
                    print('\n==============\n邮箱注册\n==============')
                    r.registe()
                    time.sleep(2)
                    continue
                # 邮箱激活
                if res[3] is 1 and (not res[4] or res[4] is 2):
                    print('\n==============\n邮箱激活\n==============')
                    e = Email()
                    e.getData(res[1], res[2])
                    del e
                    continue
                if "eNTRI" in res_group[0][9]:
                    # print('\n--- 15天 ----\n')
                    # 登录-填写信息
                    if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
                        print('\n==============\n登录-填写信息\n==============')
                        print('in login')
                        r.login()
                        time.sleep(2)
                        continue

                    # 获取签证
                    if (not res[6] or res[6] is 2) and res[5] is 1:
                        print('\n==============\n开始获取电子签\n==============')
                        r.get_visa()
                        continue

                    # if res[8] is 2 and res[6] is 2:
                    #     print('\n==============\n开始获取电子签\n==============')
                    #     r.get_visa()
                elif "eVISA" in res_group[0][9]:
                    print('\n--- 30天 ----\n')
                    # 邮箱登录
                    if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
                        print('in login')
                        r.thLogin()
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
            # finally:
            #     time.sleep(2)
            #     try:
            #         os.remove('code.png')
            #     except Exception:
            #         pass
        except Exception as e:
            print(e)
            with open("logs/error.log", 'a') as f:
                f.write(repr(e) + '\n')
            time.sleep(5)


if __name__ == '__main__':
    main()
