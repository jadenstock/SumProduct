#Jaden Stock

from BNet import *
import numpy as np
import itertools
import copy
import sys

def sum_product(BN, iters = 10, output = "results.txt"):

	factors = [Factor(BN, var) for var in BN.vars] #these are all of the factors in the factor graph. There is a one to one correspondence between factors and variables.
	edges = dict([(var, [f for f in factors if var in f.vars]) for var in BN.vars]) #this is a dict from variables to a list of all factors containing that variable.
	#for every variables we keep a list of vectors. Each vector corresponds to a factor in the graph containing the var. These vectors are the "messages" that this var will
	#send to that factor. the order is implicit. namely that i-th vector here corresponds to the i-th factor in edges[var].
	states = dict([(var, [np.array([1 for i in xrange(len(BN.vars[var]))]) for j in xrange(len(edges[var]))])for var in BN.vars])
	#this is where we store the messages from factors to vars, before we multiply them to send them back up to factors.
	incoming_messages = dict([(var, [np.array([1 for i in xrange(len(BN.vars[var]))]) for j in xrange(len(edges[var]))])for var in BN.vars])

	#do some number of iterations of message passing
	for i in xrange(iters):

		for factor in factors:
			for var in factor.vars:
				message = [0 for _ in xrange(len(BN.vars[var]))] #this is the message we will send to var

				tmp_messages = [np.array([1 for _ in xrange(len(BN.vars[factor.vars[j]]))]) for j in xrange(len(factor.vars))] #the messages from varianbles to the factor
				tgt_index = factor.vars.index(var) #the index of the var we are sending a message to
				for k in xrange(len(factor.vars)): 
					if k != tgt_index:
						factor_index = edges[factor.vars[k]].index(factor)
						
						if len(states[factor.vars[k]]) > 1:
							tmp_messages[k] = np.prod([states[factor.vars[k]][j] for j in xrange(len(states[factor.vars[k]])) if j != factor_index], axis = 0) #mulitply the messages together
				
				#normalize the tmp_messages
				for msg in tmp_messages:
					msg = msg*(1.0/sum(msg))

				#now we can actually construct the message
				for vals_assignment in itertools.product(*[BN.vars[v] for v in factor.vars]): #complete assignment of values to variables in factor
					vals_assignment = list(vals_assignment)
					prod_value = 1
					#get the product in formula (6)
					for t in xrange(len(tmp_messages)):
						if t != tgt_index:
							tmp_messages[t] = tmp_messages[t]*(1.0/sum(tmp_messages[t]))
							prod_value *= tmp_messages[t][BN.vars[factor.vars[t]].index(vals_assignment[t])] #index of this value for this variable

					message[BN.vars[var].index(vals_assignment[tgt_index])] += factor.funct(vals_assignment) * prod_value

				incoming_messages[var][edges[var].index(factor)] = np.array(copy.copy(message)) #put the message in the "queue"

		#move messages from incoming_messages to states
		for var in incoming_messages:
			states[var] = copy.copy(incoming_messages[var])
			for vect in states[var]: #normalize the vectors
				vect = (1.0/sum(vect))*vect
			
	#our final states are just a product of all of the state vectors for each var
	distributions = {}
	for var in states:
		dist = np.array([1 for _ in xrange(len(BN.vars[var]))])
		for vect in states[var]:
			dist = dist * vect
		distributions[var] = [x/float(sum(dist)) for x in dist]

	#write our results to a file
	f = open(output, "w")
	for var in BN.vars_in_order:
		f.write("{} ".format(var))
		for n in distributions[var]:
			f.write("{} ".format(n))
		f.write("\n")
	f.close()

if __name__== '__main__':
	net_name = sys.argv[1]
	net = BNet(net_name)
	sum_product(net, output = "{}-results.txt".format(net_name.replace(".bif", "")))