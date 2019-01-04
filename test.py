import base64
import json
import time

import requests


def progress(url, head=None, data=False, **kwargs):
    """ 进度条显示下载过程 """
    # url = 'http://pecl.php.net/get/pecl_http-3.2.0.tgz'

    st = time.time()
    size = 0
    head = head if head else {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    result = requests.get(url, headers=head, stream=True, **kwargs)
    US = {
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    content_size = int(result.headers["content-length"])
    # unit = ("TB", US["TB"]) if content_size > US["TB"] else ("GB", US["GB"]) if content_size > US["GB"] else ("MB", US["MB"]) if content_size > US["MB"] else ("KB", US["KB"])
    unit = ("KB", US["KB"]) if content_size < US["MB"] else ("MB", US["MB"]) if content_size < US["GB"] else ("GB", US["GB"]) if content_size < US["TB"] else ("TB", US["TB"])
    if result.status_code == 200:
        print("[文件大小] {:.2f} {}".format(content_size / unit[1], unit[0]))
        with open("files/aaa.tgz", "wb") as f:
            for data in result.iter_content(chunk_size=US['KB']):
                f.write(data)
                size += len(data)
                a = '[下载进度] {0: >6.2f}% |{1: <50}| [{2}/{3}]'.format(
                    size / content_size * 100,
                    "█" * (size * 50 // content_size),
                    size // US["KB"],
                    content_size // US["KB"]
                )
                print(a, end="\r")
    print(f'\n全部下载完成! 用时{time.time() - st:.2f}秒')


progress(url='http://pecl.php.net/get/pecl_http-3.2.0.tgz')
# from time import sleep
# from tqdm import tqdm
# for i in tqdm(range(500)):
#     sleep(0.01)
