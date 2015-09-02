'''
Created on Aug 30, 2015

@author: Amol
'''
from pydelicious import get_tagposts, get_userposts, get_urlposts
from time import sleep
from os.path import exists
from pickle import load, dump
from itertools import groupby 
from recommendations import getRecommendations, topMatches
import random

#Note: This reco syste, doesn't work very well. For speed up, lookups are cached. In case a fresh lookup
#is needed, delete the .p files and then try running again. I personally havent had lock in find a positive correlation
#between two individuals  
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


def fillItems(user_dict, cache_dict = True):    
    items_cache_file = "items_cache.p"    
    if cache_dict and exists(items_cache_file):
        print "Reading the items from cache file", items_cache_file
        cache_file = open(items_cache_file, "rb")
        user_url_tuple = load(cache_file)
        cache_file.close()
    else:        
        user_url_tuple = sorted([(user, post["url"], ) for user in user_dict for post in get_userpost_details(user)])
        if cache_dict:
            print "Saving to cache file"
            cache_file = open(items_cache_file, "wb")
            dump(user_url_tuple, cache_file)
            cache_file.close()
     
    #Very Imperative
    grouped_by_values = groupby(user_url_tuple, lambda (user, _): user)
    distinct_url_sequence = map(lambda (_, url) : (url, 0), user_url_tuple)
    for user in user_dict:
        user_dict[user] = dict(distinct_url_sequence)    
    
    for user, grouped_values in grouped_by_values:
        for _, url in grouped_values:
            user_dict[user][url] = 1      

user_dict = initializeUserDict('technology', count=10)
fillItems(user_dict)


user = user_dict.keys()[random.randint(0, len(user_dict) - 1)]
print "Top matches for ", user, " are ", topMatches(user_dict, user)
print "Recommendations for user ", user, " are ", getRecommendations(user_dict, user) 