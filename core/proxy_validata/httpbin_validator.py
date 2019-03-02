"""
该模块主要实现功能：通过对 http://httpbin.org/get 或 https://httpbin.org/get 发送请求，分析响应数据来判断proxy对象的协议类型（protocol）,响应速度（speed），代理等级(nick_type)
"""
import json
import time
import requests

from IPProxyPool.domain import Proxy
from IPProxyPool.settings import TEST_TIMEOUT
from IPProxyPool.utils.http import get_request_headers
from IPProxyPool.utils.log import logger


def check_proxy(proxy):
    # 准备代理ip字典
    proxies = {
        'http': 'http://{}:{}'.format(proxy.ip, proxy.port),
        'https': 'https://{}:{}'.format(proxy.ip, proxy.port),
    }
    # 检测代理ip
    http, http_nick_type, http_speed = __check_http_proxies(proxies)
    https, https_nick_type, https_speed = __check_http_proxies(proxies, False)
    # 返回检测结果
    # 代理IP支持的协议类型, http是0, https是1, https和http都支持是2
    if http and https:
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = https_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    return proxy

def __check_http_proxies(proxies, is_http=True):
    # 匿名类型: 高匿: 0, 匿名: 1, 透明: 2
    nick_type = -1
    # 响应速度, 单位s
    speed = -1
    # 判断是http还是https然后根据相应
    if is_http:
        test_url = 'http://httpbin.org/get'
    else:
        test_url = 'https://httpbin.org/get'
    # 发送请求解析返回参数来判断代理ip情况
    start_time = time.time()
    try: # 对于请求的操作都要try一下，防止请求不成功的情况
        response = requests.get(test_url, headers=get_request_headers(), proxies=proxies, timeout=TEST_TIMEOUT)
        # print(response.text)
        if response.ok:
            # 计算响应速度
            speed = round(time.time() - start_time, 2)
            # 匿名程度
            # 把响应的json字符串, 转换为字典
            dic = json.loads(response.text)
            # 获取来源IP: origin
            origin = dic['origin']
            proxy_connection = dic['headers'].get('Proxy-Connection', None)
            if ',' in origin:
                #    1. 如果 响应的origin 中有','分割的两个IP就是透明代理IP
                nick_type = 2
            elif proxy_connection:
                #    2. 如果 响应的headers 中包含 Proxy-Connection 说明是匿名代理IP
                nick_type = 1
            else:
                #  3. 否则就是高匿代理IP
                nick_type = 0
            return True, nick_type, speed
        return False, nick_type, speed
    except Exception as ex:
        # logger.exception(ex)
        return False, nick_type, speed


if __name__ == "__main__":
    proxy = Proxy('116.209.54.16', '9999')
    check_proxy(proxy)