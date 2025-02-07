from enum import Enum;

class CustomCityCrawlingOptions:
    #categoryHref example: 'split'
    #pageLimit - the limit on the pages that are crawled
    #outFolder - the directory where you want the data saved
    def __init__(self, categoryHref, outFolder, pageLimit = None):
        self.categoryHref = "/iznajmljivanje-stanova/" + categoryHref
        self.pageLimit = pageLimit
        self.outFolder = outFolder + "\\\\"