import gzip
from collections import defaultdict
import random as rd

def readGz(f):
  for l in gzip.open(f):
    yield eval(l)

########### Reading the training data ################
valdn_rating = []
train_count = 0
userRatings = defaultdict(list)
tusers = []
tbusiness = []
usr_bus_rating = []
usr_bus_validation_rating = []
for l in readGz("assignment1/train.json.gz"):
        train_count +=1
        user,business = l['userID'],l['businessID']
        tusers.append(user)
        tbusiness.append(business)
        usr_bus_rating.append([user,business,l['rating']])
        userRatings[user].append(l['rating'])


############### 
Busers = defaultdict(list)
Bitems = defaultdict(list)
for u in tusers:
    if u not in Busers.keys():
        Busers[u].append(0.0)
for i in tbusiness:
    if i not in Bitems.keys():
        Bitems[i].append(0.0)

for u in Busers:
    rating_sum = []
    item       = []
    for i in usr_bus_rating: 
        if u == i[0]:
            rating_sum.append(i[2])
            item.append(i[1])
    Busers[u].append(sum(rating_sum))
    Busers[u].append(len(rating_sum))
    Busers[u].append(item)
    

for u in Bitems:
    rating_sum = []
    usr_id     = []
    for i in usr_bus_rating: 
        if u == i[1]:
            rating_sum.append(i[2])
            usr_id.append(i[0])
    Bitems[u].append(sum(rating_sum))
    Bitems[u].append(len(rating_sum))
    Bitems[u].append(usr_id)
    


########## Implementing Latent Factor Model #############
for u in Busers:
    Busers[u][0] = 0.0
for i in Bitems:
    Bitems[i][0] = 0.0
meansquareerror = []
lambda1 = [4.5]
for lamda in lambda1:
 for i in range(100):
    ## Update Alpha
    alpha = 0
    for i in usr_bus_rating:
        alpha += float(i[2]) - float(Busers[i[0]][0]) - float(Bitems[i[1]][0])
    alpha = alpha/(len(usr_bus_rating))
    
    ## Update Busers
    for u in Busers:
        Busers[u][0] = Busers[u][1]-alpha*Busers[u][2]
        for i in Busers[u][3]:
            Busers[u][0] -= Bitems[i][0]
        Busers[u][0] = Busers[u][0]/(lamda + Busers[u][2])

    ## Update Bitems
    for u in Bitems:
        Bitems[u][0] = Bitems[u][1]-alpha*Bitems[u][2]
        for i in Bitems[u][3]:
            Bitems[u][0] -= Busers[i][0]
        Bitems[u][0] = Bitems[u][0]/(lamda + Bitems[u][2])

		
####### Function that returns Predicted Rating #########
def pred(u,i):
    if u not in Busers.keys():
        Betauser = 0.20
    else:
        Betauser = Busers[u][0]
        
    if i not in Bitems.keys():
        Betaitem = -0.30
    else:
        Betaitem = Bitems[i][0]
    
    return (alpha + Betauser + Betaitem - Betaitem*Betauser/2.0) 

	
########### Writing predictions back to a file ##########
count = 0
predictions = open("predictions_Rating.txt", 'w')
for l in open("assignment1/pairs_Rating.txt"):
    if l.startswith("userID"):
        predictions.write(l)
        continue
    u,i = l.strip().split('-')
    a = pred(u,i)
    
    if int((a*100)%100) >= 98 or int((a*100)%100) == 0:
        tmp_md = round(pred(u,i),2)
        predictions.write(u + '-' + i + ',' + str(tmp_md) + '\n')
    else:
        predictions.write(u + '-' + i + ',' + str(pred(u,i)) + '\n')              
    
predictions.close()
		
		