import json
import time

import requests

from Base import Base
from pipelines import Conn, RedisQueue
from selenium.webdriver import ActionChains
from settings import (ALIPAY_KEY, BROKER_URL, PROXY_KEY,
                      PROXY_URL, GLOBAL_DATA, MALAYSIA_KEY, NC, alipay_Keys, pool)

# 1-支付宝
alipay_user = GLOBAL_DATA[5]
alipay_pwd = GLOBAL_DATA[6]

ali_no_win = True
st_input = False
redis_time = 15

# 2-支付宝
# alipay_user = GLOBAL_DATA[9]
# alipay_pwd  = GLOBAL_DATA[10]
# alipay_Keys = (
#     Keys.NUMPAD8, Keys.NUMPAD3, Keys.NUMPAD0,
#     Keys.NUMPAD6, Keys.NUMPAD0, Keys.NUMPAD4)
ali_no_win = False
# st_input = True


def timess():
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    return time.time()


def pay_over(email):
    print("\n\n", email, '申请成功，付款成功！', "\n\n")
    url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
    data = {"email": email, "status": "1"}
    requests.post(url, data)
    data_photo = {"email": email, "type": 1, "text": "等待电子签"}
    url = 'http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question'
    requests.post(url, data_photo)
    with open(f'visa_photo/{time.strftime("%Y%m%d")}_log.json', 'a') as f:
        json.dump(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}:{email}, 付款成功!", f)
        f.write('\n],\n')
    # time.sleep(3)


def ali_pay(email, alipay_url, noWin=False, st_input=False):
    print('打开支付宝， 进行付款...')
    driver = Base(no_win=noWin)
    driver.get_driver()
    # driver.driver.set_window_size(1980, 2000)
    driver.driver.get(alipay_url)
    driver.driver.maximize_window()
    if st_input:
        print("--扫码回车 确认手动付款--")
        print("--输入`a`回车 为测试自动付款--")
        a = input(">>>")
        if not a:
            url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getSubmitStatus"
            data = {"email": email, "status": "1"}
            requests.post(url, data)
            data_photo = {"email": email, "type": 1, "text": "等待电子签"}
            print(data_photo)
            requests.post(
                'http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/question', data_photo)
            driver.driver.quit()
            return 1
    for _ in range(10):
        if alipay_login(driver):
            break
    else:
        return 0
    print('输入付款账号结束，进入确认付款')
    for i in range(2, 13):
        try:
            driver.Wait("payPassword_container", sleep=1)
            time.sleep(1)
            print('输入支付密码！...')
            ActionChains(driver.driver).send_keys(*alipay_Keys).perform()
            # sms_code = input("\n是否有短信息验证码？填写完成后按回车\n>>>")
            # ====================================== #
            # 短信验证码
            # ====================================== #
            driver.Wait(xpath='//*[@id="J_authSubmit"]', sleep=1)
            # try:
            #     # driver.driver.switch_to.frame(driver.Wait(xpath='//iframe[@frameborder="no"]', text=NC, sleep=2))
            #     # driver.Wait("riskackcode")
            #     # time.sleep(15)
            #     # if "信息校验" in driver.driver.page_source:
            #     #     sms_code = input("\n请输入短信验证码\n>>>")
            #     #     driver.Wait("riskackcode", sms_code)
            #     time.sleep(20)
            #     pay_over(email)
            #     return
            #     # driver.Wait("J_authSubmit")
            # except Exception:
            #     pass
            time.sleep(1)
            for _ in range(60):
                page = driver.driver.page_source
                if "确认付款" in page or '您已成功付款' in page:
                    with open("logs/email_pay.log", "a", encoding="utf8") as f:
                        f.write(
                            f"付款完成: {email: <25}{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    driver.driver.save_screenshot('visa_photo/successful.png')
                    return 1
                elif "无法完成付款" in page:
                    break
                elif "抱歉，您操作超时，请重新登录" in page:
                    print("需要登录")
                    return -1
                else:
                    time.sleep(0.1)
            # driver.driver.save_screenshot(f"visa_photo/fail{time.strftime('%m%d-%H%M%S')}.png")
            driver.Wait(xpath='//*[@id="J_GoBack_nobodyknows"]')
            driver.Wait(
                xpath='//div[@id="J-rcChannels"]/div/div/a[1]', sleep=0.5)
            driver.Wait(xpath=f'//*[@id="J_SavecardList"]/li[{i}]', sleep=0.5)
            time.sleep(1)
        except Exception as e:
            with open("logs/error.log", "a", encoding="utf-8") as f:
                f.write(f"\n\n{time.strftime('%m%d-%H%M%S')}\n" + e)
    else:
        driver.driver.save_screenshot('visa_photo/successful.png')
        return 1


def alipay_login(driver):
    driver.Wait("J_tip_qr", sleep=1)
    print('输入用户名...')
    driver.Wait("J_tLoginId", alipay_user, sleep=1)
    driver.Wait("payPasswd_rsainput", alipay_pwd, sleep=1)
    time.sleep(1)
    if '验证码' in driver.driver.page_source:
        print('- *' * 10, '\n', '有验证码， 正在识别...')
        result = driver.get_captcha(driver.Wait(
            xpath='//img[@class="checkCodeImg"]', text=NC, sleep=1), pred_type="30400")
        print(f"验证码为: {result}")
        driver.Wait(
            xpath='//input[@class="ui-input ui-input-checkcode"]', text=result)
    # 点击付款
    print('点击付款...')
    driver.Wait("J_newBtn", sleep=1)
    time.sleep(1)
    try:
        alert = driver.driver.switch_to_alert()
        if "异常" in alert.text:
            alert.accept()
            driver.driver.refresh()
            return 0
    except Exception:
        pass
    for _ in range(5):
        # input("-")
        page = driver.driver.page_source
        if '验证码错误' in page or "请正确填写校验码" in page or "校验码错误" in page:
            driver.Wait(xpath='//img[@class="checkCodeImg"]')
            result = driver.get_captcha(driver.Wait(
                xpath='//img[@class="checkCodeImg"]', timeout=10, text=NC), pred_type="30400")
            print(f"验证码错误, 重新识别验证码为: {result}")
            driver.Wait("payPasswd_rsainput", alipay_pwd, sleep=1)
            driver.Wait(
                xpath='//input[@class="ui-input ui-input-checkcode"]', text=result)
            # 点击付款
            print('点击付款...')
            driver.Wait("J_newBtn", sleep=1)
            time.sleep(2)
            # driver.dirver.save_screenshot("logs/captcha_over.png")
        elif "确认付款" in page or '安全设置检测成功' in page:
            print("验证码正确...")
            return 1
        else:
            time.sleep(1)


def get_proxy():
        try:
            red = RedisQueue(PROXY_KEY)
        except Exception:
            return 0

        if not red.qsize:
            result = requests.get(PROXY_URL).json()
            """
            proxy-1: {
                "ERRORCODE": "0",
                "RESULT": [
                    {"port": "43617", "ip": "222.85.5.118"},
                    {"port": "43569", "ip": "180.122.20.108"},
                    {"port": "20443", "ip": "221.230.254.73"}
                ]
            }
            """
            if result.get("ERRORCODE") == "0" and result.get("ERRORCODE") != "10032":
                [red.put(f"{i['ip']}:{i['port']}") for i in result.get("RESULT")]
            elif result.get("ERRORCODE") in ["10036", "10038", "10055"]:
                time.sleep(5)
        pass
        time.sleep(5)
