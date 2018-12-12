import subprocess
import time

from settings import NUM, pool, redis

r = redis.StrictRedis(connection_pool=pool)
r.flushdb()
print(r.keys())

time.sleep(5)

try:
    subprocess.Popen(f"celery -A tasks worker -l info -c {NUM}", shell=True)
except KeyboardInterrupt:
    print("用户退出")

time.sleep(5)

try:
    subprocess.Popen("python aRun_more.py", shell=True)
except KeyboardInterrupt:
    print("用户退出")

# try:
#     subprocess.Popen("python aRun_All.py", shell=True)
# except KeyboardInterrupt:
#     print("用户退出")
