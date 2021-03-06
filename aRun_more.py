import json
import time

import requests

from pipelines import Conn, RedisQueue
from settings import ALIPAY_KEY, MALAYSIA_KEY, MALA_NUM_KEY, NUM, pool, redis
from tasks import task_malaysia, get_visa


class Pipe(object):
    def __init__(self):
        self.conn = Conn()
        # 马来西亚 gid
        self.red_mala = RedisQueue(MALAYSIA_KEY)
        # 马来西亚 是否正在付款
        self.red_alipay = RedisQueue(ALIPAY_KEY)
        # 马来西亚 mpid 存在个数
        self.red_num = RedisQueue(MALA_NUM_KEY)

    # 查询
    def select_info(self, leng=NUM):
        length = self.red_mala.hlen
        if length >= leng:
            return length
        sql = 'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type, mpid, application ' \
            'from dc_business_email where type = 1 or type=2'  # limit %s' % NUM
        resp = self.conn.select_all(sql)
        if len(resp):
            for res in resp:
                if res[6] == 1:
                    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question"
                    requests.post(url, data={"email": res[1], "type": "3"})
                    continue
                # 如果正在付款, 跳过
                if self.red_alipay.hexists(res[1]):
                    continue
                # 如果线程已满, 跳出
                if length >= leng or length >= (self.red_num.qsize + 5):
                    break
                # 获取电子签
                if res[5] == 1 and res[6] != 1 and self.red_mala.db.setnx(res[1], 1):
                    get_visa.delay(res)
                    time.sleep(2)
                    continue
                # 所有 mpid 占用线程个数的最小值
                mins = min([int(self.red_num.hget(j)) if not self.red_num.hset(j, 0) else 0 for j in set(i[9] for i in resp)])
                # 本个 mpid 占用线程的个数 是否最小 以及 gid 是否存在
                if mins == int(self.red_num.hget(res[9])) and self.red_mala.hset(res[7], f"{res[0]}-{res[1]}-{time.time()}"):
                    length += 1
                    self.red_num.hincrby(res[9], 1)
                    insert_info = (
                        "插入", res[0], res[3], res[4],
                        res[5], res[6], res[7], time.strftime("%Y-%m-%d %H:%M:%S"),
                        "redis length:%s" % length
                    )
                    print("\n", insert_info, "\n")
                    task_malaysia.delay(res)
                    time.sleep(2)
                    
                # elif self.red_mala.hexists(res[7]):
                #     if time.time() - float(self.red_mala.hget(res[7]).split("-")[-1]) > 60*6:
                #         self.red_mala.hdel(res[7])
                #         self.red_num.hincrby(res[9], -1)
        elif not self.red_mala.db.get("nouser"):
            print("没有查到匹配的数据...", time.strftime("%Y-%m-%d %H:%M:%S"))
            r = redis.StrictRedis(connection_pool=pool)
            [r.delete(key) for key in r.keys() if key.decode("utf-8").startswith("celery-task-meta-")]
            self.red_mala.db.set("nouser", "1", 60 * 30)
        return length


def main():
    while 1:
        try:
            p = Pipe()
            p.select_info()
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == '__main__':
    main()
