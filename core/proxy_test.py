"""
本模块的作用是:对数据库中的proxy进行检测更新
"""
import schedule
import time
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

from queue import Queue

from core.db.mongo_pool import MongodbPool
from core.proxy_validata.httpbin_validator import check_proxy
from settings import MAX_SCORE, TEST_PROXIES_ASYNC_COUNT, TEST_PROXIES_INTERVAL


class ProxyTester(object):
    def __init__(self):
        # 建立数据库对象
        self.mongodpool = MongodbPool()
        # 建立队列
        self.queue = Queue()
        # 建立携程池
        self.gevent_pool = Pool()

    def make_circulation(self, temp):  #　这个temp必须要，这跟callback函数有关
        # 通过死循环来让携程一直运行下去
        self.gevent_pool.apply_async(self.__excute_every_proxy, callback=self.make_circulation)

    def run(self):
        # 从数据库中查处所有数据
        proxies = self.mongodpool.find_all()
        # 对每个proxy对象进行检测
        for proxy in proxies:
            self.queue.put(proxy)
        for i in range(TEST_PROXIES_ASYNC_COUNT): #　通过循环次数来创建异步个数
            self.gevent_pool.apply_async(self.__excute_every_proxy, callback=self.make_circulation)
        self.queue.join()

    def __excute_every_proxy(self):
        proxy = self.queue.get()
        proxy = check_proxy(proxy)
        # 对检测结果进行判断
        if proxy.speed == -1:
            # 若果不能联通就将分数减１
            proxy.score -= 1
            if proxy.score == 0:
                # 如果结果为０就删除
                self.mongodpool.delete_one(proxy)
            else:
                # 否则更新该代理IP
                self.mongodpool.update_one(proxy)
        else:
            # 若果能联通就将分数设为最高分
            proxy.score = MAX_SCORE
            self.mongodpool.update_one(proxy)
        self.queue.task_done()

    @classmethod
    def start(cls):
        #  4.2.1 创建本类对象
        proxy_tester = cls()
        #  4.2.2 调用run方法
        proxy_tester.run()

        # 4.2.3 每间隔一定时间, 执行一下, run方法
        schedule.every(TEST_PROXIES_INTERVAL).hours.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    # ProxyTester.start()
    pt = ProxyTester()
    pt.run()


