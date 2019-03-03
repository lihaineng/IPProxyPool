# 在配置文件: settings.py 中 定义MAX_SCORE = 50, 表示代理IP的默认最高分数
MAX_SCORE = 10

# 日志的配置信息
import logging
# 默认的配置
LOG_LEVEL = logging.DEBUG    # 默认等级
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
LOG_FILENAME = 'log.log'    # 默认日志文件名称

# 设置延迟时间
TEST_TIMEOUT = 10

# 设置mongoddb的ｕｒｌ
MONGO_URL = 'mongodb://127.0.0.1:27017'

# 爬虫模块配置
PROXIES_SPIDERS = [
    # 爬虫的全类名,路径: 模块.类名
    'core.proxy_spider.proxy_spider.Ip66Spider',
    'core.proxy_spider.proxy_spider.Ip3366Spider',
    'core.proxy_spider.proxy_spider.KaiSpider',
    'core.proxy_spider.proxy_spider.ProxylistplusSpider',
    'core.proxy_spider.proxy_spider.XiciSpider',
]

# 配置爬虫重新启动的时间间隔, 单位为小时
RUN_SPIDERS_INTERVAL = 2

# 配置检测代理IP的异步数量
TEST_PROXIES_ASYNC_COUNT = 10

# 配置检查代理IP的时间间隔, 单位是小时
TEST_PROXIES_INTERVAL = 2