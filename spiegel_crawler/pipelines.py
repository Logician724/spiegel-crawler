# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo


class ArticleValidationPipeline:
    def process_item(self, item, _):
        adapter = ItemAdapter(item)
        if not (isinstance(adapter.get('id'), str) and len(adapter.get('id').strip()) > 0):
            raise DropItem('invalid id: ' + str(adapter.get('id')))
        if not (isinstance(adapter.get('title'), str) and len(adapter.get('title').strip()) > 0):
            raise DropItem('invalid title: ' + str(adapter.get('title')))
        # Some articles don't have an abstract or a subtitle, hence
        # aggressively validating for having these attributes should
        # not be necessary
        if not(isinstance(adapter.get('subtitle'), str) or adapter.get('subtitle') is None):
            raise DropItem('invalid subtitle: ' + str(adapter.get('subtitle')))
        if not(isinstance(adapter.get('abstract'), str) or adapter.get('abstract') is None):
            raise DropItem('invalid abstract: ' + str(adapter.get('abstract')))
        return item


class ArticleFormatPipeline:
    def process_item(self, item, _):
        adapter = ItemAdapter(item)
        adapter['id'] = adapter.get('id').strip().strip('"')
        adapter['title'] = adapter.get('title').strip().strip('"')
        if isinstance(adapter['subtitle'], str):
            adapter['subtitle'] = adapter.get('subtitle').strip().strip('"')
        if isinstance(adapter['abstract'], str):
            adapter['abstract'] = adapter.get('abstract').strip().strip('"')
        return adapter.item


class ArticleMongoDBPipeline:

    def __init__(self, mongo_uri, mongo_db, mongo_col):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_col = mongo_col

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_col=crawler.settings.get('MONGO_COL'),
        )

    def open_spider(self, _):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.col = self.db[self.mongo_col]
        self.col.create_index('id', unique=True)

    def close_spider(self, _):

        self.client.close()

    def process_item(self, item, _):
        if self.col.find_one({"id": item.get('id')}) is not None:
            self.col.update_one({'id': item.get('id')}, {'$set': {
                'title': item.get('title'),
                'subtitle': item.get('subtitle'),
                'abstract': item.get('abstract'),
                'updated_at': item.get('downloaded_at')
            }})
        else:
            self.col.insert_one(dict(item))
        return item
