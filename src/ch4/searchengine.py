#
#
#
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import re


class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
    
    
    def getentryid(self, table, field, value, createnew=True):
        return None
    
    
    
    def addtoindex(self, url, soup):
        if self.isindexed(url): return

        print "Indexing %s"%url
        
        text = self.gettextonly(soup)
        words = self.separatewords(text)        
        
    
    #
    #
    #    
    def gettextonly(self, soup):
        v = soup.string        
        if v == None:
            contents = soup.contents
            resulttext = ''
            for c in contents:                
                resulttext += self.gettextonly(c) + "\n"
            
            return resulttext          
        else:
            return v.strip()
        
    
    
    #
    # Not a very trivial operation in reality and a lot of research is being done into thi
    # For sake of this example we will be separating over anything that is not a word or number  
    #
    def separatewords(self, text):
        splitter = re.compile("\\W*")        
        return [w.lower() for w in splitter.split(text) if w != '']
    
    
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
        
                            
                            
                    
                
                

    def createindextable(self, drop_existing = False):
        if drop_existing:
            self.con.execute('drop table if exists urllist')
            self.con.execute('drop table if exists wordlist')
            self.con.execute('drop table if exists wordlocation')
            self.con.execute('drop table if exists link')
            self.con.execute('drop table if exists linkwords')
            
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid integer)')
        self.con.execute('create table linkwords(wordid, linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        print "Schema Successfully (Re)created"
        
    
    

crawler = crawler("searchindex.db")
#crawler.createindextable(True)
#crawler.createindextable()
crawler.crawl(["https://en.wikipedia.org/wiki/Programming_language"])
    