# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

from article_spider.items import JobBoleArticleItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        # post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        # for post_url in post_urls:
        #     # urljoin()用于拼接URL，但这里的post_url其实是完整的，所以直接url=post_url也可以
        #     yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first()
            post_url = post_node.css("::attr(href)").extract_first()
            # meta用于传递参数
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        # .next.page-numbers没有空格，表示并列的class属性
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        提取文章具体字段
        """
        article_item = JobBoleArticleItem()
        # 文章封面图
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # 文章标题
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # 获取时间并去除多余字符
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().strip()[:-2]
        # 点赞
        praise_nums = int(response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first())
        # 收藏，结合正则表达式
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").re_first('.*?(\d+).*')
        fav_nums = int(fav_nums) if fav_nums else 0
        # 评论
        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").re_first('.*?(\d+).*')
        comment_nums = int(comment_nums) if comment_nums else 0
        # 正文
        content = response.xpath("//div[@class='entry']").extract_first()
        # 标签
        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tags里有一个评论数，把它去掉
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        yield article_item

        # 通过css选择器提取字段
        # title = response.css(".entry-header h1::text").extract_first()
        # create_date = response.css("p.entry-meta-hide-on-mobile::text").extract_first().strip()[:-2]
        # praise_nums = int(response.css(".vote-post-up h10::text").extract_first())
        # fav_nums = response.css(".bookmark-btn::text").re_first('.*?(\d+).*')
        # fav_nums = int(fav_nums) if fav_nums else 0
        # comment_nums = response.css("a[href='#article-comment'] span::text").re_first('.*?(\d+).*')
        # comment_nums = int(comment_nums) if comment_nums else 0
        # content = response.css("div.entry").extract_first()
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
