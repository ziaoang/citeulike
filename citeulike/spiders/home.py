# -*- coding: utf-8 -*-
import scrapy

class HomeSpider(scrapy.Spider):
    name = "home"
    start_urls = []
    user_ids = set()

    def __init__(self):
        for page in range(18):
            self.start_urls.append('http://www.citeulike.org/home/page/%d' % (page + 1))
        
    def parse(self, response):
        for url in response.xpath('//a[@class="pubitem "]/@href').extract():
            self.user_ids.add(url)
        for url in response.xpath('//a[@class="othrusr pubitem"]/@href').extract():
            self.user_ids.add(url)

    def closed(self, reason):
        df = open('data/user_root.txt', 'w')
        for user_id in self.user_ids:
            df.write(user_id + '\n')
        df.close()


