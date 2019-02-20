from alipay import RedisQueue, ALIPAY_KEY, time, timess, ali_pay, pay_over
st_input = True


if __name__ == "__main__":
    while 1:
        email = ""
        try:
            red = RedisQueue(ALIPAY_KEY)
        except Exception:
            time.sleep(5)
            continue
        try:
            email = red.get_nowait()
            if email:
                url = red.hget(email)
                if url:
                    st = timess()
                    print("\n", "-*" * 20, "\n", "AliPay Start", "\n", email, "\n", st, "\n", "-*" * 20)
                    a = ali_pay(email, url, False, st_input=st_input)
                    del a
                    red.db.delete("nouser_pay")
                    print("\n", "-*" * 20, "\n", "AliPay Over", "\n", email, "\n", timess() - st, "\n", "-*" * 20)
            else:
                if len(red.hgetall) != len(red.lgetall):
                    [red.hdel(i) for i in red.hgetall if i not in red.lgetall]
                    continue
                if not red.db.get("nouser_pay"):
                    print("没有查到匹配的数据...", time.strftime("%Y-%m-%d %H:%M:%S"))
                    red.db.set("nouser_pay", "1", 60 * 30)
        except Exception:
            pass
        finally:
            if email:
                pay_over(email)
                red.hdel(email)
            time.sleep(5)
