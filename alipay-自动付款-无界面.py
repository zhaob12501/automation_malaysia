from alipay import RedisQueue, ALIPAY_KEY, time, timess, ali_pay, pay_over


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
                    a = ali_pay(email, url, True)
                    del a
                    print("\n", "-*" * 20, "\n", "AliPay Over", "\n", email, "\n", timess()-st, "\n", "-*" * 20)
            else:
                if len(red.hgetall) != len(red.lgetall):
                    [red.hdel(i) for i in red.hgetall if i not in red.lgetall]
                    continue
                print("No pay", time.strftime("%Y-%m-%d %H:%M:%S"))
                time.sleep(5)
        except Exception:
            pass
        finally:
            if email:
                pay_over(email)
                red.hdel(email)
            time.sleep(3)
