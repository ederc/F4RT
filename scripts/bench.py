#!/usr/bin/python

import sys
import fnmatch
import os
import shutil
import argparse
import time
import math

# generates a 10 digit hash value from the current date and time
# to append to the already existing ".singularrc" filename in order
# to restore it later on
def hash():
  return '{0:010x}'.format(int(time.time() * 256))[:10]

# gets number of lines in a given text file
def linesInFile(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
  
currentdir = os.getcwd()

parser = argparse.ArgumentParser(description='Generates two random matrices\
A and B with float entries. These matrices are then multiplied, thus it\
is enough to predefine #rows of A, #cols of A and #cols of B. The\
multiplication is performed in various combinations of the F4RT dense\
matrix multiplication implementation. Afterwards the stored results\
are visualized.')
parser.add_argument('-l', '--rowsa', required=True,
    help='Number of rows of matrix A')
parser.add_argument('-m', '--colsa', required=True,
    help='Number of cols of matrix A')
parser.add_argument('-n', '--colsb', required=True,
    help='Number of cols of matrix B')
parser.add_argument('-t', '--threads', required=True,
    help='Maximal number of threads to be used')
parser.add_argument('-b', '--base', default=1,
    help='Base of number of threads, e.g. -b 2 -t 16 would lead to computations\
in 1,2,4,8,16 threads.')
parser.add_argument('-hg', '--homog', action="store_true", default=False,
    help='Set this flag if the ideal should be homogenized.\
Note that this flag increases the number of variables by 1.')

args = parser.parse_args()

# range of threads
threads = list()
exp = 0
max_threads = int(args.threads)
base = int(args.base)
if base == 1:
  while (base) <= max_threads:
    threads.append(base)
    base += 1
else:
  while (base**exp) <= max_threads:
    threads.append(base**exp)
    exp += 1

# list of all methods
methods = ['Raw sequential','Open MP collapse(1)','Open MP collapse(2)',
'Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
'Intel TBB 1D simple partitioner','Intel TBB 2D auto partitioner',
'Intel TBB 2D affinity partitioner','Intel TBB 2D simple partitioner']

coloring = ['k-','b--','b-.','g--','g-.','g:','r--','r-.','r:']
# lists for all methods we have, those are lists of lists:
# E.g. time_series[i] is a list of len(threads) elements of the timings
# of methods[i]. 
time_series = list()
gflops_series = list()

for i in range(0,len(methods)):
  time_series.append(list())
  gflops_series.append(list())

# generate hash value if needed
hash_value = os.urandom(16).encode('hex')

folder_name = "test-"+str(hash_value)

if not os.path.exists(folder_name):
  os.makedirs(folder_name)

os.chdir(os.getcwd()+"/"+folder_name)

#generate random matrices without timestamp
os.system('../../src/dense-mult -g -R '+args.rowsa+' -C '+args.colsa)
os.system('../../src/dense-mult -g -R '+args.colsa+' -C '+args.colsb)

bench_file = "bench-"+str(hash_value)
f = open(bench_file,"w")

strstr = '../../src/dense-mult -c \
-A random-float-mat-'+args.rowsa+'-'+args.colsa+'.mat \
-B random-float-mat-'+args.colsa+'-'+args.colsb+'.mat'

thrds_str = str(threads)
thrds_str = thrds_str.replace('[','')
thrds_str = thrds_str.replace(']','')
thrds_str = thrds_str
f.write(thrds_str+'\n')
f.close()

# sequential computation
print(strstr+' -i -m 2 >> '+bench_file+'...')
os.system(strstr+' -i -m 2 >> '+bench_file)
print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# OpenMP computations 1D
for i in threads:
  print(strstr+' -i -m 1 -d 1 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 1 -d 1 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# OpenMP computations 2D
for i in threads:
  print(strstr+' -i -m 1 -d 2 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 1 -d 2 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D auto
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D affinity
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' -a >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' -a >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D simple
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' -s >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' -s >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D auto
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' -d 2 >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' -d 2 >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D affinity
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' -d 2 -a >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' -d 2 -a >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D simple
for i in threads:
  print(strstr+' -i -m 0 -t '+str(i)+' -d 2 -s >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -i -m 0 -t '+str(i)+' -d 2 -s >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())