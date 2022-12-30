import scrapy
import pandas as pd


class MoviesSpider(scrapy.Spider):
    name = "movies"

    def start_requests(self):
        # 开始 结束
        start = int(input("Start:"))
        end = int(input("End: "))
        # 获取电影ASIN（已提前提取）
        # movie_id = ['B009F2ZYNC'] # prime
        # movie_id = ['B003AI2VGA','B00006HAXW','B00004CQT3','B00004CQT4','B006JIUN2W','B0078V2LCY','B003ZG3GAM','B004BH1TN0','B0071AD95K','B000063W1R']
        p = pd.read_csv("../Data/productId.csv")
        movie_id = list(p.loc[start:end,'productId'])

        # 转成对应的URL
        # 不加代理 很快会被锁IP
        # 或者考虑在middleware使用selenium
        urls =["https://www.amazon.com/dp/" + i for i in movie_id]

        # https://scrapeops.io/
        # API_KEY = '9332f33f-4373-4ec5-846c-59604851ec0d'
        # urls = ['https://proxy.scrapeops.io/v1/?api_key=' + API_KEY + '&url=https://www.amazon.com/dp/' + i for i in movie_id]

        # 发送请求
        i = start
        for url in urls:
            print("第" + str(i) + "条请求")
            i += 1
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # 初始化yield返回数据
        attributes = {'ASIN':'','Title':'','Language':'','Release date':'','Date First Available':'','Run time':'','Producers':'','Directors':'','Writers':'','Actors':'','Media Format':'','Subtitles':'', 'Genres':''}
        
        # 确定ASIN值
        asin_begin_position = 26
        asin_length = 10
        attributes['ASIN'] = response.url[asin_begin_position:asin_begin_position + asin_length]
        
        # 判断类别
        product_type = response.xpath('//*[@id="nav-search-label-id"]/text()').get()

        # 如果都不是 直接return
        if product_type != 'Movies & TV' and product_type != 'Prime Video':
            return 

        # 写入文件 以备不时之需
        path = 'WebPages/'
        # path = '/Volumes/PortableSSD/WebPages'
        filename = f'{path}/{attributes["ASIN"]}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        # Movies & TV
        if product_type == 'Movies & TV':
            # 获取标题
            Title = response.xpath('//*[@id="productTitle"]/text()').extract_first().strip()
            attributes['Title'] = Title

            # 获取Product details
            result = response.xpath('//*[@id="detailBullets_feature_div"]/ul/li/span/span/text()').getall()
            result = [r.replace(':','').replace('\u200f','').replace('\u200e','').replace('\t', '').replace('\n', '').replace('\r', '').strip() for r in result]
            
            columns = result[0::2]
            value = result[1::2]

            for i in range(len(columns)):
                for key in attributes.keys():
                    if columns[i] in key:
                        attributes[key] = value[i]

        # Prime Video
        elif product_type == 'Prime Video':
            # 是否为电影
            if '"titleType":"movie"' not in response.xpath('//*[@id="a-page"]/div[2]/script[15]/text()').get():
                return

            # Title = response.xpath('//*[@id="a-page"]/div[2]/div[4]/div/div/div[2]/div[3]/div/h1/text()').get() # 原先代码有误
            Title = response.xpath('//*[@id="a-page"]/div[2]/div[4]/div/div/div[2]/div[2]/div/h1/text()').get()
            if Title == None:
                Title = response.xpath('//*[@id="a-page"]/div[2]/div[4]/div/div/div[2]/div[1]/div/h1/text()').get()
                
            attributes['Title'] = Title

            columns_1 = response.xpath('//*[@id="btf-product-details"]/div/dl/dt/span/text()').getall()
            value_1 = response.xpath('//*[@id="btf-product-details"]/div/dl/dd/*/text()').getall()

            for i in range(len(columns_1)):
                for key in attributes.keys():
                    if columns_1[i] in key:
                        attributes[key] = value_1[i]

            columns_2 = response.xpath('//*[@id="meta-info"]/div/dl/dt/span/text()').getall()
            for i in range(len(columns_2)):
                # 根据columns内容判断
                if columns_2[i] == 'Directors' or columns_2[i] == 'Genres':
                    attributes[columns_2[i]] = response.xpath('//*[@id="meta-info"]/div/dl[' + str(i + 1) + ']/dd/a/text()').get()
                elif columns_2[i] == 'Starring':
                    attributes['Actors'] = str(response.xpath('//*[@id="meta-info"]/div/dl[' + str(i + 1) + ']/dd/a/text()').getall())[1:-2].replace("'",'')
        
        yield attributes
        