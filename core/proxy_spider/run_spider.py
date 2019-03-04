"""
8.5 实现运行爬虫模块
目标: 根据配置文件信息, 加载爬虫, 抓取代理IP, 进行校验, 如果可用, 写入到数据库中
思路:

1. 在run_spider.py中, 创建RunSpider类
2. 提供一个运行爬虫的run方法, 作为运行爬虫的入口, 实现核心的处理逻辑
    2.1 根据配置文件信息, 获取爬虫对象列表.
    2.2 遍历爬虫对象列表, 获取爬虫对象, 遍历爬虫对象的get_proxies方法, 获取代理IP
    2.3 检测代理IP(代理IP检测模块)
    2.4 如果可用,写入数据库(数据库模块)
    2.5 处理异常, 防止一个爬虫内部出错了, 影响其他的爬虫.
3. 使用异步来执行每一个爬虫任务, 以提高抓取代理IP效率
    3.1 在init方法中创建协程池对象
    3.2 把处理一个代理爬虫的代码抽到一个方法
    3.3 使用异步执行这个方法
    3.4 调用协程的join方法, 让当前线程等待 协程 任务的完成.
4. 使用schedule模块, 实现每隔一定的时间, 执行一次爬取任务
    4.1 定义一个start的类方法
    4.2 创建当前类的对象, 调用run方法
    4.3 使用schedule模块, 每隔一定的时间, 执行当前对象的run方法
"""
# 打猴子补丁,这个一般都放在上面
import schedule
import time
from gevent import monkey
monkey.patch_all()

from gevent.pool import Pool

import importlib
from settings import PROXIES_SPIDERS, RUN_SPIDERS_INTERVAL
from core.proxy_validata.httpbin_validator import check_proxy
from core.db.mongo_pool import MongodbPool
from utils.log import logger


class RunSpider(object):
    def __init__(self):
        # 创建数据库对象方便后面存储
        self.mongod = MongodbPool()
        # 获取携程池对象
        self.gevent_pool = Pool()

    def get_spider_from_settings(self):
        """根据配置文件信息, 获取爬虫对象列表."""
        # 遍历配置文件中爬虫信息, 获取每个爬虫全类名
        for full_class_name in PROXIES_SPIDERS:
            # core.proxy_spider.proxy_spiders.Ip66Spider
            # 获取模块名 和 类名
            module_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            # 根据模块名, 导入模块
            module = importlib.import_module(module_name)
            # 根据类名, 从模块中, 获取类
            cls = getattr(module, class_name)
            # 创建爬虫对象
            spider = cls()
            # print(spider)
            yield spider  # (返回配置里面的爬虫对象Ip3366Spider,KaiSpider.....)

    def run(self):
        # 获取爬虫对象,通过配置获取实现插拔方便对爬虫更改
        spiders = self.get_spider_from_settings()
        for spider in spiders:
            # 通过携程异步处理增加效率
            self.gevent_pool.apply_async(self.__excute_eyery_spider, args=(spider,))
        # 3.4 调用协程的join方法, 让当前线程等待 协程 任务的完成.即携程池中的任务都完成了才走下面的程序
        self.gevent_pool.join()

    def __excute_eyery_spider(self, spider):
        try:
            # 遍历爬虫对象，调用对象的方法获取proxy对象集合
            proxies = spider.get_proxies()  # 获取到的是可迭代对象
            for proxy in proxies:
                # 检验proxy对象
                proxy = check_proxy(proxy)
                # 判断检测后的结果如果speed==-1代表不合格,合格就存入数据库
                if proxy.speed != -1:
                    # 检测合格存入数据库
                    self.mongod.insert_one(proxy)
        except Exception as ex:
            logger.exception(ex)

    @classmethod
    def start(cls):
        rs = RunSpider()
        rs.run()  # 先要运行一次之后才开始监测
        schedule.every(RUN_SPIDERS_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == '__main__':
    RunSpider.start()
