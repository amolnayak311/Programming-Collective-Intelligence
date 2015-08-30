# A dictionary of movie critics and their ratings of a small
# set of movies
from math import sqrt
from heapq import nlargest
from itertools import groupby
import operator

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
    person1_movies = prefs[person1]
    person2_movies = prefs[person2]    

    # Find if there are common movie preferences else the score would be 0
    if not any(movie in person1_movies for movie in person2_movies):
        return 0
    
    sum_of_squares = sum([ pow(person2_movies[movie] - person1_movies[movie], 2) for movie in person2_movies if movie in person1_movies])
    
    # Note that the square root is not given in the book and the Euclidean distance has to be sqrt
    # TODO: Check if this is correct
    #return 1 / (1 + sum_of_squares) 
    return 1 / (1 + sqrt(sum_of_squares))

# Find the similarity scores of person1 and person2 using Pearson distance
def sim_pearson(prefs, person1, person2):        
    # TODO: Add validation for valid person
    p1_m = prefs[person1]
    p2_m = prefs[person2]
    
    # Find if there are common movie preferences else the score would be 0
    common_movies = [movie for movie in p1_m if movie in p2_m]
    num_common_movies = len(common_movies)
    
      
    pref_and_square_p1 = [(p1_m[movie], pow(p1_m[movie], 2)) for movie in common_movies] 
    pref_and_square_p2 = [(p2_m[movie], pow(p2_m[movie], 2)) for movie in common_movies]
    sum_square_p1 = reduce(lambda x, y : (x[0] + y[0], x[1] + y[1]), pref_and_square_p1)
    sum_square_p2 = reduce(lambda x, y : (x[0] + y[0], x[1] + y[1]), pref_and_square_p2)
    prod_prefs = sum([p1_m[movie] * p2_m[movie] for movie in common_movies])
    
     
    # TODO write the complete mathematical formula here, give reference to derivation
    # Denominator is sqrt(( sum_of_squares of p1- square_of_sum of p1 / n)*( sum_of_squares of p2- square_of_sum of p2 / n))
    den = sqrt((sum_square_p1[1] - pow(sum_square_p1[0], 2) / num_common_movies) * (sum_square_p2[1] - pow(sum_square_p2[0], 2) / num_common_movies))
        
    # Avoid div by 0
    if den == 0:
        return 0
    else:
        # Sum of products - (product of sum / n)
        return  (prod_prefs - (sum_square_p1[0] * sum_square_p2[0] / num_common_movies)) / den
    

#Returns the best match for the person from the prefs dictionary
def topMatches(prefs, person, n=5, similarity=sim_pearson):    
    #Using heapq for top n. For large n close to the size of the list this isnt optimal and sort works better
    #Not adding this unnecessary optimization though
    return nlargest(n, [(similarity(prefs, person, other), other) for other in prefs if other != person])

#
def getRecommendations(prefs, person, similarity=sim_pearson):    
    
    #Step 1: Get a similarity score with others, the result is a list of 2 tuple, (similarity score, name of the person)
    similarity_with_others = filter(lambda x: x[0] > 0, topMatches(prefs, person, len(prefs) - 1, similarity))      
    p_movies = prefs[person]    

    #Step 2: Find movies present in all other peoples maps which are either not present in the person's map or
    #if present has a score of 0, since there will be duplicates, have a set
    movies_not_rated_by_person = set(
                                     [movie for other in prefs if other != person 
                                        for movie in prefs[other] if movie not in p_movies or p_movies[movie] == 0]
                                    )
    
    #Step 3: Compute the weighted scores, the result is a list of three tuple
    # (movie_name, similarity_score_in_step_1, similarity_score_in_step1 * rating_by_the_person_for_the_movie)
    weighted_scores = [(movie, sim[0], sim[0] * prefs[sim[1]][movie]) 
           for sim in similarity_with_others 
           for movie in prefs[sim[1]] if movie in movies_not_rated_by_person and prefs[sim[1]][movie] != 0 ]
    
    #Step 4. Group by the list in step 3 by the movie_name, 
    #the grouped by result is a key and an iterable of the values for that key
    # We now run a reduce operation to emit the following List
    # (movie_name, sum_of_the_similarityscores, sum_of_the_weighted_similarity_scores_from_step3
    #IMP: groupby requires the list of 3 tuples to be sorted, else, the groupby will yield unexpected results) 
    reduced_weighted_scores = [(reduce(lambda x, y : (x[0], x[1] + y[1], x[2] + y[2]) , grouped_values))
                                for _, grouped_values in groupby( sorted(weighted_scores), lambda x : x[0] )]
    
    #Step 5: Return the sorted list of recommendations by the score, 
    # score is the sum_of_weighted_similarity_score/sum_of_similarity_score
    return sorted(map(lambda x : (x[2]/x[1], x[0]), reduced_weighted_scores), reverse = True)
    

    
print "Similarity by Euclidean distance between Lisa Rose and Gene Seymour is ", sim_distance(critics, "Lisa Rose", "Gene Seymour")
print "Similarity by Euclidean distance between Lisa Rose and Jack Matthews is ", sim_distance(critics, "Lisa Rose", "Jack Matthews")
print "Similarity by Pearson distance between Lisa Rose and Gene Seymour is ", sim_pearson(critics, "Lisa Rose", "Gene Seymour")
print "Similarity by Pearson distance between Lisa Rose and Jack Matthews is ", sim_pearson(critics, "Lisa Rose", "Jack Matthews")
print "Top 3 matches using pearson distance for Toby are ", topMatches(critics, 'Toby', n = 3)
print "Top Recommendations for Toby are by pearson distance ", getRecommendations(critics, "Toby")
print "Top Recommendations for Toby are by euclidean distance ", getRecommendations(critics, "Toby", similarity=sim_distance)
