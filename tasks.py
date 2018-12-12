# from __future__ import absolute_import, unicode_literals
import time
from random import random

import redis
import requests
from celery import Celery

from automation_malaysia import Automation_malaysia
from email163 import Email
from pipelines import Conn
from settings import BROKER_URL, pool

#  celery -A tasks worker -c 3 -l info
#  catching classes that do not inherit from BaseException is not allowed
app = Celery("tasks", broker=BROKER_URL, backend=BROKER_URL)

app.conf.update(
    TIME_ZONE='UTC',
    USE_TZ=True,
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE="UTC")


@app.task()
def task_malaysia(res):
    print(res)
    con = Conn()
    try:
        red = redis.Redis(connection_pool=pool, db=0)
        sql1 = 'select * from dc_business_malaysia_group where tids=' + \
            str(res[7])
        res_group = con.select_all(sql1)
        sql2 = 'select * from dc_business_malaysia_visa where group_id=' + \
            str(res[7])
        res_info = con.select_all(sql2)

        if not (res_info and res_group):
            print("数据为空.....")
            # red.srem("malaysia", res[7])
            return -1

        r = Automation_malaysia(res, res_info, res_group)
        if res[6] == 1:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
            data = {
                "email": res[1],
                "type": "3"
            }
            requests.post(url, data=data)
            return 1

        # 邮箱注册
        if res[3] != 1:
            print('注册中....')
            if r.registe():
                print('注册成功...')
            else:
                print('注册失败 ...')

        # 邮箱激活
        elif res[3] == 1 and res[4] != 1:
            print("邮箱激活中......")
            e = Email()
            if e.getData(res[1], res[2]):
                print("激活成功 下一步....")
            else:
                print("激活失败，结束....")

        elif "eNTRI" in res_group[0][9]:
            print('\n--- 15天 ----\n')
            # 邮箱登录
            if res[5] != 1 and res[4] == 1:
                t = random() * 10
                print(t)
                time.sleep(t)
                print('登录-付款....')
                r.login()

            # 获取签证
            elif res[6] != 1 and res[5] == 1:
                print('==========开始获取电子签==========')
                r.get_visa()
    except Exception as e:
        print(e)
        return 0
    finally:
        time.sleep(2)
        red.srem("malaysia", res[7])


@app.task()
def register(res):
    con = Conn()
    sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
    res_info = con.select_all(sql2)
    sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
    res_group = con.select_all(sql1)

    r = Automation_malaysia(res, res_info, res_group)
    # 邮箱注册
    if res[3] != 1:
        print('注册中....')
        if r.registe():
            print('注册成功...')
        else:
            print('注册失败 ...')
    time.sleep(2)
    red = redis.Redis(connection_pool=pool, db=0)
    red.delete("reg")

    return 1


@app.task()
def active(res):
    e = Email()
    if e.getData(res[1], res[2].strip()):
        print("激活成功 下一步....")
    else:
        print("激活失败，结束....")
    time.sleep(2)
    red = redis.Redis(connection_pool=pool, db=0)
    red.delete("act")
    return 1


@app.task()
def visa(res):
    con = Conn()
    sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
    res_info = con.select_all(sql2)
    sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
    res_group = con.select_all(sql1)

    r = Automation_malaysia(res, res_info, res_group)
    # 邮箱注册
    if "eNTRI" in res_group[0][9]:
        print('\n--- 15天 ----\n')
        # 邮箱登录
        if res[5] != 1 and res[4] == 1:
            t = random() * 10
            print(t)
            time.sleep(t)
            print('登录-付款....')
            r.login()
    time.sleep(2)
    red = redis.Redis(connection_pool=pool, db=0)
    red.delete("sub")
    return 1


@app.task()
def get_visa(res):
    con = Conn()
    sql2 = f'select * from dc_business_malaysia_visa where group_id={res[7]}'
    res_info = con.select_all(sql2)
    sql1 = f'select * from dc_business_malaysia_group where tids={res[7]}'
    res_group = con.select_all(sql1)
    r = Automation_malaysia(res, res_info, res_group)
    if res[6] != 1 and res[5] == 1:
        print('==========开始获取电子签==========')
        r.get_visa()
    time.sleep(2)
    red = redis.Redis(connection_pool=pool, db=0)
    red.delete("vis")
    return 1
