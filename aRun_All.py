import json
import time

from pipelines import Conn
from settings import pool, redis, NUM
from tasks import register, active, visa, get_visa
import requests

"""
activate mala
python Run.py
"""


class Pipe(object):
    def __init__(self):
        self.conn = Conn()
        self.redis = redis.Redis(connection_pool=pool, db=0, decode_responses=True)  #

    def ins_info(self, info, res):
        infos = [
            info, res[0], res[3], res[4], res[5], res[6], res[7],
            time.strftime("%Y-%m-%d %H:%M:%S")
        ]
        print(infos)
        with open("logs/insert_info.log", "a") as f:
            f.write(json.dumps(infos))

    # 查询
    def select_info(self):
        # act_len  = self.redis.scard("active")
        # visa_len = self.redis.scard("visa")
        reg = self.redis.scard("reg")
        act = self.redis.scard("act")
        sub = self.redis.scard("sub")
        vis = self.redis.scard("vis")

        if reg and act and sub and vis:
            return

        sql = 'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, ' \
            'type from dc_business_email where type=1 or type=2'
        # f'where id=500'
        resp = self.conn.select_all(sql)
        for res in resp:
            if res[6] == 1:
                url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                data = {"email": res[1], "type": "3"}
                requests.post(url, data=data)
            if res[3] != 1:
                self.ins_info("注册", res)
                self.redis.sadd("reg", res[7])
                register.delay(res)
            if res[3] == 1 and res[4] != 1:
                self.ins_info("激活", res)
                self.redis.set("act", "1", nx=True)
                active.delay(res)
            if res[4] == 1 and res[5] != 1:
                self.ins_info("注册", res)
                self.redis.set("act", "1", nx=True)
                visa.delay(res)
            if res[5] == 1 and res[6] != 1:
                self.ins_info("提取", res)
                self.redis.set("vis", "1", nx=True)
                get_visa.delay(res)
        return


def main():
    while 1:
        try:
            # print('-' * 30)
            # print("马来西亚电子签", time.strftime('%Y-%m-%d %H:%M:%S'))
            # print('-' * 30)
            p = Pipe()
            p.select_info()
            # input("===")
            time.sleep(1)
            # print(length)
        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == '__main__':
    # time.sleep(60)
    # main()
    p = Pipe()
    p.redis
