from bs4 import BeautifulSoup
import json
import time
import os
import random
import re

class NjuskaloQueryCrawler():
    #The blacklisted links which should be skipped
    blacklistedLinks = {'/luksuzne-nekretnine'}
    #Gets a list of all possible entities on the page. An entity is an entry to the njuskalo website.
    def _getPossibleEntities(self, soup):
        regularEntityList = soup.find('div', class_='EntityList--ListItemRegularAd')
        vauVauEntityList = soup.find('div', class_='EntityList--VauVau')
        entities = []
        if (regularEntityList != None):
            entities = regularEntityList.find_all('li', class_='EntityList-item')
        if (vauVauEntityList != None):
            entities.extend(vauVauEntityList.find_all('li', class_='EntityList-item'))
        return entities
    

    def _crawlEntity(self, parsed_items, entity):
        if (entity.find('article', class_='entity-body') == None):
            return
        
        #Prep of entity description for easier parsing
        description_str_raw = entity.find('div', class_='entity-description-main').text
        living_area_str = re.search(r'(\d+(\.\d+)?)\s* m2', description_str_raw)
        location_str = re.search(r'Lokacija:\s*(.*)', description_str_raw)

        name_data = entity.find('a')

        name_str = name_data.text
        link_str = name_data['href']
        id_str = re.search(r'(?P<prefix>oglas-)(?P<id_num>\d+)', link_str)
        # location_str = entity.find('div', class_='entity-description-main').text
        published_str = entity.find('time').text
        price_str = entity.find('strong', class_='price--hrk').text
        price_value = re.match(r'(?P<price>\d+)', price_str.strip().replace('.',''))

        # Check if price_int is not a number and change to usable value
        if price_value: 
            price_value = float(price_value.group('price'))
        else:
            price_value = 0.0

        print("Scraped " + name_str)

        parsed_items.append({
                            'id': id_str.group('id_num'),
                            'name' : name_str.strip(),
                            'location' : location_str.group(1),
                            'Living Area': living_area_str.group(0),
                            'price' : price_value,
                            'link' : link_str,
                            'published' : published_str,
                            'detailCheck' : False  # flag to check if deepScan was done 
                    })
    #Write a category into a file on disk
    def _crawlCategoryLink(self, category_href, page, out_folder, page_limit):
        currentPage = 1
        nextPageCustomStart = 'https://www.njuskalo.hr' + category_href + '?page='
        nextPageCustom = nextPageCustomStart + str(currentPage)
        page.goto(nextPageCustom)

        parsed_items_from_category = []
        charsToRemoveFromFilename='/?'
        # Replace special characters with "-" and remove leading "-"
        sanitized_filename = re.sub(f'[{re.escape(charsToRemoveFromFilename)}]', '-', category_href)
        sanitized_filename = re.sub('^-', '', sanitized_filename)  # Remove leading "-"
        
        while (True):
            html_from_page = page.content()
            soup = BeautifulSoup(html_from_page, 'html.parser')
            entities = self._getPossibleEntities(soup)

            # Break if no entities found (end of listings)
            if not entities:
                print(f'No more listings found on page {currentPage}')
                break

            file = open(out_folder + sanitized_filename + '.json', 'w', encoding='utf-8')
                
            for entity in entities:
                self._crawlEntity(parsed_items_from_category, entity)

            parsed_items_string_json = json.dumps(parsed_items_from_category, ensure_ascii=False, indent=2)
            file.write(parsed_items_string_json)

            print('Parsed page: '+ str(currentPage))

            currentPage = currentPage + 1
            nextPageLink = nextPageCustomStart + str(currentPage)
            shouldConsiderPageLimit = page_limit != None
            if ((nextPageLink == None) or (shouldConsiderPageLimit and (page_limit == (currentPage - 1)))):
                file.close()
                break
            else:
                #sleep to give it a bit of human behavior
                time.sleep(random.uniform(0.05, 0.25))

                page.goto(nextPageLink)

    #The crawling mechanism for user picked categories:
    def crawlSelectedCategory(self, page, options):
        page.goto('https://www.njuskalo.hr')

        time.sleep(3)

        self._crawlCategoryLink(options.categoryHref, page, options.outFolder, options.pageLimit)

    #The crawling mechanism
    def crawlSelectedTab(self, page, options):
        # Navigate to the URL.
        page.goto(options.tab)

        time.sleep(3)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        categories = soup.find_all('li', class_='Category')

        categories.extend(soup.find_all('div', class_='Category'))

        links_to_crawl = []
        for category in categories:
            category_links = category.find_all('a')
            links_to_crawl.extend(category_links)

        for link in links_to_crawl:
            category_href = link['href']
            if (category_href in self.blacklistedLinks):
                print('Skipping: ' + category_href +'. Blacklisted.')
                continue
            print(category_href)

            self._crawlCategoryLink(category_href, page, options.outFolder, options.pageLimit)

    #If there is no page after this, returns None
    def _getNextPageLink(self, soup):
        try:
            pagination_html = soup.find('ul', class_='Pagination-items')
            # Using a lambda allows matching any span that contains '»'
            nextButtonSpan = pagination_html.find('span', text=lambda t: t and '»' in t)
            if nextButtonSpan is None:
                return None
            else:
                try:
                    return nextButtonSpan.parent['data-href']
                except:
                    return nextButtonSpan.parent['href']
        except:
            return None
        
