# Jaden Stock
# Class for Bayesian Networks

#an ADT for a Bayesian Network. It takes a .BIF file on construction.
#getting the CDP of a variable takes consant time
class BNet():

	def __init__(self, file_name):
		self.file_name = file_name #the file name which we built our BN from
		self.vars_in_order = []
		self.vars = {} #the keys are the variables and the values are lists of possible values for those variables
		self.parents = {} #the keys are variables and the values are lists of parents of that variable in the BN
		self.roots = {} #the keys are vairables with no parents ("roots"), and the values are lists of probabilities for each value
		self.CPTs = {} #main data structure for holding conditional probability tables. the keys are variable names,
						#the value is another dict which goes from tuples of values for parents to the conditional probability given those values

		#read in the file
		f = open(file_name, "r")
		for line in f:

			#if the line starts with variables then we are about to read in a new variable
			if line.startswith("variable"):
				line = line.split() #split on spaces
				var = line[1]
				self.vars_in_order.append(var)
				line = f.next() #go to the next line
				line = line[line.index("{") + 1: line.index("}")] #just get what is in the curly braces
				line = line.replace(" ", "") #remove spaces
				self.vars[var] = line.split(",") #finally we have our values
			
			#otherwise we are going to get either a distribution or a CPT
			elif line.startswith("probability"):
				line = line[line.index("(") + 1: line.index(")")]
				line = line.replace(" ", "")

				if "|" not in line: #not a conditional
					var = line
					self.parents[var] = []
					line = f.next()
					line = line.replace("table", "").replace(";", "").replace(",", "").split()
					self.roots[var] = [float(x) for x in line]
					self.CPTs[var] = {}
					self.CPTs[var][()] = [float(x) for x in line]

				else: #the variables is a conditional
					line = line.split("|")
					self.parents[line[0]] = line[1].split(",") #add the variable to the parents dict
					var = line[0]
					self.CPTs[var] = {}

					#now we read in the CPT
					line = f.next()
					while not line.startswith("}"):
						line = line.replace(" ", "").replace(";", "")
						line = [ line[line.index("(") + 1: line.index(")")], line[line.index(")") + 1:] ] #get the two parts of the line
						self.CPTs[var][tuple(line[0].split(","))] = [float(x) for x in line[1].split(",")]
						line = f.next()

	def __str__(self):
		string = ""
		#string += "vars: {}\n".format(self.vars.keys())

		#print the roots and root probs
		for r in self.roots:
			string += "{}: {}\n".format(r, self.roots[r])
			string += "\n"

		#print the conditional probs
		for var in self.CPTs:
			string += "{} | {}\n".format(var, tuple(self.parents[var]))
			for tup in self.CPTs[var]:
				string += "\t{}:\t{}\n".format(tup, self.CPTs[var][tup])
			string += "\n"

		return string

	#input: a variable, and a list of values for the parents of this variable.
	#output: an array of probabilities for each value the variable can take on.
	def CPT(var, parent_vals):
		return self.CPTs[var][tuple(parent_vals)]


class Factor():
	def __init__(self, BN, var):
		self.vars = [var] + BN.parents[var]
		self.funct = lambda args : BN.CPTs[var][tuple(args[1:])][BN.vars[var].index(args[0])]

	def __str__(self):
		return "P({}|{})".format(self.vars[0], self.vars[1:])


a = BNet("sprinkler.bif")
b = Factor(a, "WetGrass")