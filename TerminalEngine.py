from NjuskaloCrawler import NjuskaloCrawler
from CrawlingOptions import CustomCityCrawlingOptions
from enum import Enum

splash_message = """
****************************************************
*                                                  *
*           Welcome to Njuškalo Crawler!           *
*                                                  *
* This tool allows you to scrape and analyze data  *
* from the popular Croatian classifieds website    *
* Njuškalo. Whether you're looking for the best    *
* real estate deals, the latest tech gadgets, or   *
* just curious about market trends, this crawler   *
* has you covered.                                 *
*                                                  *
* Please ensure you have the necessary permissions *
* to scrape data and respect the website's         *
* terms of service.                                *
*                                                  *
* Happy Crawling!                                  *
*                                                  *
***************************************************


"""

class TerminalEngine:
    def _runCustomCity(self):
        print("Pick a city link to crawl: 'split', 'zagreb', etc...")
        print("This is basically everyhing after www.njuskalo.hr/iznajmljivanje-stanova/ in the link in chrome")

        category_href = input()

        page_num_option = 250        
        data_folder = "results"        
        
        print(f"Data folder: {data_folder}")
        print(f"Limit on the pages scraped: {page_num_option}")

        options = CustomCityCrawlingOptions(category_href, data_folder, int(page_num_option))
        crawler = NjuskaloCrawler()
        crawler.crawlCustomCity(options = options)

    def runCoreLoop(self):
        print(splash_message)
        while True:
            print("Running crawling of custom city on Njuskalo")            
            self._runCustomCity()

            print ("Crawling complete!")
        print('Hope you like this tool! Please leave a star on github if you did :)!')