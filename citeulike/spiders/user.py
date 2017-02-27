# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from collections import defaultdict

class UserSpider(scrapy.Spider):
    name = "user"
    start_urls = []

    max_level = 3
    user_ids = set()
    user_papers = defaultdict(set)

    def __init__(self):
        for line in open('data/user_root.txt'):
            self.start_urls.append('http://www.citeulike.org' + line.strip())
            break

    def get_page_count(self, paper_count):
        count_per_page = 50
        if paper_count <= 0: return 1
        return (paper_count - 1) / count_per_page + 1

    def parse(self, response):
        for request in self.parse_user(response):
            yield request

        paper_count = int(response.xpath('//title/text()').extract_first().split(' ')[-2])
        page_count = self.get_page_count(paper_count)
        for page in range(1, page_count):
            yield Request(url='%s/page/%d' % (response.url, page + 1),
                callback=self.parse_user)

    def parse_user(self, response):
        t = response.url.split('/')
        curr_user_id = t[-1] if t[-2] == 'user' else t[-3]
        for paper in response.xpath('//tr[contains(@class, "list")]/@data-article_id').extract():
            self.user_papers[curr_user_id].add(paper)

        user_ids = set()
        for url in response.xpath('//a[@class="pubitem "]/@href').extract():
            user_ids.add(url)
            self.user_ids.add(url)
        for url in response.xpath('//a[@class="othrusr pubitem"]/@href').extract():
            user_ids.add(url)
            self.user_ids.add(url)

        level = response.meta['level'] if 'level' in response.meta else 1
        if level + 1 <= self.max_level:
            for url in user_ids:
                yield Request(url='http://www.citeulike.org' + url,
                    meta={'level': level + 1},
                    callback=self.parse)

    def closed(self, reason):
        df = open('data/users.txt', 'w')
        for user_id in self.user_ids:
            df.write(user_id + '\n')
        df.close()

        df = open('data/user_papers.txt', 'w')
        for user_id in self.user_papers:
            for paper in self.user_papers[user_id]:
                df.write(user_id + '\t' + paper + '\n')
        df.close()


