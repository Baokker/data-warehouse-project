# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

import time
from scrapy.http import HtmlResponse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class FilminfospiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FilminfospiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self) -> None:
        option = webdriver.ChromeOptions()
        # option.add_argument('--headless')
        option.add_argument('blink-settings=imagesEnabled=false')  # 设置不加载图片
        self.driver = webdriver.Chrome(options=option)
        # 设置定时
        self.driver.set_page_load_timeout(5)
        self.driver.set_script_timeout(5) 

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        self.driver.get(request.url+"/?language=en_US")
        self.driver.refresh()

        # 检测机器人
        robot_sentence = "Sorry, we just need to make sure you're not a robot. For best results, please make sure your browser is accepting cookies."
        if robot_sentence in self.driver.page_source:
            from lxml import etree
            html = etree.HTML(self.driver.page_source)

            from amazoncaptcha import AmazonCaptcha
            link = html.xpath("/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img/@src")[0]
            captcha = AmazonCaptcha.fromlink(link)
            solution = captcha.solve()

            from selenium.webdriver.common.by import By
            input_element = self.driver.find_element(By.ID,"captchacharacters")
            input_element.send_keys(solution)

            button = self.driver.find_element(By.XPATH,"//button")
            button.click()
            time.sleep(3)

        source = self.driver.page_source
        response = HtmlResponse(url = self.driver.current_url, body = source, request = request, encoding = 'utf-8')
        return response

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
