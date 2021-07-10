# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
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
        return item

class ArticleFormatPipeline:
    def process_item(self, item, _):
        adapter = ItemAdapter(item)
        adapter['id'] =  adapter.get('id').strip().strip('"')
        adapter['title'] = adapter.get('title').strip().strip('"')
        if isinstance(adapter['subtitle'], str):
            adapter['subtitle'] = adapter.get('subtitle').strip().strip('"')
        if isinstance(adapter['abstract'], str):
            adapter['abstract'] = adapter.get('abstract').strip().strip('"')
        return adapter.item
