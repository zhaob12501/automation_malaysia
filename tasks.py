# from __future__ import absolute_import, unicode_literals
import json
import time
from random import random

import redis
import requests
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from automation_malaysia import Automation_malaysia
from Base import Base
from email163 import Email
from fateadm import Captcha
from pipelines import Conn, RedisQueue
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from settings import (ALIPAY_KEY, MALA_NUM_KEY, BROKER_URL, GLOBAL_DATA, MALAYSIA_KEY, NC,
                      alipay_Keys, pool)

# 1-支付宝
alipay_user = GLOBAL_DATA[5]
alipay_pwd = GLOBAL_DATA[6]

ali_no_win = True
st_input = False
redis_time = 15

# 2-支付宝
# alipay_user = GLOBAL_DATA[9]
# alipay_pwd  = GLOBAL_DATA[10]
# alipay_Keys = (
#     Keys.NUMPAD8, Keys.NUMPAD3, Keys.NUMPAD0,
#     Keys.NUMPAD6, Keys.NUMPAD0, Keys.NUMPAD4)
ali_no_win = False
# st_input = True

#  celery -A tasks worker -c 3 -l info
#  catching classes that do not inherit from BaseException is not allowed
app = Celery("tasks", broker=BROKER_URL, backend=BROKER_URL)

app.conf.update(
    TIME_ZONE='UTC',
    USE_TZ=True,
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE="UTC"
)


@app.task(soft_time_limit=300)
def task_malaysia(res):
    print(res)
    while 1:
        try:
            con = Conn()
            red = RedisQueue(MALAYSIA_KEY)
            red_num = RedisQueue(MALA_NUM_KEY)
            break
        except Exception as e:
            print(f"=\n\n\n连接异常:\n{e}\n\n\n")
    try:
        sql1 = 'select * from dc_business_malaysia_group where tids=' + \
            str(res[7])
        res_group = con.select_all(sql1)
        sql2 = 'select * from dc_business_malaysia_visa where group_id=' + \
            str(res[7])
        res_info = con.select_all(sql2)

        r = Automation_malaysia(res, res_info, res_group)

        # 邮箱注册
        if res[3] != 1:
            print('=\n==============\n邮箱注册\n==============')
            if r.registe():
                print('注册成功...')

        # 邮箱激活
        elif res[3] == 1 and res[4] != 1:
            e = Email()
            print('=\n==============\n邮箱激活\n==============')
            if e.getData(res[1], res[2]):
                print("激活成功 下一步....")

        elif "eNTRI" in res_group[0][9]:
            print('\n--- 15天 ----\n')
            # 邮箱登录
            print('=\n==============\n登录-填写信息\n==============')
            if res[5] != 1 and res[4] == 1:
                t = random() * 10
                print(t)
                time.sleep(t)
                print('登录-付款....')
                r.login()

            # 获取签证
            elif res[6] != 1 and res[5] == 1:
                print('=\n==============\n开始获取电子签\n==============')
                r.get_visa()
    except SoftTimeLimitExceeded as e:
        print(f"SoftTimeLimitExceeded: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        red.get_nowait()
        red.hdel(res[7])
        red_num.hincrby(res[9], -1)


# @app.task()
# def register(res):
#     con = Conn()
#     sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
#     res_info = con.select_all(sql2)
#     sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
#     res_group = con.select_all(sql1)

#     r = Automation_malaysia(res, res_info, res_group)
#     # 邮箱注册
#     if res[3] != 1:
#         print('注册中....')
#         if r.registe():
#             print('注册成功...')
#         else:
#             print('注册失败 ...')
#     time.sleep(2)
#     red = redis.Redis(connection_pool=pool, db=0)
#     red.delete("reg")

#     return 1


# @app.task()
# def active(res):
#     e = Email()
#     if e.getData(res[1], res[2].strip()):
#         print("激活成功 下一步....")
#     else:
#         print("激活失败，结束....")
#     time.sleep(2)
#     red = redis.Redis(connection_pool=pool, db=0)
#     red.delete("act")
#     return 1


# @app.task()
# def visa(res):
#     con = Conn()
#     sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
#     res_info = con.select_all(sql2)
#     sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
#     res_group = con.select_all(sql1)

#     r = Automation_malaysia(res, res_info, res_group)
#     # 邮箱注册
#     if "eNTRI" in res_group[0][9]:
#         print('\n--- 15天 ----\n')
#         # 邮箱登录
#         if res[5] != 1 and res[4] == 1:
#             t = random() * 10
#             print(t)
#             time.sleep(t)
#             print('登录-付款....')
#             r.login()
#     time.sleep(2)
#     red = redis.Redis(connection_pool=pool, db=0)
#     red.delete("sub")
#     return 1


# @app.task()
# def get_visa(res):
#     con = Conn()
#     sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
#     res_info = con.select_all(sql2)
#     sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
#     res_group = con.select_all(sql1)
#     r = Automation_malaysia(res, res_info, res_group)
#     if res[6] != 1 and res[5] == 1:
#         print('==========开始获取电子签==========')
#         r.get_visa()
#     time.sleep(2)
#     red = redis.Redis(connection_pool=pool, db=0)
#     red.delete("vis")
#     return 1
