import scrapy
from spiegel_crawler.items import ArticleItem
import re
import logging
import datetime
class SpiegelCrawler(scrapy.Spider):
    name = 'spiegel'
    start_urls = [
        'https://www.spiegel.de/international/'
    ]

    def parse(self, response):
        articles_selectors = response.xpath('//article')
        for curr_selector in articles_selectors:
            curr_article = ArticleItem(
                id = SpiegelCrawler.gen_id(curr_selector),
                title = curr_selector.xpath('.//header//a[@title]/@title').get(),
                subtitle = curr_selector.xpath(
                    './/header//a[@title]//span').css('.text-primary-base').xpath('./text()').get(),
                abstract = curr_selector.xpath(
                    '(.//section//a[@title]/span)[1]//text()').get(),
                downloaded_at = datetime.datetime.now()
            )
            yield curr_article
        next_page = re.search(
            "'(.*)'", response.xpath('//div[@data-area="pagination-bar"]').xpath('.//span[@title="Ältere Artikel"]/@onclick').get()).group().replace("'","")
        
        if next_page is not None:
            # The last page in spiegel international moves to a
            # different view. Crawler should stop there.
            if next_page.find('nachrichtenarchiv') == -1:
                logging.debug(next_page)
                yield response.follow(next_page, self.parse)

    @staticmethod
    def gen_id(article_selector):
        id = article_selector.xpath('@data-sara-article-id').get()
        # There seems to be a bug in spiegel where some articles have a mistyped id attribute
        if(id is None):
            id = article_selector.xpath('@ata-sara-article-id').get()
        return id