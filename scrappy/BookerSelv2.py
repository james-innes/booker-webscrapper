# -*- coding: utf-8 -*-
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|r|e|d|a|n|d|g|r|e|e|n|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# ! Firefox has been used for webdriver #

import os
import json
import time

from selenium import webdriver

from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request
from scrapy.http import FormRequest
from scrapy.settings import Settings
from scrapy import Selector
from scrapy.loader import ItemLoader
from items import BookerMbItem

from dotenv import load_dotenv
load_dotenv()

with open ('sitemap.json') as j:
    bookerdict = json.load(j)
  
#  work in progresss -----------------------------
def flatten_json(jsondict):
    d = {}
    mylist = bookerdict['categories']
    for names in mylist:
        #print (names['name'])
        dictnames = (names['subCategories'])
        #print(dictnames)
        for i in dictnames:
            for k,v in i.items():
                print (v)
                
print(flatten_json(bookerdict))
print("...Categories have been processed...")
time.sleep(2)
#  ----------------------------------------------

	
class BookerProductList(Spider):

    name = "booker_mb"
    custom_settings = {"FEEDS": {"booker1.csv":{"format":"csv"}}}
    allowed_domains = ["booker.co.uk"]
    start_urls = ['https://www.booker.co.uk/home.aspx']
    
    try:
        os.remove("booker1.csv")
    except OSError:
        pass
    
    def __init__(self):
    
        self.driver = webdriver.Firefox()
        
        self.driver.get('https://www.booker.co.uk/home.aspx')
        self.driver.find_element_by_id ('OutsideHomePageControl_CustomerNumber').send_keys(os.getenv("BOOKER_ACCOUNT"))
        self.driver.find_element_by_id('OutsideHomePageControl_cmdCustomerNumber').click()

        time.sleep(2)
             
        self.driver.find_element_by_id ('LoginControl_EmailSingle').send_keys(os.getenv('BOOKER_EMAIL'))
        self.driver.find_element_by_id ('LoginControl_PasswordSingle').send_keys(os.getenv('BOOKER_PASSWORD'))
        self.driver.find_element_by_id('LoginControl_EnterEmailPasswordSubmit').click()
        
        self.cookie = self.driver.get_cookie("ASP.NET_SessionId")
        self.parse(response=self.driver.page_source)
        self.driver.quit()
        
        # From here onwards Selenium hands back to Scrapy
        
    def parse(self, response):

        print('### Logged IN ###')
        
        products="https://www.booker.co.uk/catalog/products.aspx"
        next_url = products
        
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': f"ASP.NET_SessionId={self.cookie['value']}",
            'Host': 'www.booker.co.uk',
            'Referer': 'https://www.booker.co.uk/catalog/mybooker.aspx',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
            }
                
        request = FormRequest(url=next_url, headers=headers ,callback=self.parse2)
        yield request      
             
             
    def parse2(self, response):
    
        print("\n## Now on Products Page of 24 thumbnails menu ##")
        
        print("\n## Now we will go and get all items, eg: BEER ##")
        
        # Trying one category here, will eventually read all 24 from JSON/sitemap
        
        
        BEER = 'https://www.booker.co.uk/catalog/products.aspx?categoryName=Default%20Catalog&keywords=beer&view=UnGrouped'
        
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '2660',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f"ASP.NET_SessionId={self.cookie['value']}",
            'Host': 'www.booker.co.uk',
            'Origin': 'https://www.booker.co.uk',
            'Referer': 'https://www.booker.co.uk/catalog/products.aspx',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'  
            }
        
        # Go from Main listing of 24 thumbnails to a specific Category ( approx 24 categories to visit )   
        request = Request(url=BEER,callback=self.parse_product)
        yield request     
        

    def parse_product(self, response):
        
        print("\n## Now Parsing individual products ##")
        for pr in response.xpath('.//*[@class="pr"]'):
            l = ItemLoader(item=BookerMbItem(), selector=pr, response=response)
            l.add_xpath('BPLIC', ".//td[@class='packm']/div/text()")
            l.add_xpath('alt', ".//img/@alt")
            l.add_xpath('pack', ".//div[@class='pibox']/descendant::*/text()")
            l.add_xpath('promotionText', ".//*[@class='promotionText']/descendant::*/text()")
            l.add_xpath('price', ".//li[@class='wsp']/text()")
            yield l.load_item()
            
        next_page_url =  response.xpath('//a[text()="Next >>"]//@href').get()
        absolute_next_page_url = response.urljoin(next_page_url)
        if next_page_url is not None:
            yield Request(absolute_next_page_url, callback=self.parse_product)
            
               
# Main Driver 
if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(BookerProductList)
	process.start()
