'''
Created on Sep 5, 2015

@author: Amol
'''

from math import sqrt

#Reads the pigeonhole file
def process_line(line):
    splits = line.split('\t')
    return splits[0], map(lambda v: float(v), splits[1:])


def readfile(file_name="blogdata.txt"):    
    lines = [line for line in file(file_name)]    
    colnames = lines[0].split('\t')[1:]
    [rownames, values] = zip(*map(process_line, lines[1:]))
    return rownames, colnames, values    


#Find the distance between given two List of numbers

def find_sum_and_sum_square(list_of_numbers):    
    return reduce(
        lambda (acc_sum, acc_sqr_sum), (next_num, next_sqr_num): (acc_sum + next_num, acc_sqr_sum + next_sqr_num),  
           map(lambda num: (num, pow(num, 2)), list_of_numbers)
    )
    

#
#
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

class bicluster:
    def __init__(self, vec, left = None, right = None, distance = 0.0, clust_id = None):
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.clust_id = clust_id


def cluster_recursively(clusters, cached_distances = {}, distance = pearson):
    if len(clusters) == 1 :
        return clusters[0]
    else:
        #TODO: Implement recursive invocation
        
        
        return None


def hcluster(rows, distance=pearson):     
    return cluster_recursively(
                cluster = [bicluster(id = i) for i in range(len(rows))], 
                distance = distance
        )
    
    
#readfile()
#pearson()