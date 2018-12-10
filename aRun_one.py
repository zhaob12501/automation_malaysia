import os
import time

from automation_malaysia import Automation_malaysia
from email163 import Email
from pipelines import Mysql


def main():
    while 1:
        os.system("cls")
        try:
            print('-' * 30)
            print("马来西亚电子签", time.strftime('%Y-%m-%d %H:%M:%S'))
            print('-' * 30)
            mysql = Mysql()

            sql = f'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type ' \
                'from dc_business_email where (type=1 or type=2)'  # and act_status=1 and sub_status!=1'
            res = mysql.getOne(sql)
            if res:
                sql_info = 'select * from dc_business_malaysia_group where tids =' + str(res[7])
                res_info = mysql.getOne(sql_info)
                sql_group = 'select * from dc_business_malaysia_visa where group_id =' + str(res[7])
                res_group = mysql.getOne(sql_group)
            else:
                time.sleep(5)
                continue
            print(res)
            if not (res and res_info and res_group):
                time.sleep(5)
                continue

            r = Automation_malaysia(res, res_info, res_group)

            # 邮箱注册
            if (not res[3]) or (res[3] is 2):
                print('in reg')
                r.registe()
                time.sleep(2)
                continue
            # 邮箱激活
            if res[3] is 1 and (not res[4] or res[4] is 2):
                e = Email()
                e.getData(res[1], res[2])
                del e
                continue
            if "eNTRI" in res_group[0][9]:
                print('\n--- 15天 ----\n')
                # 邮箱登录
                if (not res[5] or res[5] is 2 or res[5] is 4) and res[4] is 1:
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
            with open("logs/error.log", 'a') as f:
                f.write(repr(e) + '\n')
            time.sleep(5)


if __name__ == '__main__':
    main()
