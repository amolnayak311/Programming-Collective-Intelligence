'''
Created on Oct 4, 2015

@author: Amol
'''
from itertools import groupby

my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]

class decisionnode:
    
    #
    #    col:      Column index of the criteria to be tested
    #    value:    Value the column must match to get true result
    #    results:  Dictionary of results, only for leaf nodes
    #    tb:       Branch taken on true condition
    #    fb:       Branch taken on false condition
    #    
    def __init__(self, col = -1, value = None, results = None, tb = None, fb = None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb
        



#
# Divide the given rows in two lists based on the following condition
# For numeric types, the split lists are based on the condition >= and < the given value
# for other types the check splits the rows in row based on whether the value is = or not = to the given value
#
def divideset(rows, column, value):
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value
        
    return (
        [row for row in rows if split_function(row)],
        [row for row in rows if not split_function(row)]
    )
    

# (yes_list, no_list) = divideset(my_data, 2 , 'yes')
# print yes_list
# print no_list


#
# Get the dictionary of possible results. The function assumes the last column in each row is the result 
#
def uniquecounts(rows):        
    values = sorted( [(row[len(row) - 1], 0) for row in rows] )
    return dict([(k, len(list(v))) for k, v in groupby(values, lambda (k, _) : k )])

# Probability that a randomly placed item will
# be in the wrong category
# In this case it is as follows
#    Item is None and Classified as Basic
#    or
#    Item is None and Classified as Premium
#    or
#    Item is Basic and Classified as None
#    or
#    Item is Basic and Classified as Premium
#    or
#    Item is Premium and Classified as None
#    or
#    Item is Premium and Classified as Basic
#    Mathematically it is 
#
#    P(N)*P(B) + P(N)*P(P) + P(B)*P(N) + P(B)*P(P) + P(P)*P(N) + P(P)*P(B)
#    where
#    P(N)    The Result is None,
#    P(B)    The Result is Basic, that is the membership chosen is Basic
#    P(P)    The Result is Premium, that is the membership chosen is Premium
def giniimpurity(rows):
    total=len(rows)
    counts=uniquecounts(rows)
    values = [counts[c] for c in counts]
    return sum([float(v1) / total  * float(v2) / total for v1 in values for v2 in values if v1 != v2])    


#print giniimpurity(my_data) # 0.6328125


#print(uniquecounts(my_data))

