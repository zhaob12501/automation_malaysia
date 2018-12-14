import json
import time

from pipelines import Conn
from settings import pool, redis, NUM


class Pipe(object):
    def __init__(self):
        self.conn = Conn()
        self.redis = redis.Redis(connection_pool=pool, db=0)

    # 查询
    def select_info(self, leng=4):
        length = self.redis.scard("malaysia")
        NoUser = self.redis.get("nouser")
        if length >= leng:
            return length
        sql = 'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, ' \
            'type from dc_business_email ' \
            'where type = 1 or type=2 order by id limit %s' % leng
        # f'where id=500'
        resp = self.conn.select_all(sql)
        if len(resp) == 0:
            if not NoUser:
                print("没有查到匹配的数据...", time.strftime("%Y-%m-%d %H:%M:%S"))
                self.redis.set("nouser", "1", 60 * 30)
        else:
            for res in resp:
                if length < leng:
                    Bool = self.redis.sismember("malaysia", res[7])
                    if not Bool:
                        # gid 加入集合, 防止再次加入任务
                        length += 1
                        from tasks import task_malaysia
                        insert_info = (
                            "插入",
                            res[0],
                            res[3],
                            res[4],
                            res[5],
                            res[6],
                            res[7],
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            "redis length:%s" % length
                        )
                        print("\n", insert_info, "\n")
                        self.redis.sadd("malaysia", res[7])
                        with open("logs/insert_info.log", "a") as f:
                            f.write(json.dumps(insert_info) + "\n")
                        task_malaysia.delay(res)
                        time.sleep(10)
        # print('\n执行任务结束...\n')
        return length


def main():

    while 1:
        try:
            # print('-' * 30)
            # print("马来西亚电子签", time.strftime('%Y-%m-%d %H:%M:%S'))
            # print('-' * 30)
            p = Pipe()
            length = p.select_info(leng=NUM)
            # input("===")
            time.sleep(1)
            # print(length)
        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == '__main__':
    # time.sleep(60)
    main()
