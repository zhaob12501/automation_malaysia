import sys
from time import sleep, strftime

import selenium
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from pymouse import PyMouse

import requests
from yunsu import upload

NC = "noClick"


class Base:
    """ 浏览器基类, 保持同一个 driver """

    def __init__(self, no_win=None):
        self.path = sys.path[0] + '\\'
        self.usUrl = 'https://ceac.state.gov/GenNIV/Default.aspx'
        self.payUrl = 'https://cgifederal.secure.force.com/'

        # 设置 chrome_options 属性
        self.chrome_options = webdriver.ChromeOptions()

        # 不加载图片
        # self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 无界面   
        self.chrome_options.add_argument('--headless')
        # 设置代理
        # self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1080')
        # 设置浏览器窗口大小
        self.chrome_options.add_argument('window-size=1000x1500')
        self.driver = webdriver.Chrome(
            executable_path=self.path + 'chromedriver', chrome_options=self.chrome_options)
        # 设置隐性等待时间, timeout = 20
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        # 设置显性等待时间, timeout = 10, 间隔 0.3s 检查一次
        self.wait = WebDriverWait(self.driver, 10, 0.3, "请求超时")

    # 获取验证码

    def getCaptcha(self, id=''):
        """ 验证码识别
            根据页面验证码元素位置, 截取验证码图片
            发送验证码识别请求,返回验证码文字

            Returns: result (str)
        """
        print("正在识别验证码...")
        self.Wait(id, NC)

        captcha = self.driver.find_element_by_id(id)
        self.driver.save_screenshot('captcha.png')
        captcha_left = captcha.location['x']
        top = 0 if captcha.location['y'] < 1200 else 910
        captcha_top = captcha.location['y'] - top
        captcha_right = captcha.location['x'] + captcha.size['width']
        captcha_bottom = captcha.location['y'] + captcha.size['height'] - top
        # print(captcha_left, captcha_top, captcha_right, captcha_bottom)
        img = Image.open('captcha.png')
        img = img.crop((captcha_left, captcha_top,
                        captcha_right, captcha_bottom))
        img.save('code.png')
        sleep(0.5)
        result = upload()
        print(f"验证码为: {result}")
        return result

    # 检测元素 / 点击 / 发送字符 / 选择下拉框
    def Wait(self, idName=None, text=None, xpath=None, css=None):
        """ 设置显性等待, 每 0.3s 检查一次
            Parameter:
                idName, xpath, className: 选择器规则, 默认idName
                text: 需要发送的信息 (非 NC --> 'noClick')
        """
        try:
            assert idName or xpath or css
        except AssertionError:
            pass
        if idName:
            locator = ("id", idName)
        elif xpath:
            locator = ("xpath", xpath)
        elif css:
            locator = ("css selector", css)

        try:
            self.wait.until(EC.presence_of_element_located(locator))
            if not text:
                self.driver.find_element(*locator).click()
            elif text != NC:
                try:
                    self.driver.find_element(*locator).clear()
                except selenium.common.exceptions.InvalidElementStateException:
                    pass
                self.driver.find_element(*locator).send_keys(text)
            return self.driver.find_element(*locator)
        except Exception as e:
            pass
        return 0

    def choiceSelect(self, selectid=None, value=None, t=0.3):
        """ 下拉框选择器
            根据 value 选择下拉框
        """
        try:
            assert selectid and value
        except AssertionError:
            pass
        sleep(t)
        self.Wait(selectid, text=NC)
        try:
            element = Select(self.driver.find_element_by_id(selectid))
            element.select_by_value(value)
        except Exception as e:
            pass

        return 0

    def waitIdSel(self, idlist=None, selist=None):
        """ 对 idlist 进行点击/发送字符串 或对 selist 进行选择
            Returns: 
                [] 空列表
        """
        if idlist:
            for idName, value in idlist:
                self.Wait(idName, value)
        if selist:
            for idName, value in selist:
                self.choiceSelect(idName, value)

        return []

    def __del__(self):
        self.driver.quit()


class Email(Base):
    def getData(self, email, pwd):
        try:
            self.driver.get("http://mail.163.com/index_alternate.htm")
            print("输入用户名")
            self.Wait("idInput", email)
            print("输入密码")
            self.Wait("pwdInput", pwd)
            print("点击登录")
            self.Wait("loginBtn")
            print("点击收件箱")
            self.Wait(xpath='//li[@title="收件箱"]')
            sleep(2)
            if 'VisaMalaysia' not in self.driver.page_source:
                self.Wait(xpath='//span[contains(text(), "其他2个文件夹")]')
                sleep(2)
                # self.Wait(xpath='//span[contains(text(), "垃圾邮件")]')
                print("点击其他邮件")
                eles = self.driver.find_elements_by_class_name("nui-tree-item-text")
                print("点击垃圾箱", len(eles))

                eles[14].click()
                sleep(2)
            if 'VisaMalaysia' not in self.driver.page_source:
                print("无邮件")
                url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
                data_02 = {"email":  email, "status": "4", "status_if": 1}
                requests.post(url_02, data_02)
                return 0

            print('点击第一封邮件')
            self.Wait(xpath='//span[contains(text(), "VisaMalaysia")]')
            sleep(2)
            f2 = self.driver.find_element_by_class_name("oD0")
            self.driver.switch_to.frame(f2)
            sleep(2)
            print('获取链接地址')
            # self.Wait(xpath='//body/div/div[4]/p[2]/a', text=NC)
            content = self.driver.find_element_by_xpath('//body/div/div[4]/p[2]/a')
            em_url = content.get_attribute('href')
            print(em_url)
            res = requests.get(em_url)
            print("激活成功")
            act_url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            act_data = {"email":  email, "status": "3"}
            requests.post(act_url, data=act_data)
            sleep(3)
            return 1
        except Exception as e:
            print(e, '-' * 20, sep='\n')
            url_02 = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/getEmailStatus"
            data_02 = {"email":  email, "status": "4"}
            requests.post(url_02, data_02)
            return 0


        





if __name__ == '__main__':
    e = Email()
    e.getData(1, 1)    
