#
#
#
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin


class crawler:
    def __init__(self, dbname):
        pass
    
    def __del__(self):
        pass
    
    def dbcommit(self):
        pass
    
    
    def getentryid(self, table, field, value, createnew=True):
        return None
    
    
    
    def addtoindex(self, url, soup):
        print "Indexing %s"%url
        
    
    def gettextonly(self, soup):
        return None
    
    
    def separatewords(self, text):
        return None
    
    
    def isindexed(self, url):
        return False
    
    
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass        
    
    
    #Breadth first search crawl
    def crawl(self, pages, depth = 2):
        for _ in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urlopen(page)
                except:
                    print "Exception while opening page %s"%page
                    continue
                
                soup = BeautifulSoup(c.read())
                self.addtoindex(page, soup)                
                links = soup('a')                
                for link in links:
                    link_attributes = dict(link.attrs)                    
                    if 'href' in link_attributes:                        
                        url = urljoin(page, link['href'])
                        #TODO: What is this check for
                        if url.find("'") != -1: continue
                        url = url.split("#")[0]     #Remove the # in the URL and keep the base URL only
                        #Index http/https only                        
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                       
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)
            
                
                self.dbcommit()        
            pages = newpages
        
                            
                            
                    
                
                
    
    def createindextable(self):
        pass
    
    

crawler = crawler("dummy")    
crawler.crawl(["https://en.wikipedia.org/wiki/Python_(programming_language)"])
    