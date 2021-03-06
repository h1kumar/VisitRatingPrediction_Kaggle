import gzip
from collections import defaultdict
import random as rd
import numpy  as np

def readGz(f):
    for l in gzip.open(f):
        yield eval(l)
		
##### Reading Training Data ########
bus_usr_list   = defaultdict(list)
usr_categories = defaultdict(list)
bus_categories = defaultdict(list)
tusers         = [] ## List of all User ID's
tbusinesses    = [] ## List of all Business ID's

for l in readGz("assignment1/train.json.gz"):
    user,business = l['userID'],l['businessID']
    bus_usr_list[business].append(user)
    tusers.append(user)
    tbusinesses.append(business)
    for l1 in l['categories']:
        usr_categories[user].append(l1)
        bus_categories[business].append(l1)
		
		
###### Implementing Collaborative Filtering ##########
###### Between User-User & Item-Item Similarity ######

Busers = defaultdict(list)
Bitems = defaultdict(list)

index = 0
for u in tusers:
    if u not in Busers.keys():
        Busers[u].append(index)
        index += 1

index = 0
for i in tbusinesses:
    if i not in Bitems.keys():
        Bitems[i].append(index)
        index += 1
		
a = [[0.0]*len(Busers)]*len(Bitems)
b = np.matrix(a)

for bus in bus_usr_list:
    for u in bus_usr_list[bus]:
        b[Bitems[bus][0],Busers[u][0]] = 1
		
d1 = defaultdict(list)
for u in Busers.keys():
    d1[u] =  [b[:,Busers[u][0]].T*b]
    
d2 = defaultdict(list)
for u in Bitems.keys():
    d2[u] =  [b[Bitems[u][0],:]*b.T
	
	
############################################
####### Making Predictions #################
############################################

predictions = open("predictions_Visit.txt", 'w')
for l in open("assignment1/pairs_Visit.txt"):
    if l.startswith("userID"):
        predictions.write(l)
        continue
    u,bus = l.strip().split('-')
    if u not in Busers.keys() or bus not in Bitems.keys():
        predictions.write(u + '-' + bus + ",0\n")
        continue

    no_of_sim_user = 205
    ## sort in decreasing order, '-' makes largest value smallest
    idx =  np.argsort(-d1[u][0])[0,:no_of_sim_user] 
    index     = []
    weight    = []
    norm_wght = []
    for i in range(no_of_sim_user):
        weight.append(float(d1[u][0][0,idx[0,i]]))
        index.append(idx[0,i])

    for w in weight:
        norm_wght.append(w/sum(weight))
    
    sum1 = 0.0
    for i in range(len(index)):
        sum1 += norm_wght[i]*b[Bitems[bus][0],index[i]]

    if sum1>0.005:
        predictions.write(u + '-' + bus + ",1\n")
    else:
        no_of_sim_user1 = 205
        ## sort in decreasing order, '-' makes largest value smallest
        idx1 =  np.argsort(-d2[bus][0])[0,:no_of_sim_user1] 
        index1     = []
        weight1    = []
        norm_wght1 = []
        for i in range(no_of_sim_user1):
            weight1.append(float(d2[bus][0][0,idx1[0,i]]))
            index1.append(idx1[0,i])

        for w in weight1:
            norm_wght1.append(w/sum(weight1))
    
        sum2 = 0.0
        for i in range(len(index1)):
            sum2 += norm_wght1[i]*b[index1[i],Busers[u][0]]

        if sum2>0.005:
            predictions.write(u + '-' + bus + ",1\n")
        else:
            predictions.write(u + '-' + bus + ",0\n")
predictions.close()   
print "Done"