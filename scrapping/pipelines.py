# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from datetime import datetime



class ScrappingPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        date = adapter['published_date']
        adapter["published_date"] = self._to_datetime(date)

        return item
    def _to_datetime(self, date):
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

import pymongo
from pymongo.errors import PyMongoError
import sys

class SaveToMongoDBPipeline:
    """
    A pipeline for saving scraped property data to a MongoDB database.
    """

    def __init__(self):
        try:
            # Connect to MongoDB (assuming local MongoDB setup)
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.db = self.client["avito_trackr"]  # Create database if not exists
            self.collection = self.db["property"]  # Create collection if not exists
        except ConnectionError as err:
            sys.exit(f"MongoDB Error: {err}")

    def process_item(self, item, spider):
        """
        Process an PropertyItem by inserting it into the 'property' collection.

        :param item: The scraped property data.
        :type item: PropertyItem
        :param spider: The spider object.
        """
        try:
            # Insert the item as a document in the MongoDB collection
            self.collection.update_one(
                {"url": item["url"]},  # Unique identifier: 'url'
                {"$set": dict(item)},   # Update or insert the document
                upsert=True             # Create if not exists
            )
        except pymongo.errors.PyMongoError as err:
            print(f"MongoDB Error: {err}")

        return item

    def close_spider(self, spider):
        """
        Close the MongoDB connection when the spider is closed.

        :param spider: The spider object.
        """
        self.client.close()






