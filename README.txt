This is a program that reads in a .bif (Bayesian Interchange Format) file representing a bayesian network
and it performs some number of rounds (until convergence) of the sum-product algorithm to find the marginals
of all variables. Then it writes those marginals into a results file.

To use the program you only need to run

python SumProduct.py [filename]

with filename in the same directory. You will then find the results in filename-results.txt