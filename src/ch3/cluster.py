'''
Created on Sep 5, 2015

@author: Amol
'''

from math import sqrt
from operator import add
from PIL import Image, ImageDraw
from random import random

#Reads the pigeonhole file
def process_line(line):
    splits = line.split('\t')
    return splits[0], map(lambda v: float(v), splits[1:])


#
#
#
def readfile(file_name="blogdata.txt"):    
    lines = [line for line in file(file_name)]    
    colnames = lines[0].split('\t')[1:]
    [rownames, values] = zip(*map(process_line, lines[1:]))
    return rownames, colnames, values    


#Find the distance between given two List of numbers
#
#

def find_sum_and_sum_square(list_of_numbers):    
    return reduce(
        lambda (acc_sum, acc_sqr_sum), (next_num, next_sqr_num): (acc_sum + next_num, acc_sqr_sum + next_sqr_num),  
           map(lambda num: (num, pow(num, 2)), list_of_numbers)
    )
    

#
# Find distance between two Lists using pearson method
#
def pearson(v1, v2):
    #No validation for equal length for now
    len_lists =  len(v1)
    (sum_of_v1, sum_square_v1) = find_sum_and_sum_square(v1)
    (sum_of_v2, sum_square_v2) = find_sum_and_sum_square(v2)
    prod_sum_of_lists = reduce(
                               lambda acc_prod_sum, curr_prod_sum : curr_prod_sum + acc_prod_sum,     
                                map( lambda (first, second): first * second, zip(v1, v2) )
                        )
    # ProdSum - SumProd/n
    numerator = prod_sum_of_lists - (sum_of_v1 * sum_of_v2 / len_lists)
    #sqrt (prod of SumSqr - SrqSum/2 of both )
    denominator = sqrt( ( sum_square_v1 - pow(sum_of_v1, 2) / len_lists ) * ( sum_square_v2 - pow(sum_of_v2, 2) / len_lists ) )
    
    return 1 - (numerator/ denominator)

#
#
#
class bicluster:
    def __init__(self, vec, left = None, right = None, distance = 0.0, clust_id = None):
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.clust_id = clust_id


cached_distances = {}

#
# Check if cached else compute and cache the distance before returning
#
def get_distance(cluster1, cluster2, distance_algo):
    key = (cluster1.clust_id, cluster2.clust_id)
    if key not in cached_distances:
        distance = distance_algo(cluster1.vec, cluster2.vec)
        cached_distances[key] = distance
    else:
        distance = cached_distances[key]

    return distance

#
#
#

def combine_clusters(cluster1, cluster2, distance, new_cluster_index):
    #TOD/o: Use lazy eval    
    merged_vec = map(lambda (f, s): (f + s)/ 2, [x for x in zip(cluster1.vec, cluster2.vec)])    
    clust = bicluster(merged_vec, cluster1, cluster2, distance, new_cluster_index)    
    return clust

#
#
#
def cluster_recursively(clusters, new_cluster_index = 0, distance_algo = pearson):    
    if len(clusters) == 1:
        return clusters[0]
    else:
        
        min_distance_index = (0, 1)
        min_distance = get_distance(clusters[0], clusters[1], distance_algo)        
        r1 = range(len(clusters))
        for i in r1:
            for j in range(i + 1, len(clusters)):
                distance = get_distance(clusters[i], clusters[j], distance_algo)
                if distance < min_distance:
                    min_distance_index = (i, j)
                    min_distance = distance       
        
        new_cluster = combine_clusters(clusters[min_distance_index[0]], clusters[min_distance_index[1]], min_distance, new_cluster_index - 1)
        #Delete the higher index first
        del clusters[min_distance_index[1]]
        del clusters[min_distance_index[0]]        
        clusters.append(new_cluster)                
        return cluster_recursively(clusters, new_cluster_index - 1, distance_algo)


#
#
#
def hcluster(rows, distance=pearson):
    print "Creating Hierarchical cluster for", len(rows), "rows"
    clust = cluster_recursively(
                clusters = [bicluster(vec = rows[i], clust_id = i) for i in range(len(rows))], 
                distance_algo = distance
        )
    print "Hierarchical cluster creation successful"
    return clust

#
#
#
def printclust(clust, labels=None, n = 0):
    for i in range(n): print ' ',
    if clust.clust_id < 0:
        #Just additional info to print the distance of its two children
        print '- (', clust.distance, ')'
        #print '- '
    else:
        if labels == None:  print clust.clust_id
        else: print labels[clust.clust_id]
        
    if clust.left != None: printclust(clust.left, labels = labels, n = n + 1)
    if clust.right != None: printclust(clust.right, labels = labels, n = n + 1)

#######Code for Drawing Dendrogram as an Image goes here, #################
##### TODO: verbose code, taken as is from the book, analyse well later 
#
#
#
def getheight(clust):
    if clust.left == None and clust.right == None: return 1
    return getheight(clust.left) + getheight(clust.right)

#
#
#
def getdepth(clust):
    if clust.left == None and clust.right == None: return 0
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


def drawnode(draw, clust, x, y, scaling, label):
    if clust.clust_id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        ll = clust.distance * scaling
        fill = (255, 0, 0)
        draw.line((x, top + h1/2, x, bottom - h2/2), fill)
        draw.line((x, top + h1/2, x + ll, top + h1/2), fill)
        draw.line((x, bottom - h2/2, x + ll, bottom - h2/2), fill)
        drawnode(draw, clust.left, x + ll, top + h1/2, scaling, label)
        drawnode(draw, clust.right, x + ll, bottom - h2/2, scaling, label)
    else:
        # If this is an endpoint draw the item label
        draw.text((x + 5, y - 7), label[clust.clust_id], (0, 0, 0))

#
#
#
def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    h = getheight(clust) * 20
    w = 1200    
    depth = getdepth(clust)    
    #Why 150?    
    scaling = (w - 150) / depth    
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h/2, 10, h/2), fill = (255, 255, 0))
    drawnode(draw, clust, 10, h/2, scaling, labels)
    img.save(jpeg, 'JPEG')
    print "Dendrogram successfully saved to ", jpeg
    

#
#
#
def rotatematrix(data):
    newdata = []    
    for i in range(len(data)):
        newdata.append([data[j][i] for j in range(len(data))])
    
    return newdata

###############################################################################################################            

#
# For n items of length m each, find  the min and max value for each of the m numbers across these
#n items
#
# for e.g 
#    1 2 3 4
#    5 6 7 8 
#    4 3 2 1 
#
#Output is [ (1, 5), (2, 6), (2, 7), (1, 8) ]
#
# The min and the max values are computed by the above function get_min_max_range_values and are computed for each point
# That is min and max value for 1th location in each of the n rows
def get_min_max_range_values(rows):    
     
    return [
        reduce(
           lambda (min_val, max_val), (curr_1, curr_2): 
                (min_val if min_val < curr_1 else curr_1, max_val if max_val > curr_2 else curr_2),
            [(row[i], row[i]) for row in rows]
          )
        for i in range(len(rows[0]))]

#
# Get an List of K elements. Each element is a list same as the number of elements in the given min_max_range_values
# The value of each of these lists is 
# some_random_value * (max_value - min_value) + min_value
#
# The min and the max values are computed by the above function get_min_max_range_values and are computed for each point
# That is min and max value for 1th location in each of the n rows
#
def get_k_centroids(min_max_range_values, k):
    return [[random() * (min_max_range_values[i][1] - min_max_range_values[i][0]) + min_max_range_values[i][0] 
     for i in range(len(min_max_range_values))] for _ in range(k)]

#print get_min_max_range_values( [ [1, 2, 3, 4], [5, 6, 7, 8], [4, 3, 2, 1] ])

#print get_k_centroids(get_min_max_range_values( [ [1, 2, 3, 4], [5, 6, 7, 8], [4, 3, 2, 1] ]), k = 2)


#
#
# on invoking for e.g. find_mean_of_arrays([[1, 2, 3], [4, 5, 6]])
# We get [2.5, 3.5, 4.5] 
def find_mean_of_arrays(list_of_arrays):
        added_list = reduce (
                        lambda cumulated_list, next_list: 
                            map(add,cumulated_list, next_list),
                            list_of_arrays)
        total_closes_nodes = len(list_of_arrays)
        return map(lambda element: float(element) / total_closes_nodes, added_list)
        

#
#
#        
def kclusters(rows, distance = pearson, k = 4):
    ranges = get_min_max_range_values(rows)
    clusters = get_k_centroids(ranges, k)
    
    #perform the operation of placing each of the n rows into k clusters repeatedly
    #till two subsequent iterations of partitioning the n rows in k clusters yield same result
    #Need to check if this assumption of using 100 iterations is good enough or that needs to be derived
    #based on the number of k clusters and n rows
    
    #Stores the matches found in last iteration
    lastmatches = None
    for i in range(100):
        print "Executing the ", i, 'th iteration'        
        #For each of the rows, find which of the k centroids given in the variable clusters are close
        bestmatches = [[] for _ in range(k)]
        bestmatches_indexes = [[] for _ in range(k)]
        for index in range(len(rows)):
            row = rows[index]            
            #This is a list of lists where the total number of elements equal to the number of rows.
            #Each of the k sub lists hold the multiple rows from the original set of rows provided.
            #Note that one row can belong to only one of the k sub list            
            bestmatch = 0
            bestdistance = distance(clusters[0], row)
            for j in range(1, k):
                d = distance(clusters[j], row)
                if d < bestdistance:
                    bestdistance = d
                    bestmatch = j
            
            bestmatches[bestmatch].append(row)
            bestmatches_indexes[bestmatch].append(index)    
        
        if bestmatches == lastmatches:
            #No need to0 further iterate as the n rows are now stable in k clusters
            break
        else:
            lastmatches = bestmatches
            
        #After the previous iteration, we have segregated all n rows in these k clusters.
        #Next step is to move these k centroids to the center of the data points in that particular cluster    
        #For finding the new centroids, simply addup arrays element wise for the given centroid's bestmatches.    
        clusters = [find_mean_of_arrays(closest_nodes) for closest_nodes in bestmatches]

    
    return bestmatches_indexes


        
blognames, words, data = readfile(file_name = "../../dataset/blogdata.txt")
#blognames, words, data = readfile()
#clust = hcluster(data)
# #printclust(clust, labels = blognames)
# drawdendrogram(clust, blognames)
# wordclust = hcluster(rotatematrix(data))
# drawdendrogram(wordclust, labels = words, jpeg='wordclust.jpg')
k = 10
kclust = kclusters(data, k = k)
for i in range(10):
    print "Printing Cluster ", (i + 1)
    print [blognames[i] for i in kclust[i]]
    
