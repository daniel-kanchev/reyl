import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from reyl.items import Article


class ReylSpider(scrapy.Spider):
    name = 'reyl'
    start_urls = ['https://reyl.com/en/groupe/corporate-podcast.html']

    def parse(self, response):
        links = response.xpath('//td[@headers="view-title-table-column"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//span[@class="field field--name-title field--type-string field--label-hidden"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="field field--name-field-publication-date field--type-datetime field--label-hidden field__item"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="right-container"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
