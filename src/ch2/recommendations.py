'''
Created on Aug 29, 2015

@author: Amol
'''
from math import sqrt
from heapq import nlargest
from itertools import groupby

# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5, 'You, Me and Dupree':1.0, 'Superman Returns':4.0}}


# Find similarity score of person1 and person2 using euclidean distance.
# 0 <= sim_distance <= 1
# 0 indicates no correlation
# 1 indicates strong correlation and likings are identical
#
# Note that the results are different than the one in book as we 
# return 1 / (1 + sqrt(sum_of_squares)) and not return 1 / (1 + sum_of_squares)  
def sim_distance(prefs, person1, person2):
    # TODO: Add validation for valid person
    person1_prefs = prefs[person1]
    person2_prefs = prefs[person2]    

    # Find if there are common items in  preferences else the score would be 0
    if not any(item in person1_prefs for item in person2_prefs):
        return 0
    
    sum_of_squares = sum([ pow(person2_prefs[item] - person1_prefs[item], 2) for item in person2_prefs if item in person1_prefs])
    
    # Note that the square root is not given in the book and the Euclidean distance has to be sqrt
    # TODO: Check if this is correct
    # return 1 / (1 + sum_of_squares) 
    return 1 / (1 + sqrt(sum_of_squares))

# Find the similarity scores of person1 and person2 using Pearson distance
def sim_pearson(prefs, person1, person2):        
    # TODO: Add validation for valid person
    p1_p = prefs[person1]
    p2_p = prefs[person2]
    
    # Find if there are common item preferences else the score would be 0
    common_prefs = [pref for pref in p1_p if pref in p2_p]
    num_common_prefs = len(common_prefs)
    
    if num_common_prefs != 0:
        pref_and_square_p1 = [(p1_p[pref], pow(p1_p[pref], 2)) for pref in common_prefs] 
        pref_and_square_p2 = [(p2_p[pref], pow(p2_p[pref], 2)) for pref in common_prefs]
        sum_square_p1 = reduce(lambda x, y : (x[0] + y[0], x[1] + y[1]), pref_and_square_p1)
        sum_square_p2 = reduce(lambda x, y : (x[0] + y[0], x[1] + y[1]), pref_and_square_p2)
        prod_prefs = sum([p1_p[pref] * p2_p[pref] for pref in common_prefs])     
        # TODO write the complete mathematical formula here, give reference to derivation
        # Denominator is sqrt(( sum_of_squares of p1- square_of_sum of p1 / n)*( sum_of_squares of p2- square_of_sum of p2 / n))
        den = sqrt((sum_square_p1[1] - pow(sum_square_p1[0], 2) / num_common_prefs) * (sum_square_p2[1] - pow(sum_square_p2[0], 2) / num_common_prefs))
        
        # Avoid div by 0
        if den == 0:
            return 0
        else:
            # Sum of products - (product of sum / n)
            return  (prod_prefs - (sum_square_p1[0] * sum_square_p2[0] / num_common_prefs)) / den
    else:
        return 0
    

# Returns the best match for the person from the prefs dictionary
def topMatches(prefs, person, n=5, similarity=sim_pearson):    
    # Using heapq for top n. For large n close to the size of the list this isnt optimal and sort works better
    # Not adding this unnecessary optimization though
    return nlargest(n, [(similarity(prefs, person, other), other) for other in prefs if other != person])

#
def getRecommendations(prefs, person, similarity=sim_pearson):    
    
    # Step 1: Get a similarity score with others, the result is a list of 2 tuple, (similarity score, name of the person)
    similarity_with_others = filter(lambda (score, _): score > 0, topMatches(prefs, person, len(prefs) - 1, similarity))      
    p_prefs = prefs[person]    

    # Step 2: Find items present in all other peoples maps which are either not present in the person's map or
    # if present has a score of 0, since there will be duplicates, have a set
    items_not_rated_by_person = set(
                                     [pref for other in prefs if other != person 
                                        for pref in prefs[other] if pref not in p_prefs or p_prefs[pref] == 0]
                                    )
    
    # Step 3: Compute the weighted scores, the result is a list of three tuple
    # (item_name, similarity_score_in_step_1, similarity_score_in_step1 * rating_by_the_person_for_the_item)
    weighted_scores = [(pref, similarity_score, similarity_score * prefs[other_person][pref]) 
           for similarity_score, other_person in similarity_with_others 
           for pref in prefs[other_person] if pref in items_not_rated_by_person and prefs[other_person][pref] != 0 ]
    
    # Step 4. Group by the list in step 3 by the item_name, 
    # the grouped by result is a key and an iterable of the values for that key
    # We now run a reduce operation to emit the following List
    # (item_name, sum_of_the_similarityscores, sum_of_the_weighted_similarity_scores_from_step3
    # IMP: groupby requires the list of 3 tuples to be sorted, else, the groupby will yield unexpected results) 
    reduced_weighted_scores = [(reduce(
                                       lambda (first_item, first_sim_score, first_sim_weighted_rating), (_, second_sim_score, second_sim_weighted_rating) : 
                                                (first_item, first_sim_score + second_sim_score,
                                                 first_sim_weighted_rating + second_sim_weighted_rating),
                                                 grouped_values))
                                for _, grouped_values in groupby(sorted(weighted_scores), lambda (item, x, y) : item)]
    
    # Step 5: Return the sorted list of recommendations by the score, 
    # score is the sum_of_weighted_similarity_score/sum_of_similarity_score
    return sorted(map( lambda (item_name, sum_similarity, sum_sim_weighted_items) : (sum_sim_weighted_items / sum_similarity, item_name), reduced_weighted_scores), reverse=True)


#Inverts the preferences and creates a map with inner key as the outer key and outer key as the inner key 
def transformPrefs(prefs):
    flattened_map = [(inner_key, outer_key, prefs[outer_key][inner_key]) 
                     for outer_key in prefs for inner_key in prefs[outer_key]]
    return dict(
                [(key,  dict( (inner_key, value) for _, inner_key, value in inner_map_values) )
                    for key, inner_map_values in groupby(sorted(flattened_map), lambda (key, v1, v2): key)]
            )
    

def loadMovieLens(path="../../dataset/ml-100k"):    
    movies = dict(map(lambda split: (split[0], split[1]), [line.split("|")[0:2] for line in open(path + "/u.item")]))
    movies_grouped_by_users = groupby(
                                      sorted(
                                             # Emit (user, (movie_id, rating) )
                                             map(lambda (x): (x[0], (x[1], x[2])), 
                                                 [line.split("\t") for line in open(path + "/u.data")]
                                            )
                                        ),
                                lambda (key, _) : key
                            )
    
    
    return dict( 
               (user, dict(
                           map(lambda (_, (movie_id, rating )): (movies[movie_id], float(rating)), 
                               grouped_values
                            )
                           )
                ) 
               for user, grouped_values in movies_grouped_by_users
    )
    
print "Similarity by Euclidean distance between Lisa Rose and Gene Seymour is ", sim_distance(critics, "Lisa Rose", "Gene Seymour")
print "Similarity by Euclidean distance between Lisa Rose and Jack Matthews is ", sim_distance(critics, "Lisa Rose", "Jack Matthews")
print "Similarity by Pearson distance between Lisa Rose and Gene Seymour is ", sim_pearson(critics, "Lisa Rose", "Gene Seymour")
print "Similarity by Pearson distance between Lisa Rose and Jack Matthews is ", sim_pearson(critics, "Lisa Rose", "Jack Matthews")
print "Top 3 matches using pearson distance for Toby are ", topMatches(critics, 'Toby', n=3)
print "Top Recommendations for Toby are by pearson distance ", getRecommendations(critics, "Toby")
print "Top Recommendations for Toby are by euclidean distance ", getRecommendations(critics, "Toby", similarity=sim_distance)
print "Top matches for Superman Returns are ", topMatches(transformPrefs(critics), "Superman Returns")
#Euclidean distance doesn't return negative values 
print "Top matches for Superman Returns are ", topMatches(transformPrefs(critics), "Superman Returns", similarity=sim_distance)
print "Recommendations for Just My Luck are ", getRecommendations(transformPrefs(critics), "Just My Luck")
print "\n\nRunning Tests on Movielens database"
prefs = loadMovieLens()
#print prefs['87']
#print topMatches(prefs, '87')
print "Top recommendations for user 87 are\n", getRecommendations(prefs, '87')[0:30]