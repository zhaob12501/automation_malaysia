import redis

from settings import POOL, pool_alipay, ALIPAY_KEY


class Conn(object):
    conn = None
    cursor = None

    def __init__(self):
        self.conn = POOL.connection()
        self.cursor = self.conn.cursor()

    def close_conn(self):
        self.conn.close()
        self.cursor.close()

    def select_one(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result

    def select_all(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result


class RedisQueue(object):
    def __init__(self, name, namespace='queue'):
        # redis的默认参数为：host='localhost', port=6379， 其中db为定义redis database的数量
        self.__db = redis.StrictRedis(connection_pool=pool_alipay)
        self.__key = '%s:%s' % (namespace, name)

    @property
    def db(self):
        return self.__db

    @property
    def qsize(self):
        return self.__db.llen(self.name("l"))  # 返回队列里面list内元素的数量

    def put(self, item):
        self.__db.rpush(self.name("l"), item)  # 添加新元素到队列最右方

    @property
    def lgetall(self):
        val = self.__db.lrange(self.name("l"), 0, -1)
        return [self.bytes_str(i) for i in val]

    def lexists(self, key):
        return key in self.lgetall

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        return self.__db.blpop(self.name("l"), timeout=timeout)

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.name("l"))
        if item:
            return self.bytes_str(item)
        return item

    def hset(self, key, val):
        key = self.str_bytes(key)
        val = self.str_bytes(val)
        if self.__db.hsetnx(self.name(), key, val):
            self.put(key)
            return 1
        return 0

    def hget(self, key):
        key = self.str_bytes(key)
        val = self.__db.hget(self.name(), key)
        if val:
            return self.bytes_str(val)
        return None

    def hincrby(self, key, num):
        key = self.str_bytes(key)
        if isinstance(num, int):
            self.__db.hincrby(self.name(), key, num)

    def hdel(self, key):
        key = self.str_bytes(key)
        return self.__db.hdel(self.name(), key)

    def hexists(self, key):
        key = self.str_bytes(key)
        return self.__db.hexists(self.name(), key)

    @property
    def hgetall(self):
        val = self.__db.hgetall(self.name())
        val = {self.bytes_str(k): self.bytes_str(v) for k, v in val.items()}
        return val

    @property
    def hlen(self):
        return self.__db.hlen(self.name())

    def name(self, types="h"):
        return self.str_bytes(f"{types}_{self.__key}")

    def str_bytes(self, strs):
        return strs if strs.__class__ is bytes else str(strs).encode("utf8")

    def bytes_str(self, byte):
        return byte.decode("utf8") if byte.__class__ is bytes else str(byte) if byte else byte
