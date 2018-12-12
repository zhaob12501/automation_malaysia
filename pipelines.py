from settings import POOL


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
