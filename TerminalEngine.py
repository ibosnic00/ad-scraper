from NjuskaloCrawler import NjuskaloCrawler
from CrawlingOptions import CustomCategoryCrawlingOptions, TabCrawlingOptions
from NjuskaloTab import NjuskaloTab
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
    def _runWholeTab(self):
        print("Pick a tab to crawl: 1 = Marketplace, 2 = AutoMoto, Anything else = Nekretnine")
        choice = input()
        tab_option = None
        if (choice == '1'):
            tab_option = NjuskaloTab.Marketplace
        elif (choice == '2'):
            tab_option = NjuskaloTab.AutoMoto
        else:
            tab_option = NjuskaloTab.Nekretnine

        
        choice = 250
        print(f"Limit on the pages scraped: {choice}")
        page_num_option = choice
        
        data_folder = "results"

        options = TabCrawlingOptions(tab_option, data_folder, int(page_num_option))
        crawler = NjuskaloCrawler()
        crawler.crawlTab(options = options)
    def _runCustomCategory(self):
        print("Pick a category link to crawl: '/prodaja-kuca', '/prodaja-kuca/istra', etc...")
        print("This is basically everyhing after www.njuskalo.hr in the link in chrome")

        category_href = input()


        choice = 250
        print(f"Limit on the pages scraped: {choice}")

        page_num_option = choice
        
        data_folder = "results"

        options = CustomCategoryCrawlingOptions(category_href, data_folder, int(page_num_option))
        crawler = NjuskaloCrawler()
        crawler.crawlCustomCategory(options = options)

    def runCoreLoop(self):
        print(splash_message)
        while True:
            print("Running crawling of custom category on Njuskalo")            
            self._runCustomCategory()

            print ("Crawling complete!")
        print('Hope you like this tool! Please leave a star on github if you did :)!')