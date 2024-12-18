import scrapy


class PropertyItem(scrapy.Item):
    url = scrapy.Field()
    ad_title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    category = scrapy.Field()
    is_new_building = scrapy.Field()
    phone = scrapy.Field()
    published_date = scrapy.Field()
    seller_name = scrapy.Field()
    habitable_size = scrapy.Field()
    total_surface = scrapy.Field()