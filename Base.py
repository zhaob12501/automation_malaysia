import json
import os
import time

from selenium import webdriver
from selenium.common.exceptions import InvalidElementStateException as IESE
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from fateadm import Captcha
from settings import BASEDIR, NC


class Base:
    """ 基类 """
    # 设置 chrome_options 属性
    chrome_options = webdriver.ChromeOptions()
    # 设置浏览器窗口大小
    chrome_options.add_argument('window-size=1800x2000')

    # chrome_options.add_extension(extension_path)

    def __init__(self, no_win=False, no_img=False):
        # 不加载图片
        if no_img:
            self.chrome_options.add_argument(
                'blink-settings=imagesEnabled=false')
        # 无界面
        if no_win:
            self.chrome_options.add_argument('--headless')
        # 设置代理
        # self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1080')

        # for linux/*nix, download_dir="/usr/Public"
        download_dir = os.path.join(BASEDIR, 'files')
        # ----------页面打印版pdf下载-----------------
        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local"
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        # ----------网页版pdf直接下载-----------------
        profile = {
            "plugins.plugins_list": [{
                "enabled": False, "name": "Chrome PDF Viewer"
            }],  # Disable Chrome's PDF Viewer
            "download.default_directory": download_dir,
            "download.extensions_to_open": "applications/pdf",
            'printing.print_preview_sticky_settings.appState': json.dumps(appState),
            'savefile.default_directory': download_dir
        }
        self.chrome_options.add_experimental_option("prefs", profile)

    # 打开 driver
    def get_driver(self):
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # 设置隐性等待时间, timeout = 20
        # self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    # 检测元素 / 点击 / 发送字符 / 选择下拉框
    def Wait(self, idName=None, text=None, timeout=5, sleep=0.1, **kwargs):
        """ 设置显性等待, 每 0.3s 检查一次
        Parameter:
            idName  : 选择器规则, 默认idName
            text    : 需要发送的信息 (非 NC --> 'noClick')
            timeout : 等待时间
            kwargs  : 其它选择器
                xpath or css or tag_name or class_name or name
        """
        assert idName or kwargs
        time.sleep(sleep)
        if idName:
            locator = (By.ID, idName)
        elif kwargs.get("xpath"):
            locator = (By.XPATH, kwargs.get("xpath"))
        elif kwargs.get("css"):
            locator = (By.CSS_SELECTOR, kwargs.get("css"))
        elif kwargs.get("tag_name"):
            locator = (By.TAG_NAME, kwargs.get("tag_name"))
        elif kwargs.get("class_name"):
            locator = (By.CLASS_NAME, kwargs.get("class_name"))
        elif kwargs.get("name"):
            locator = (By.NAME, kwargs.get("name"))

        # 设置显性等待时间, timeout = 5, 间隔 0.2s 检查一次
        wait = WebDriverWait(self.driver, timeout, 0.2, "请求超时")
        element = wait.until(EC.presence_of_element_located(locator))
        if not text:
            element.click()
        elif text != NC:
            try:
                element.clear()
            except IESE:
                pass
            element.send_keys(text)
        return element

    def choiceSelect(self, elem=None, value=None, index=None, t=0.3):
        """ 下拉框选择器
            根据 value 选择下拉框
        """
        element = Select(elem)
        if value:
            element.select_by_value(value)
        elif index:
            element.select_by_index(index)
        return 0

    def get_captcha(self, elem=None, pred_type=None):
        img = elem.screenshot_as_png
        rsp = Captcha(img_data=img, pred_type=pred_type)
        return rsp.pred_rsp.value

    def __del__(self):
        try:
            self.driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    from base64 import b64decode as bd
    print(
        f"{(int(bd(bd('OXY4TlhNM2JqaEtObms0V0RZaE5Tbz0=')[3:])[::2]) - 3) // 6 - 1219:0>6}")
