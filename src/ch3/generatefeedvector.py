'''
Created on Sep 4, 2015

@author: Amol
'''
from feedparser import parse
import re
from itertools import groupby


#Remove HTML and get the remaining words
def getwords(html):
    txt = re.compile(r'<[^>]+>').sub('', html)
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    return [word.lower() for word in words if word != ''] 


#Short implementation to count words, however, the performance is not something I have benchmarked
#As this includesm sort, groupby and len(list(group))
def getwordcounts(url):
    d = parse(url)
    print "Getting feed from URL %s" % url
    feed_map = d['feed']
    if 'title' in feed_map:    
        res = [getwords(e['title'] + ' ' + e['summary' if 'summary' in e else 'description']) for e in d['entries']]
        word_count_map = dict((key, len(list(group))) for key, group in groupby(sorted([word for l in res for word in l])))    
        return feed_map['title'], word_count_map
    else:
        print "Warn: Unable to access data from feed %s" % url
        #Special handling for some URLs not found or Forbidden
        return 'NA', {}
    
      
    
# TODO: Clean implementation of the following code
# TODO: Experiment using Stopword filters 
apcount = {}
wordcount = {}
feedlist = 0
for feedurl in file('feedlist.txt'):
    title, wc = getwordcounts(feedurl)
    if title != 'NA' and len(wc) > 0: 
        feedlist += 1
        wordcount[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 1:
                apcount[word] += 1

print "Retrieved and parsed all words from the List of Blogs"

wordlist = []
for w,bc in apcount.items():
    frac = float(bc) / float(feedlist)
    if frac > 0.1 and frac < 0.5: wordlist.append(w)

print "Writing to blogdata.txt"    
out = file('blogdata.txt', 'w')
out.write('Blog')
for word in wordlist: out.write('\t%s'% word)
out.write('\n')
for blog, wc in wordcount.items():
    out.write(blog)
    for word in wordlist:
        word_count = wc[word] if word in wc else 0
        out.write("\t%d" % word_count)
    out.write("\n")
out.close()
print "Successfully written to blogdata.txt"

#Note that the output generated will not match the one given by the author. Some of the URLs dont even work now