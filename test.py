from pipelines import RedisQueue

threds = 4

res = [
    ['a', 1],
    ['ab', 1],
    ['b', 2],
    ['c', 1],
    ['d', 3],
    ['e', 4],
    ['f', 1],
    ['g', 2],
    ['z', 6],
    ['ss', 6],
]
r = RedisQueue("aa")
q = RedisQueue("ab")
[q.hdel(i) for i in q.hgetall]
[r.hdel(i) for i in r.hgetall]
for _ in range(100):
    for i in res:
        mins = min([int(r.hget(j)) if not r.hset(j, 0) else 0 for j in set(i[1] for i in res)])
        if mins == int(r.hget(i[1])) and q.hset(i[0], '1'):
            print(i)
            r.hincrby(i[1], 1)
            print(r.hgetall)
            print()
