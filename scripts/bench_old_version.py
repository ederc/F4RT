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
parser.add_argument('-n', '--colsb', default=0,
    help='Number of cols of matrix B')
parser.add_argument('-s', '--startthreads', default=1,
    help='start of number of threads to be used')
parser.add_argument('-t', '--threads', required=True,
    help='Maximal number of threads to be used')
parser.add_argument('-b', '--base', default=2,
    help='Base of number of threads, e.g. -b 2 -t 16 would lead to computations\
in 1,2,4,8,16 threads. Default is 2.')
parser.add_argument('-a','--alg', required=True,
    help='What algorithm should be benchmarked:\r\n\
1 = Matrix multiplication\r\n\
2 = Gaussian Elimination')

args = parser.parse_args()

# handle error if multiplication shall be done but only two dimensions are
# given:
algorithm = ''
if int(args.alg) == 1:
  algorithm = 'M'
  if args.colsb == 0:
    args.colsb = args.rowsa
else:
  algorithm = 'E'

# range of threads
threads = list()
exp = 0
max_threads = int(args.threads)
start_threads = int(args.startthreads)
base = int(args.base)
if base == 1:
  while (start_threads) <= max_threads:
    threads.append(start_threads)
    start_threads += 1
else:
  while start_threads > (base**exp):
    exp += 1
  while (base**exp) <= max_threads:
    threads.append(base**exp)
    exp += 1

# list of all methods, sequential only if start_threads == 1
if start_threads == 1:
  methods = ['Raw sequential','pThread 1D','Open MP collapse(1) outer loop',
  'Open MP collapse(1) inner loop','Open MP collapse(2)',
  'KAAPIC 1D','KAAPIC 2D',
  'Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
  'Intel TBB 1D simple partitioner','Intel TBB 2D auto partitioner',
  'Intel TBB 2D affinity partitioner','Intel TBB 2D simple partitioner']
else :
  methods = ['pThread 1D','Open MP collapse(1) outer loop',
  'Open MP collapse(1) inner loop','Open MP collapse(2)',
  'KAAPIC 1D','KAAPIC 2D',
  'Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
  'Intel TBB 1D simple partitioner','Intel TBB 2D auto partitioner',
  'Intel TBB 2D affinity partitioner','Intel TBB 2D simple partitioner']

# lists for all methods we have, those are lists of lists:
# e.g. time_series[i] is a list of len(threads) elements of the timings
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
os.system('../../src/f4rt -G -R '+args.rowsa+' -C '+args.colsa)
os.system('../../src/f4rt -G -R '+args.colsa+' -C '+args.colsb)

bench_file = "bench-"+str(hash_value)
f = open(bench_file,"w")

strstr = '../../src/f4rt -'+algorithm+' \
-A random-float-mat-'+args.rowsa+'-'+args.colsa+'.mat \
-B random-float-mat-'+args.colsa+'-'+args.colsb+'.mat'

thrds_str = str(threads)
thrds_str = thrds_str.replace('[','')
thrds_str = thrds_str.replace(']','')
thrds_str = thrds_str
f.write(args.rowsa+','+args.colsa+','+args.colsb+'\r\n')
f.write(thrds_str+'\r\n')
f.close()

# sequential computation, only if start_threads == 1
if start_threads == 1:
  print(strstr+' -m0 >> '+bench_file+'...')
  os.system(strstr+' -m0 >> '+bench_file)
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# pThread computations 1D outer
for i in threads:
  print(strstr+' -m4 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m4 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# OpenMP computations 1D outer
for i in threads:
  print(strstr+' -m1 -d 1 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m1 -d 1 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# OpenMP computations 1D inner
for i in threads:
  print(strstr+' -m1 -d 1 -i -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m1 -d 1 -i -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# OpenMP computations 2D
for i in threads:
  print(strstr+' -m1 -d 2 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m1 -d 2 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# KAAPIC computations 1D
for i in threads:
  print('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# KAAPIC computations 2D
for i in threads:
  print('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -d2 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -d2 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D auto
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D affinity
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' -a >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' -a >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 1D simple
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' -s >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' -s >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D auto
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' -d 2 >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' -d 2 >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D affinity
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' -d 2 -a >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' -d 2 -a >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# TBB computations 2D simple
for i in threads:
  print(strstr+' -m2 -t '+str(i)+' -d 2 -s >> bench-'+str(hash_value)+'...')
  os.system(strstr+' -m2 -t '+str(i)+' -d 2 -s >> bench-'+str(hash_value))
  print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
