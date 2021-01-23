# -*- coding: utf-8 -*-
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |r|e|d|a|n|d|g|r|e|e|n|.|c|o|.|u|k|
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 
import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import replace_escape_chars

class Sitemap(scrapy.Item):
    sub_cat_code = scrapy.Field()
    cat_name = scrapy.Field()
    sub_cat_name = scrapy.Field()

class ProductList(scrapy.Item):
    code = scrapy.Field()
    sub_cat_name = scrapy.Field()
    sub_cat_code = scrapy.Field()
    img_small = scrapy.Field()
    wsp_inc_vat = scrapy.Field()
    rrp = scrapy.Field()
    por = scrapy.Field()

class ProductDetail(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field(
        input_processor=MapCompose(replace_escape_chars),
        output_processor=Join(),
    )
    img_big = scrapy.Field()
    info = scrapy.Field(
        input_processor=MapCompose(replace_escape_chars),
        output_processor=Join(),
    )

class Barcode(scrapy.Item):
    barcode = scrapy.Field()
    code = scrapy.Field()
    sub_cat_code = scrapy.Field()