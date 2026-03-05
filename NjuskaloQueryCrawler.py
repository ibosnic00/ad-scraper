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
        regularEntityList = soup.find(class_='EntityList--ListItemRegularAd')
        vauVauEntityList = soup.find(class_='EntityList--VauVau')
        regular_entities = []
        entities = []
        if (regularEntityList != None):
            regular_entities = regularEntityList.find_all('li', class_='EntityList-item')
            entities.extend(regular_entities)
        if (vauVauEntityList != None):
            entities.extend(vauVauEntityList.find_all('li', class_='EntityList-item'))
        return entities, len(regular_entities) > 0


    def _crawlEntity(self, parsed_items, entity):
        if (entity.find('article', class_='entity-body') == None):
            return

        #Prep of entity description for easier parsing
        description_div = entity.find('div', class_='entity-description-main')
        if description_div is None:
            return

        description_str_raw = description_div.text
        living_area_str = re.search(r'(\d+(\.\d+)?)\s*m2', description_str_raw)
        location_str = re.search(r'Lokacija:\s*(.*)', description_str_raw)

        name_data = entity.find('h3', class_='entity-title')
        if name_data is None:
            return
        name_link = name_data.find('a')
        if name_link is None:
            return

        name_str = name_link.text.strip()
        link_str = name_link['href']
        id_str = re.search(r'(?P<prefix>oglas-)(?P<id_num>\d+)', link_str)
        if not id_str:
            return

        time_el = entity.find('time')
        published_str = time_el.text if time_el else ""

        price_el = entity.find('strong', class_='price--hrk')
        if price_el:
            price_str = price_el.text.strip()
        else:
            price_str = "0"

        price_value = re.match(r'(?P<price>\d+)', price_str.replace('.',''))
        if price_value:
            price_value = float(price_value.group('price'))
        else:
            price_value = 0.0

        if living_area_str and location_str:
            parsed_items.append({
                                'id': id_str.group('id_num'),
                                'name': name_str,
                                'location': location_str.group(1),
                                'Living Area': living_area_str.group(0),
                                'price': price_value,
                                'link': link_str,
                                'published': published_str,
                                'detailCheck': False  # flag to check if deepScan was done
                        })
            print("Scraped " + name_str)

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

        previous_ids = set()
        while (True):
            html_from_page = page.content()
            soup = BeautifulSoup(html_from_page, 'html.parser')
            entities, has_regular = self._getPossibleEntities(soup)

            # Break if no regular listings found (VauVau ads repeat on every page)
            if not has_regular:
                print(f'No more listings found on page {currentPage}')
                break

            # Detect duplicate page (site serves last page again for out-of-range pages)
            current_ids = set()
            for entity in entities:
                link = entity.find('a')
                if link and link.get('href'):
                    id_match = re.search(r'oglas-(\d+)', link['href'])
                    if id_match:
                        current_ids.add(id_match.group(1))
            if current_ids and current_ids == previous_ids:
                print(f'Page {currentPage} is a repeat of previous page, stopping.')
                break
            previous_ids = current_ids

            for entity in entities:
                self._crawlEntity(parsed_items_from_category, entity)

            # Write results to file after each page
            file = open(out_folder + sanitized_filename + '.json', 'w', encoding='utf-8')
            parsed_items_string_json = json.dumps(parsed_items_from_category, ensure_ascii=False, indent=2)
            file.write(parsed_items_string_json)
            file.close()

            print('Parsed page: '+ str(currentPage))

            currentPage = currentPage + 1
            nextPageLink = nextPageCustomStart + str(currentPage)
            shouldConsiderPageLimit = page_limit != None
            if ((nextPageLink == None) or (shouldConsiderPageLimit and (page_limit == (currentPage - 1)))):
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
