# import time

# import requests


# def progress(url, head=None, path=None, **kwargs):
#     """ 进度条显示下载过程 """
#     # url = 'http://pecl.php.net/get/pecl_http-3.2.0.tgz'

#     st = time.time()
#     size = 0
#     head = head if head else {
#         "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
#     }
#     result = requests.get(url, headers=head, stream=True, **kwargs)
#     US = {
#         "KB": 1024,
#         "MB": 1024 ** 2,
#         "GB": 1024 ** 3,
#         "TB": 1024 ** 4,
#     }
#     content_size = int(result.headers["content-length"])
#     # unit = ("TB", US["TB"]) if content_size > US["TB"] else ("GB", US["GB"]) if content_size > US["GB"] else ("MB", US["MB"]) if content_size > US["MB"] else ("KB", US["KB"])
#     unit = ("KB", US["KB"]) if content_size < US["MB"] else ("MB", US["MB"]) if content_size < US["GB"] else ("GB", US["GB"]) if content_size < US["TB"] else ("TB", US["TB"])
#     if result.status_code == 200:
#         print("[文件大小] {:.2f} {}".format(content_size / unit[1], unit[0]))
#         with open(path, "wb") as f:
#             for data in result.iter_content(chunk_size=US['KB']):
#                 f.write(data)
#                 size += len(data)
#                 a = '[下载进度] {0: >6.2f}% |{1: <50}| [{2}/{3}]'.format(
#                     size / content_size * 100,
#                     "█" * (size * 50 // content_size),
#                     size // US["KB"],
#                     content_size // US["KB"]
#                 )
#                 print(a, end="\r")
#     print(f'\n全部下载完成! 用时{time.time() - st:.2f}秒')


# progress(url='http://pecl.php.net/get/pecl_http-3.2.0.tgz')

class A(object):
    def go(self):
        print("go A go!")

    def stop(self):
        print("stop A stop!")

    def pause(self):
        raise Exception("Not Implemented")


class B(A):
    def go(self):
        super(B, self).go()
        print("go B go!")


class C(A):
    def go(self):
        super(C, self).go()
        print("go C go!")

    def stop(self):
        super(C, self).stop()
        print("stop C stop!")


class D(B, C):
    def go(self):
        super(D, self).go()
        print("go D go!")

    def stop(self):
        super(D, self).stop()
        print("stop D stop!")

    def pause(self):
        print("wait D wait!")


class E(B, C):
    pass


a = A()
b = B()
c = C()
d = D()
e = E()
# 说明下列代码的输出结果
a.go()      # go A go!
b.go()      # go A go!  go B go!
c.go()      # go A go!  go C go!
d.go()      # go A go!  go B go!  go C go! go D go!
e.go()      # 
a.stop()
b.stop()
c.stop()
d.stop()
e.stop()
a.pause()
b.pause()
c.pause()
d.pause()
e.pause()
