import requests
import time


def get_proxy():
    url = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=eb2ef3ba6a47461abd79a5fa9d5f964d&orderno=YZ20185159470jNDY4L&returnType=1&count=1"
    text = requests.get(url).text.strip()
    if "10036" in text or "10038" in text or "10055" in text:
        time.sleep(5)
        text = requests.get(url).text
    return text


def main():
    url_login = "https://www.windowmalaysia.my/evisa/evisa.jsp?alreadyCheckLang=1&lang=zh"
    url = "https://www.windowmalaysia.my/evisa/captchaImaging?&_=%s" % (int(time.time() * 1000))
    req = requests.session()
    proxy = get_proxy()
    req.proxies = {
        "http": proxy,
        "https": proxy
    }
    print(f"使用代理: {proxy}")
    req.get(url_login)
    for i in range(3000):
        print(f"\r{i+1}/3000", end="")
        html = req.get(url)
        if html.status_code == 200 and html.content:
            img = html.content
            with open(f"./code/code{int(time.time() * 1000)}.png", "wb") as f:
                f.write(img)
        else:
            proxy = get_proxy()
            req.proxies = {
                "http": proxy,
                "https": proxy
            }
            print(f"更换代理: {proxy}")


if __name__ == "__main__":
    main()
