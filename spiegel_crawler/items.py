# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ArticleItem(Item):
    id = Field()
    title = Field()
    subtitle = Field()
    abstract = Field()
    downloaded_at = Field()