# 在配置文件: settings.py 中 定义MAX_SCORE = 50, 表示代理IP的默认最高分数
MAX_SCORE = 50

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