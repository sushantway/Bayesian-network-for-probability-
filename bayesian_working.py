# This file implements the variable enumeration algorithm described in the
# Bayes Network chapter of the Russel/Norvig textbook.
# I have assumed throughout that all the variables are Boolean.  This makes
# the code slightly simpler because there are always only two possible
# values to consider.  




# start reading from the bottom of the file up.


# my debug print function.  if I want debug messages printed, then
# print(args), otherwise do nothing.  this is nice so I can leave my
# debug statements in and just have them print when I want them.
def debugprint(*args):
    pass
    #print(args)


# compute probability that var has the value val.  e are the list of
# variable values we already know, and bn has the conditional probability
# tables.
def Pr(var, val, e, bn):
    parents = bn[var][0]
    debugprint('Pr***', var, val, e, bn, parents)
    if len(parents) == 0:
        truePr = bn[var][1][None]
    else:
        debugprint('   Pr***')
        parentVals = [e[parent] for parent in parents]
        truePr = bn[var][1][tuple(parentVals)]
    if val==True: return truePr
    else: return 1.0-truePr


# QX is a dictionary that have probabilities for different values.  this
# function normalizes so the probabilities all add up to 1.
def normalize(QX):
    total = 0.0
    for val in QX.values():
        total += val
    for key in QX.keys():
        QX[key] /= total
    return QX[1]


# The enumerate-ask function from the textbook that does the variable
# enumeration algorithm to compute probabilities in a Bayesian network.
# Remember this is exponential in the worst case!
#
# Note: in both this function and enumerateAll, I make sure to undo any
# changes to the dictionaries and lists after I am done with recursive
# calls.  This is needed because dictionaries and lists are passed by
# reference in python.  Instead of the undoing, I could use deep copy.
def enumerationAsk(X, e, bn,varss):
    QX = {}
    for xi in [False,True]:
        e[X] = xi
        QX[xi] = enumerateAll(varss,e,bn)
        del e[X]
    #return QX
    return normalize(QX)


# Helper function for enumerateAsk that does the recursive calls,
# essentially following the tree that is in the book.
def enumerateAll(varss, e,bn):
    debugprint('EnumerateAll***', varss, e, bn)
    if len(varss) == 0: return 1.0
    Y = varss.pop()
    if Y in e:
        val = Pr(Y,e[Y],e,bn) * enumerateAll(varss,e,bn)
        varss.append(Y)
        return val
    else:
        total = 0
        e[Y] = True
        total += Pr(Y,True,e,bn) * enumerateAll(varss,e,bn)
        e[Y] = False
        total += Pr(Y,False,e,bn) * enumerateAll(varss,e,bn)
        del e[Y]
        varss.append(Y)
        return total


# put the conditional probability tables for the Bayesian network into
# a dictionary.  The key is a string describing the node.
#
# The value for the key has the information about its parents and the
# conditional probabilities.  It is a list with two things.  The first
# thing is a list of the nodes parents (an empty list if there are no
# parents).  The second thing is the conditional probability table in a
# dictionary; the key to this dictionary is values for the parents, and the
# value is the probability of being True given these values for the parents.
bn = {'Burglary':[[],{None:.001}],
      'Earthquake':[[],{None:.002}],
      'Alarm':[['Burglary','Earthquake'],
               {(False,False):.001,(False,True):.29,
                (True,False):.94,(True,True):.95}],
      'JohnCalls':[['Alarm'],
                   {(False,):.05,(True,):.90}], #note: (False,) is a tuple with just the value False.  (False) would not be, python makes that just False, and that would not be good because the code above assumes it is a tuple.
      'MaryCalls':[['Alarm'],
                   {(False,):.01,(True,):.70}]}

# a list of the variables, starting "from the bottom" of the network.
# in the enumerationAsk algorithm, it will look at the variables from
# the end of this list first.
varss = ['MaryCalls','JohnCalls','Alarm','Burglary','Earthquake']

# call the enumerationAsk function to figure out a probability.
#print(enumerationAsk('Alarm',{'MaryCalls':False},bn,varss))




# ***
# Now this part of the file has some code to do random sampling to estimate
# probabilities in a Bayes Net.
# ***

import random

# obtain a random sample from the bayes net.  this will return values
# for all of the variables that are sampled according to the probabilities
# in the bayes net.  the varss list is a list of the variables in order
# from "bottom to top", so we'll start looking at the variables from the
# end - we sample the parents before the children.
def priorSample(bn, varss):
    # first reverse variables so they are top down.
    varss.reverse()

    # e will keep track of values for the variables
    e = {}
    for var in varss:
        # pick a value for var according to the probabilities in bn and the
        # ones we already picked.

        # probability it is True.
        prTrue = Pr(var,True,e,bn)

        # then set it to True with prTrue and False otherwise.
        if random.uniform(0.0,1.0) <= prTrue:
            e[var] = True
        else:
            e[var] = False

    # reverse variable list again so it is the same as it was before this
    # function was called.
    varss.reverse()

    # return the sample - e
    return e

#print(priorSample(bn,varss))


# see if the two sets of variable settings are consistent
def consistent(e1, e2):
    for k in e1:
        if k in e2 and e1[k] != e2[k]: return False
    return True
    

# do rejection sampling.  So take samples to estimate the probability
# that X is True or False given the values of variables that are already
# known in e.  Take N many samples.
def rejectionSample(X,bn,e,num,varss):
    N = {True:0, False:0}
    for i in range(0, num):
        sample = priorSample(bn,varss)
        if consistent(sample,e):
            N[sample[X]] += 1
    # then look at all the samples we have, and just print the fraction
    # of them that have X set to either True or False.
    total = float(N[True] + N[False])
    if total <= .5:
        print('No values...')
        return None
    QX = {True: N[True]/total, False: N[False]/total}
    return [QX, N]



v_list = ['Alarm','Burglary','Earthquake','JohnCalls','MaryCalls']
input_list = []
variable_list = {}
count = 0
for i in v_list:
    print(i)
    temp = input("Enter value for %s: "%i)
    input_list.append(temp)
    if temp == '0':
        print("zero")
        variable_list[i] = 'given false'
    elif temp == '1':
        print("one")
        variable_list[i] = 'given true'
    elif temp == '2':
        print("two")
        variable_list[i] = 'query false'
    elif temp == '3':
        print("three")
        variable_list[i] = 'query true'
    elif temp =='4':
        print("four")
        count= count + 1
        variable_list[i] = 'unspecified'
#print(input_list)
print(variable_list)
print(count)
rules = {0: 'given false',1: 'given true',2: 'query false',3: 'query true',4: 'unspecified'}
#print(rules)

#e_dict = {}

Xfound = 0
prob_E = 0.002 #using the probability values from table. No hardcoding
prob_B = 0.001 #using the probability values from table. No hardcoding
prob_A = 0.002516442
prob_J = 0.052142
prob_M = 0.0117388
if(count == 3):
    for i in variable_list:
        if(variable_list[i] == 'query false' and Xfound == 0):
            X = i
            print(X)
            Xflag = 0
            Xfound = 1
        elif(variable_list[i] == 'query true' and Xfound == 0):
            X = i
            print(X)
            Xflag = 1
            Xfound = 1
        if(variable_list[i] == 'query true' and Xfound == 1):
            value = True
            key = i
            if(key == 'Burglary'):
                PY = prob_B
            elif(key == 'Earthquake'):
                PY = prob_E
            elif(key == 'JohnCalls'):
                PY = prob_J
            elif(key == 'MaryCalls'):
                PY = prob_M
        elif(variable_list[i] == 'query false' and Xfound == 1):
            value = False
            key = i
            if(key == 'Burglary'):
                PY = 1 - prob_B
            elif(key == 'Earthquake'):
                PY = 1 - prob_E
            elif(key == 'JohnCalls'):
                PY = 1 - prob_J
            elif(key == 'MaryCalls'):
                PY = 1 - prob_M
        #print(rejectionSample('Burglary',bn,{'JohnCalls':True,'MaryCalls':True},10000,varss))
    #print(key)
    PX = enumerationAsk(X,{key:value},bn,varss)
    if(Xflag == 0):
        PX = 1 - PX
    print(PX)
    print(PY)
    prob = PX * PY
    print(prob)

if(count == 4):
    for i in variable_list:
        if(variable_list[i] == 'query true'):
            if(i == 'Alarm'):
                prob = prob_A
                print(prob)
            elif(i == 'Burglary'):
                prob = prob_B
                print(prob)
            elif(i == 'Earthquake'):
                prob = prob_E
                print(prob)
            elif(i == 'JohnCalls'):
                prob = prob_J
                print(prob)
            elif(i == 'MaryCalls'):
                prob = prob_M
                print(prob)
        elif(variable_list[i] == 'query false'):
            if(i == 'Alarm'):
                prob = 1 - prob_A
                print(prob)
            elif(i == 'Burglary'):
                prob = 1 - prob_B
                print(prob)
            elif(i == 'Earthquake'):
                prob = 1 - prob_E
                print(prob)
            elif(i == 'JohnCalls'):
                prob = 1 - prob_J
                print(prob)
            elif(i == 'MaryCalls'):
                prob = 1 - prob_M
                print(prob)


if(count == 2):
    F_element = 0
    S_element = 0
    for i in variable_list:
        if(variable_list[i] == 'query true' and F_element == 0):
            X = i
            F_element = 1
            F_flag = 1
            print(X)
        elif(variable_list[i] == 'query false' and F_element == 0):
            X = i
            F_flag = 0
            F_element = 1
            print(X)
        if(variable_list[i] == 'query true' and F_element == 1 and S_element == 0 and i != X):
            Y = i
            S_element = 1
            S_flag = 1
            print(Y)
        elif(variable_list[i] == 'query false' and F_element == 1 and S_element == 0 and i != X):
            Y = i
            S_element = 1
            S_flag = 0
            print(Y)
        if(variable_list[i] == 'given true' and F_element == 1 and S_element == 1):
            value = True
            key = i
            print(key)
        elif(variable_list[i] == 'given false' and F_element == 1 and S_element == 1):
            value = False
            key = i
            print(key)
    PX1 = enumerationAsk(X,{key:value},bn,varss)
    if(F_flag == 0):
        PX1 = 1 - PX1
    PX2 = enumerationAsk(Y,{key:value},bn,varss)
    if(S_flag == 0):
        PX2 = 1 - PX2
    print(PX1)
    print(PX2)
    prob = PX1 * PX2
    print(prob)


            
            
    
        
    
    
        
        
            


#print(enumerationAsk('Alarm',{'MaryCalls':False},bn,varss))
