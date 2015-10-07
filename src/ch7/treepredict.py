'''
Created on Oct 4, 2015

@author: Amol
'''
from itertools import groupby
from math import log

my_data = [['slashdot', 'USA', 'yes', 18, 'None'],
        ['google', 'France', 'yes', 23, 'Premium'],
        ['digg', 'USA', 'yes', 24, 'Basic'],
        ['kiwitobes', 'France', 'yes', 23, 'Basic'],
        ['google', 'UK', 'no', 21, 'Premium'],
        ['(direct)', 'New Zealand', 'no', 12, 'None'],
        ['(direct)', 'UK', 'no', 21, 'Basic'],
        ['google', 'USA', 'no', 24, 'Premium'],
        ['slashdot', 'France', 'yes', 19, 'None'],
        ['digg', 'USA', 'no', 18, 'None'],
        ['google', 'UK', 'no', 18, 'None'],
        ['kiwitobes', 'UK', 'no', 19, 'None'],
        ['digg', 'New Zealand', 'yes', 12, 'Basic'],
        ['slashdot', 'UK', 'no', 21, 'None'],
        ['google', 'UK', 'yes', 18, 'Basic'],
        ['kiwitobes', 'France', 'yes', 19, 'Basic']]

class decisionnode:
    
    #
    #    col:      Column index of the criteria to be tested
    #    value:    Value the column must match to get true result
    #    results:  Dictionary of results, only for leaf nodes
    #    tb:       Branch taken on true condition
    #    fb:       Branch taken on false condition
    #    
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
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
    




#
# Get the dictionary of possible results. The function assumes the last column in each row is the result 
#
def uniquecounts(rows):        
    values = sorted([(row[len(row) - 1], 0) for row in rows])
    return dict([(k, len(list(v))) for k, v in groupby(values, lambda (k, _) : k)])

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
#
#  This however is simplified by doing the following 1 - ( P(N)*P(N) + P(B)*P(B) + P(P)*P(P) )
def giniimpurity(rows):
    total = len(rows)
    probs = map(lambda v: float(v) / total, uniquecounts(rows).values())
    return 1 - sum([p * p for p in probs])

# Entropy is the amount of disorder in the set.
# It is defined as p(i) * log2(p(i)) for all outcomes
def entropy(rows):
    total = len(rows)
    probs = map(lambda v: float(v) / total, uniquecounts(rows).values())
    return sum(map(lambda p:-p * log(p, 2), probs))


#
#
#
def buildtree(rows, scoref=entropy):
    if len(rows) == 0 : return decisionnode()
        
    current_score = scoref(rows)
    
    # Initialize with defaults
    best_gain = 0.0
    best_criteria_col_index, best_criteria_col_value = (None, None) 
    best_true_set, best_false_set = (None, None)
    
    # Algorithm is as follows
    # 1. For each of the columns, find distinct values across the rows
    # 2. Partition the set into two, called set1 and set2  based on each of these columns and the corresponding values they hold
    # 3. Calculate the information gain as follows
    #        info_gain = current_score - P(set1) * scoref(set1) - P(set2) * scoref(set2)
    # 4. If info gain is negative, no point going ahead, this is the leaf node. Set the result as the uniquecount(rows)
    # 5. If however, the information gain is more than 0, then take the best set1 and set2 and the partitioning column and value
    #   as the criteria
    # 6. Recursively call buildtree on set1 and set2 to get the true and false branch and return a decisionnode with the returned
    #    left and right tree and the best criteria column index and value
    
    row_val_pair = frozenset([(i, row[i]) for i in range(len(rows[0]) - 1) for row in rows])
    #row_val_pair = [(i, row[i]) for i in range(len(rows[0])) for row in rows]
    n_rows = len(rows)
    
    for column, value in row_val_pair:
        t_set, f_set = divideset(rows, column, value)
        p = float(len(t_set)) / n_rows
        gain = current_score - p * scoref(t_set) - (1 - p) * scoref(f_set) 
        if gain > best_gain and len(t_set) > 0 and len(f_set) > 0:
            best_gain = gain
            best_criteria_col_index, best_criteria_col_value = (column, value)
            best_true_set, best_false_set = (t_set, f_set)
        
    
    if best_gain > 0:
        # Intermediate node 
        tb = buildtree(best_true_set, scoref)
        fb = buildtree(best_false_set, scoref)
        return decisionnode(col=best_criteria_col_index, value=best_criteria_col_value, tb=tb, fb=fb)
    else:
        # It is a leaf node
        return decisionnode(results=uniquecounts(rows))



#Taken as is
def printtree(tree, indent=''):
    # Is this a leaf node?
    if tree.results != None:
        print str(tree.results)
    else:
        # Print the criteria
        print str(tree.col) + ':' + str(tree.value) + '? '
        # Print the branches
        print indent + 'T->',
        printtree(tree.tb, indent + '  ')
        print indent + 'F->',
        printtree(tree.fb, indent + '  ')


#Taken as is
def classify(observation,tree):
    if tree.results!=None:
        return tree.results
    else:
        v=observation[tree.col]
        branch=None
        if isinstance(v,int) or isinstance(v,float):
            if v >= tree.value: 
                branch=tree.tb
            else: 
                branch=tree.fb
        else:
            if v==tree.value: 
                branch=tree.tb
            else: 
                branch=tree.fb
        
        return classify(observation,branch)

# print(uniquecounts(my_data))
# print giniimpurity(my_data) # 0.6328125
# print entropy(my_data)  #1.50524081494
# yes_list, no_list = divideset(my_data, 2 , 'yes')
# print entropy(yes_list)
# print giniimpurity(yes_list)


#
#
# Prune a tree
def prune(tree, mingain, scoref=entropy):
    #TODO: Prune the tree here here
    None


tree = buildtree(my_data)
#print "Built tree is " 
printtree(tree)
print "Testing the tree from the training data, should get 100% accuracy"
total = 0
failure = 0
for data in my_data:
    res = classify(data[0:4], tree)
    total += 1   
    if res.keys()[0] != data[4]:
        failure += 1

print "Total: %s, Passed: %s, Failed: %s with an accuracy of %s%s" %(total, (total - failure), failure,  float( (total - failure) * 100 / total), '%')

print "Prediction for ['(direct)', 'USA', 'yes', 5] is %s"% (classify(['(direct)', 'USA', 'yes', 5], tree))

 
        