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


class Email:
    def __init__(self, no_win=None):
        # self.path = sys.path[0] + '\\'
        self.usUrl = 'https://ceac.state.gov/GenNIV/Default.aspx'
        self.payUrl = 'https://cgifederal.secure.force.com/'

        # 设置 chrome_options 属性
        # self.chrome_options = webdriver.ChromeOptions()

        # 不加载图片
        # self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 无界面
        # self.chrome_options.add_argument('--headless')
        # 设置代理
        # self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1080')
        # 设置浏览器窗口大小
        # self.chrome_options.add_argument('window-size=1000x1500')
        # self.driver = webdriver.Chrome(
        #     executable_path=self.path + 'chromedriver', chrome_options=self.chrome_options)
        self.driver = webdriver.PhantomJS("phantomjs")
        # 设置隐性等待时间, timeout = 20
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        # 设置显性等待时间, timeout = 10, 间隔 0.3s 检查一次
        self.wait = WebDriverWait(self.driver, 10, 0.3, "请求超时")

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

    def __del__(self):
        self.driver.quit()

    def getData(self, email, pwd):
        try:
            self.driver.get("http://mail.163.com/index_alternate.htm")
            print("输入用户名")
            self.Wait("idInput", email)
            print("输入密码")
            self.Wait("pwdInput", pwd)
            print("点击登录")
            self.Wait("loginBtn")
            while 1:
                if self.driver.title == "网易邮箱6.0版":
                    break
            print("点击收件箱")
            self.Wait(xpath='//li[@title="收件箱"]')
            sleep(2)
            if 'VisaMalaysia' not in self.driver.page_source:
                self.Wait(xpath='//span[contains(text(), "其他2个文件夹")]')
                sleep(2)
                # self.Wait(xpath='//span[contains(text(), "垃圾邮件")]')
                eles = self.driver.find_elements_by_class_name(
                    "nui-tree-item-text")
                print("点击垃圾箱")
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
            content = self.driver.find_element_by_xpath(
                '//body/div/div[4]/p[2]/a')
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
    e.getData('chunpzf05861@163.com', 'ptgwr4295')
