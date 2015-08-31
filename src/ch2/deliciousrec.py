'''
Created on Aug 30, 2015

@author: Amol
'''
from pydelicious import get_tagposts, get_urlposts


#TODO: Use Pickle for later use and avoid this API call and get result reproducabilty
#Initilizes an empty user dict with user name as the key and an empty map as the value
def initializeUserDict(tag, count=5):
    #get_popular doesn't work any more. Getting by tag 
    #return [url_post['user'] for item in get_tagposts(tag=tag)[0:count] for url_post in get_urlposts(item['url'])]
    #from hashlib import md5    
    #print md5('http://usingtechnologybetter.com/chrome-extensions-for-teachers/').hexdigest()
        
    return dict(
                [(url_info['user'], {}) 
                    for item in get_tagposts(tag=tag)[0:count] 
                        for url_info in get_urlposts(item['url']) if url_info['user'] != '']
            )




print initializeUserDict('technology', count=10)