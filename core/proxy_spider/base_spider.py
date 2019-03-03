"""实现通用爬虫方便后面继承修改"""
from lxml import etree

import requests

from IPProxyPool.domain import Proxy
from IPProxyPool.utils.http import get_request_headers


class BaseSpider(object):
    # 需要传的参数:urls,group_xpath分组的xpath获取table里面的内容,detail_xpath分组的xpath用于获取ip,area,port
    urls = []
    group_xpath = ''
    detail_xpath = {} # 形式为{'ip':xx,'port':xx,'area':xx}
    def __init__(self, urls = [], group_xpath = '', detail_xpath = {}):
        if urls:
            self.urls = urls
        if group_xpath:
            self.group_xpath = group_xpath
        if detail_xpath:
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        # 发送请求获取响应数据
        response = requests.get(url, headers=get_request_headers())
        return response.content
    
    def get_first_from_list(self, list):
        # 如果列表长度大于０就取第一个，否则取空
        return list[0] if len(list) != 0 else ''
    
    def get_proxy_from_page(self, page):
        # 1 利用xpath提取组信息
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        # 2 遍历组信息获取ip,port,area
        for tr in trs:
            ip = self.get_first_from_list(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_list(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_list(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            # 使用yield返回提取到的数据
            yield proxy
        
        
    def get_proxies(self):
        # 便利urls列表
        for url in self.urls:
            # 发送请求获取响应数据
            page = self.get_page_from_url(url)
            # 解析页面数据获取ip,port,area,然后返回proxy对象
            proxy = self.get_proxy_from_page(page)
            yield from proxy  # yield from后面加上可迭代对象，他可以把可迭代对象里的每个元素一个一个的yield出来，对比yield来说代码更加简洁，结构更加清晰,如果不用from得到的是三个对象

if __name__ == '__main__':

    config = {
        'urls': ['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1, 4)],
        'group_xpath': '//*[@id="list"]/table/tbody/tr',
        'detail_xpath': {
            'ip':'./td[1]/text()',
            'port':'./td[2]/text()',
            'area':'./td[5]/text()'
        }
    }

    spider = BaseSpider(**config)
    for proxy in spider.get_proxies():
        print(proxy)
    
    