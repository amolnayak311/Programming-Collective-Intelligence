'''
Created on Aug 30, 2015

@author: Amol
'''
from pydelicious import get_tagposts, get_userposts, get_urlposts
from time import sleep
from os.path import exists
from pickle import load, dump 


#Convenience method that wraps getting the user details and hand exceptions and retry
def get_userpost_details(user, num_retries = 3, sleep_time=10):
    for i in range(num_retries):
        try:
            posts = get_userposts(user)
            break
        except:
            print "Exception caught while retrying for user ", user, " retry number ", i
            sleep(sleep_time)
            
    return posts
         

#Uses Pickle to avoid frequent API calls and get result reproducabilty. To fetch the data delete the .p pickle filles
#Initilizes an empty user dict with user name as the key and an empty map as the value
def initializeUserDict(tag, count=5, cache_dict = True):
    #get_popular doesn't work any more. Getting by tag 
    #return [url_post['user'] for item in get_tagposts(tag=tag)[0:count] for url_post in get_urlposts(item['url'])]
    #from hashlib import md5    
    #print md5('http://usingtechnologybetter.com/chrome-extensions-for-teachers/').hexdigest()
    user_dict_cache_file = "user_dict.p"    
    if cache_dict and exists(user_dict_cache_file):
        print "Reading the user_dict from cache file", user_dict_cache_file
        cache_file = open(user_dict_cache_file, "rb")
        user_dict = load(cache_file)
        cache_file.close()
    else:
        user_dict = dict(
                [(url_info['user'], {}) 
                    for item in get_tagposts(tag=tag)[0:count] 
                        for url_info in get_urlposts(item['url']) if url_info['user'] != '']
            )
        if cache_dict:
            print "Writing the user_dict to cache file", user_dict_cache_file
            cache_file = open(user_dict_cache_file, "wb")
            dump(user_dict, cache_file)
            cache_file.close()
   
    return user_dict


def fillItems(user_dict):
    user_url_tuple = sorted([(user, post["url"], ) for user in user_dict for post in get_userpost_details(user)])
    print user_url_tuple
      

user_dict = initializeUserDict('technology', count=10)
print user_dict
fillItems(user_dict)