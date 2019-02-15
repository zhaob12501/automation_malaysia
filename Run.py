import subprocess
import time

from settings import NUM, pool, pool_alipay, redis

r = redis.StrictRedis(connection_pool=pool)
rd = redis.StrictRedis(connection_pool=pool_alipay)
r.flushdb()
rd.delete("l_queue:malaysia")
rd.delete("h_queue:malaysia")
if int(time.strftime("%H") < 9):
    rd.flushall()
time.sleep(3)

try:
    subprocess.Popen(f"celery -A tasks worker -l info -c {NUM}", shell=True)
except KeyboardInterrupt:
    print("用户退出")

time.sleep(3)

# try:
#     subprocess.Popen("python alipay.py", shell=True)
# except KeyboardInterrupt:
#     print("用户退出")

time.sleep(3)

try:
    subprocess.Popen("python aRun_more.py", shell=True)
except KeyboardInterrupt:
    print("用户退出")

# try:
#     subprocess.Popen("python aRun_All.py", shell=True)
# except KeyboardInterrupt:
#     print("用户退出")
