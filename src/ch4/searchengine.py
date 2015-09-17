#
#
#
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import re


ignorewords=frozenset(['the','of','to','and','a','in','is','it'])

class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
    
    
    #
    #
    #
    def getentryid(self, table, field, value, createnew=True):
        res = self.con.execute("select rowid from %s where %s = '%s'" % (table, field, value)).fetchone()
        if res == None:
            return self.con.execute("insert into %s (%s) values ('%s')" % (table, field, value)).lastrowid
        else:
            return res[0]
        
    
    
    
    def addtoindex(self, url, soup):
        if self.isindexed(url):
            print "%s already indexed, skipping" % url 
            return

        print "Indexing %s"%url
        
        text = self.gettextonly(soup)
        words = self.separatewords(text)
        
        #Create and get the id from the DB for this URL 
        urlid = self.getentryid('urllist', 'url', url)
        
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords: continue
            
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute('insert into wordlocation(urlid, wordid, location) \
            values (%d, %d, %d)' % (urlid, wordid, i))
    
    
            
        
    
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
    
    
    #
    #
    #
    def isindexed(self, url):
        val = self.con.execute("select rowid from urllist where url = '%s'" %url).fetchone()
        #If the page is indexed is it really crawled and words indexed?
        if val != None:
            wordcount = self.con.execute("select count(1) from urllist where url = '%s'" % url).fetchone()
            return False if wordcount[0] == 0 else True
        else:
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
                except Exception, err:
                    print "Exception while opening page %s"%page, err
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
        #TODO: Add logic to check if tables exist and accordingly create/drop first
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
        
    
class searcher:
    
    #
    #
    #
    def __init__(self, dbname):
        self.con=sqlite.connect(dbname)
        
    
    #
    #
    #
    def __del__(self):
        self.con.close()

    #
    # Gets the count of documents in which the given word is present
    #
    def get_doc_count_for_word(self, word):
        return self.con.execute("select count(*) from wordlist where word = '%s'" % word.lower()).fetchone()[0]
    #
    #
    #
    def getmatchrows(self, q):
        #Split the words by space
        words = q.split(' ')        
        doc_count = [self.get_doc_count_for_word(word) for word in words]
        non_zero_words = filter(lambda (_, count): count >0 , zip(words, doc_count))
        print non_zero_words
        #TODO
        
        



crawler = crawler("searchindex.db")
#crawler.createindextable(True)
#crawler.createindextable()
#crawler.crawl(["https://en.wikipedia.org/wiki/Programming_language"])
#crawler.crawl(["https://en.wikipedia.org/wiki/Functional_programming"])
searcher = searcher('searchindex.db')
searcher.getmatchrows("Programming in Scala and Python")