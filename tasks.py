# from __future__ import absolute_import, unicode_literals
import time
from random import random

import redis
from celery import Celery

from automation_malaysia import Automation_malaysia
from email163 import Email
from pipelines import Mysql
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
    mysql = Mysql()

    try:
        red = redis.Redis(connection_pool=pool, db=0)
        sql2 = 'select * from dc_business_malaysia_visa where group_id=%s'
        res_info = mysql.getOne(sql2, res[7])
        sql1 = 'select * from dc_business_malaysia_group where tids=%s'
        res_group = mysql.getOne(sql1, res[7])

        if not (res_info and res_group):
            print("数据为空.....")
            # red.srem("malaysia", res[7])
            return -1

        r = Automation_malaysia(res, res_info, res_group)
        if res[6] == 1:
            data = {'email': res[1], 'type': 3}
            # red.srem("malaysia", res[7])
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
