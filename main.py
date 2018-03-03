"""
Created on 2018/3/3
@Author: Jeff Yang
"""
from scrapy.cmdline import execute
import sys
import os

# sys.path.append("D:\Program Files\PyCharm 2017.1.4\PycharmProjects\article_spider")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # __file__指当前文件路径,dirname()指所在文件夹路径
execute(["scrapy", "crawl", "jobbole"])
