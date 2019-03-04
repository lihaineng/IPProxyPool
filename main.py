"""
利用多进程启动程序
"""
from multiprocessing import Process

from core.proxy_api import ProxyApi
from core.proxy_spider.run_spider import RunSpider
from core.proxy_test import ProxyTester


def run():
    # 创建进程
    p1 = Process(target=RunSpider.start)
    p2 = Process(target=ProxyTester.start)
    p3 = Process(target=ProxyApi.start)
    # 开启进程
    process_list = [p1, p2, p3]
    for process in process_list:
        process.daemon = True  # 一定要设置为守护进程，一面某个进程运行玩影响其他进程
    # 阻塞主进成，只有三个线程结束了主进程才能结束,注意要在线程开启前设置
        process.start()
    for process in process_list:
        process.join()

if __name__ == '__main__':
    run()