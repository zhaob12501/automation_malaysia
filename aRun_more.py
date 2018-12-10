import json
import time

from pipelines import Mysql
from settings import pool, redis, NUM
from tasks import task_malaysia


class Pipe(Mysql):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis(connection_pool=pool, db=0)

    # 查询
    def select_info(self):
        length = self.redis.scard("malaysia")
        NoUser = self.redis.get("nouser")
        if length >= NUM:
            return length

        sql = 'select username, email_no, email_pwd, reg_status, act_status, sub_status, visa_status, gid, type ' \
            'from dc_business_email where type = 1 or type=2'
        resp = self.getMany(sql, NUM)
        if len(resp) == 0:
            if not NoUser:
                print("没有查到匹配的数据...", time.strftime("%Y-%m-%d %H:%M:%S"))
                self.redis.set("nouser", "1", 60 * 30)
        else:
            for res in resp:
                if length < NUM:
                    Bool = self.redis.sismember("malaysia", res[7])
                    if not Bool:
                        # gid 加入集合, 防止再次加入任务
                        length += 1
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
        # print('\n执行任务结束...\n')
        return length


def main():
    while 1:
        try:
            p = Pipe()
            length = p.select_info()
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == '__main__':
    main()
