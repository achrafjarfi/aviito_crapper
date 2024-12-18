import json
from typing import Union, Any
from urllib.parse import unquote


from scrapy.http import Response

from project_avito_scrapping.helpers import get_last_url,save
from project_avito_scrapping.scrapping.propertyItems import PropertyItem

import scrapy
import logging





def total_surface(ad_info: dict, key: str, value: Union[str,int]) -> int:
    for param in ad_info.get("params", {}).get(key, []):
        try:
            if param.get("key") == value:
                return int(param.get("value", ""))
        except KeyError:
            pass
    return 0


class PropertySpider(scrapy.Spider):
    name = 'propertySpider'
    #allowed_domains = ['www.avito.ma']
    start_urls = ['https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre']
    page_number = 2

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOADER_DELAY": 1
    }

    def __init__(self):
        self.parsed = unquote(get_last_url())
        self.is_last_ad_url_saved = False

    def parse(self, response):


        properties = response.css("a.sc-1jge648-0")

        if not self.is_last_ad_url_saved:
            save(properties[0].css("a").attrib["href"])
            self.is_last_ad_url_saved = True

        for property in properties:
            url = property.css("a").attrib["href"]
            url = unquote(url)
            if url == self.parsed:
                return

            yield response.follow(url, callback=self.parse_property_page)

        next = 'https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre?o=' + str(PropertySpider.page_number)

        if PropertySpider.page_number<=500:
            PropertySpider.page_number += 1
            yield response.follow(next, callback=self.parse)

        #if href := self.get_next_page_url(response):
        #    yield response.follow(href, callback=self.parse, dont_filter=True)

    def parse_property_page(self, response: Response):
        """
        Parse a property page and extract details.

        :param response: The response object for a property page.
        :type response: scrapy.http.Response
        :return: Yields property details.
        :rtype: Scrapy item
        """
        json_data = response.css("#__NEXT_DATA__::text").get()
        try:
            data = json.loads(json_data)

            ad_info = data["props"]["pageProps"]["componentProps"]["adInfo"]["ad"]
            property_item = PropertyItem()

            property_item["url"] = unquote(response.url)
            property_item["ad_title"] = ad_info.get("subject", "N/A")
            property_item["description"] = ad_info.get("description", "N/A")
            property_item["price"] = ad_info.get("price", {}).get("value", None)
            property_item["address"] = ad_info.get("location", {}).get("address", "N/A")
            property_item["city"] = ad_info.get("location", {}).get("city", {}).get("name", "N/A")
            property_item["category"] = ad_info.get("category", {}).get("name", "N/A")
            property_item["is_new_building"] = ad_info.get("isImmoneuf", False)
            property_item["phone"] = ad_info.get("phone", None)
            property_item["published_date"] = ad_info.get("listTime", None)
            property_item["seller_name"] = ad_info.get("seller", {}).get("name", "N/A")
            property_item["habitable_size"] = total_surface(ad_info, "primary", "habitable_size")
            property_item["total_surface"] = total_surface(ad_info, "secondary", "size")

            yield property_item
        except (ValueError, KeyError) :
            self.logger.error(f"Failed to parse data for URL: {response.url}")



    def get_next_page_url(self, response: Response) -> Union[str, None]:
        next_page = response.css(
            'a.sc-1cf7u6r-0.gRyZxr.sc-2y0ggl-1.yRCEb:not(.activePage)::attr(href)'
        ).get()
        return next_page



