# -*- coding: utf-8 -*-
import scrapy


class BinarytreeSpider(scrapy.Spider):
    name = 'binarytree'
    allowed_domains = ['www.youtube.com/results?search_query=binary+tree']
    start_urls = ['https://www.youtube.com/results?search_query=binary+tree//']

    def parse(self, response):
        #extracting content using css and xpath
        titles = response.xpath('//a[@id = "video-title"]/text()').get()
        lengths = response.xpath('//span[@class = "style-scope ytd-thumbnail-overlay-time-status-renderer"]/text()').get()
        views = response.xpath('//span[@class = "style-scope ytd-video-meta-block"]/text()').get()

        #Print out contents by row
        for item in zip(titles, lengths, views):
            #create dictionary to store scraped into
            scraped_info = {
                'title' : item[0],
                'lengths' : item[1],
                'views' : item[2]
            }

            #give out scraped info
            yield scraped_info
            
    
