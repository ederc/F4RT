#!/usr/bin/python

import sys
import fnmatch
import os
import shutil
import argparse
from argparse import RawTextHelpFormatter
import time
import math
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import pylab as pl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

# generates a 10 digit hash value from the current date and time
# to append to the already existing ".singularrc" filename in order
# to restore it later on
def hash():
  return '{0:010x}'.format(int(time.time() * 256))[:10]

# gets number of lines in a given text file
def linesinfile(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
  
currentdir = os.getcwd()

parser = argparse.ArgumentParser(description='\
Generates two random matrices a and b with either float\n\
or uint16 entries. these matrices are then multiplied,\n\
thus it is enough to predefine #rows of a, #cols of a\n\
and #cols of b. The multiplication is performed in various\n\
combinations of the f4rt dense matrix multiplication\n\
implementation. afterwards the stored results are visualized.',
formatter_class=RawTextHelpFormatter)
parser.add_argument('-a','--alg', required=True,
    help="What algorithm should be benchmarked:\n\
1 = Matrix multiplication\n\
2 = Naive Gaussian Elimination with pivoting\n\
3 = Naive Gaussian Elimination without pivoting\n\
4 = Cache-oblivious Gaussian Elimination without pivoting")
parser.add_argument('-b', '--base', default=2,
    help='base of number of threads, e.g. -b 2 -t 16\n\
would lead to computations in 1,2,4,8,16\n\
threads. Default is 2.')
parser.add_argument('-c', '--count', default=10,
    help='If doing Gaussian Elimination and the option "-i" is\n\
set, then the benchmarking is done on increasing matrix\n\
sizes. Thus it works only with the number of threads set\n\
by option "-t", but increases the row resp. column number\n\
by the value given for i. The increasing is done "-c" times.\n\
By default this value is 10.')
parser.add_argument('-i', '--inc', default=0,
    help='If doing Gaussian Elimination and this option is\n\
set, then the benchmarking is done on increasing matrix\n\
sizes. Thus it works only with the number of threads set\n\
by option "-t", but increases the row resp. column number\n\
by the value given for i. The increasing is done 10 times.')
parser.add_argument('-l', '--rowsa', required=True,
    help='number of rows of matrix a')
parser.add_argument('-m', '--colsa', required=True,
    help='number of cols of matrix a')
parser.add_argument('-n', '--colsb', default=0,
    help='number of cols of matrix b')
parser.add_argument('-p', '--plot', action='store_true',
    help='plotting of results? (default=0)')
parser.add_argument('-s', '--startthreads', default=1,
    help='start of number of threads to be used')
parser.add_argument('-t', '--threads', required=True,
    help='maximal number of threads to be used')

args = parser.parse_args()

# handle error if multiplication shall be done but only two dimensions are
# given:
algorithm = ''
if int(args.alg) == 1:
  algorithm = 'M'
  if args.colsb == 0:
    args.colsb = args.rowsa
if int(args.alg) == 2:
  algorithm = 'E -w'
if int(args.alg) == 3:
  algorithm = 'E'
if int(args.alg) == 4:
  algorithm = 'E -c'

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
if int(args.alg) == 1:
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
if int(args.alg) == 2 or int(args.alg) == 3:
  if start_threads == 1:
    methods = ['Raw sequential','pThread 1D','Open MP collapse(1) outer loop',
    'KAAPIC 1D','Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
    'Intel TBB 1D simple partitioner']
  else :
    methods = ['pThread 1D','Open MP collapse(1) outer loop',
    'KAAPIC 1D','Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
    'Intel TBB 1D simple partitioner']
  
if int(args.alg) == 4:
  if start_threads == 1:
    methods = ['Raw sequential','pThread 1D','Open MP parallel sections',
    'KAAPIC 1D','Intel TBB Invoke']
  else :
    methods = ['pThread 1D','Open MP parallel sections',
    'KAAPIC 1D','Intel TBB Invoke']

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

# generate random matrices without timestamp if no increasing is done
if int(args.inc) == 0:
  if int(args.alg) == 1:
    os.system('../../src/f4rt -G -R '+args.rowsa+' -C '+args.colsa)
    os.system('../../src/f4rt -G -R '+args.colsa+' -C '+args.colsb)
  else :
    os.system('../../src/f4rt -G -R '+args.rowsa+' -C '+args.colsa)

  bench_file = "bench-"+str(hash_value)
  f = open(bench_file,"w")

  strstr = '../../src/f4rt -'+algorithm+' \
  -A random-mat-'+args.rowsa+'-'+args.colsa+'.mat '
  if int(args.alg) == 1:
    strstr += '-B random-mat-'+args.colsa+'-'+args.colsb+'.mat'

  thrds_str = str(threads)
  thrds_str = thrds_str.replace('[','')
  thrds_str = thrds_str.replace(']','')
  thrds_str = thrds_str
  if int(args.alg) == 1:
    f.write(args.rowsa+','+args.colsa+','+args.colsb+'\r\n')
  else :
    f.write(args.rowsa+','+args.colsa+'\r\n')
  f.write(thrds_str+'\r\n')
  f.close()

  # sequential computation, only if start_threads == 1
  if start_threads == 1:
    print(strstr+' -m0 >> '+bench_file+'...')
    os.system(strstr+' -m0 >> '+bench_file)
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # pThread computations 1D outer
  block = 512
  j = 0
  for i in threads:
    block = max(block - j * 64,16)
    j = j+1
    print(strstr+' -m4 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m4 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # OpenMP computations 1D outer
  block = 512
  j = 0
  for i in threads:
    block = max(block - j * 64,16)
    j = j+1
    print(strstr+' -m1 -d 1 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m1 -d 1 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  if int(args.alg) == 1:
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
  block = 512
  j = 0
  for i in threads:
    block = max(block - j * 64,16)
    j = j+1
    print('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value)+'...')
    os.system('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  if int(args.alg) == 1:
    # KAAPIC computations 2D
    for i in threads:
      print('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -d2 -t '+str(i)+' >> bench-'+str(hash_value)+'...')
      os.system('KAAPI_CPUCOUNT='+str(i)+' '+strstr+' -m3 -d2 -t '+str(i)+' >> bench-'+str(hash_value))
      print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # TBB computations 1D auto
  block = 272
  j = 0
  for i in threads:
    block = max(block - j * 64,16)
    j = j+1
    print(strstr+' -m2 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m2 -t '+str(i)+' -b'+str(block)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  if int(args.alg) != 4:
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

  if int(args.alg) == 1:
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

# generate 10 random matrices without timestamp if increasing is done
# works only for GEP
else:
  for k in range(0,int(args.count)+1):
    rows = int(args.rowsa) + k * int(args.inc)
    cols = int(args.colsa) + k * int(args.inc)
    os.system('../../src/f4rt -G -R '+str(rows)+' -C '+str(cols))

  bench_file = "bench-"+str(hash_value)
  f = open(bench_file,"w")

  thrds_str = str(threads)
  thrds_str = thrds_str.replace('[','')
  thrds_str = thrds_str.replace(']','')
  thrds_str = thrds_str

  f.write(args.rowsa+','+args.colsa+','+args.inc+'\r\n')
  f.write(thrds_str+'\r\n')
  f.close()

  # sequential computation, only if max_threads == 1
  if int(max_threads) == 1:
    for k in range(0,int(args.count)+1):
      rows = int(args.rowsa) + k * int(args.inc)
      cols = int(args.colsa) + k * int(args.inc)
      strstr = '../../src/f4rt -'+algorithm+' \
      -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

      print(strstr+' -m0 >> '+bench_file+'...')
      os.system(strstr+' -m0 >> '+bench_file)
      print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # pThread computations 1D outer
  for k in range(0,int(args.count)+1):
    rows = int(args.rowsa) + k * int(args.inc)
    cols = int(args.colsa) + k * int(args.inc)
    strstr = '../../src/f4rt -'+algorithm+' \
    -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

    print(strstr+' -m4 -t '+str(max_threads)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m4 -t '+str(max_threads)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # OpenMP computations 1D outer
  for k in range(0,int(args.count)+1):
    rows = int(args.rowsa) + k * int(args.inc)
    cols = int(args.colsa) + k * int(args.inc)
    strstr = '../../src/f4rt -'+algorithm+' \
    -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

    print(strstr+' -m1 -d 1 -t '+str(max_threads)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m1 -d 1 -t '+str(max_threads)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # KAAPIC computations 1D
  for k in range(0,int(args.count)+1):
    rows = int(args.rowsa) + k * int(args.inc)
    cols = int(args.colsa) + k * int(args.inc)
    strstr = '../../src/f4rt -'+algorithm+' \
    -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

    print('KAAPI_CPUCOUNT='+str(max_threads)+' '+strstr+' -m3 -t '+str(max_threads)+' >> bench-'+str(hash_value)+'...')
    os.system('KAAPI_CPUCOUNT='+str(max_threads)+' '+strstr+' -m3 -t '+str(max_threads)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  # TBB computations 1D auto
  for k in range(0,int(args.count)+1):
    rows = int(args.rowsa) + k * int(args.inc)
    cols = int(args.colsa) + k * int(args.inc)
    strstr = '../../src/f4rt -'+algorithm+' \
    -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

    print(strstr+' -m2 -t '+str(max_threads)+' >> bench-'+str(hash_value)+'...')
    os.system(strstr+' -m2 -t '+str(max_threads)+' >> bench-'+str(hash_value))
    print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

  if int(alg.args) != 4:
    # TBB computations 1D affinity
    for k in range(0,int(args.count)+1):
      rows = int(args.rowsa) + k * int(args.inc)
      cols = int(args.colsa) + k * int(args.inc)
      strstr = '../../src/f4rt -'+algorithm+' \
      -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

      print(strstr+' -m2 -t '+str(max_threads)+' -a >> bench-'+str(hash_value)+'...')
      os.system(strstr+' -m2 -t '+str(max_threads)+' -a >> bench-'+str(hash_value))
      print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

    # TBB computations 1D simple
    for k in range(0,int(args.count)+1):
      rows = int(args.rowsa) + k * int(args.inc)
      cols = int(args.colsa) + k * int(args.inc)
      strstr = '../../src/f4rt -'+algorithm+' \
      -A random-mat-'+str(rows)+'-'+str(cols)+'.mat '

      print(strstr+' -m2 -t '+str(max_threads)+' -s >> bench-'+str(hash_value)+'...')
      os.system(strstr+' -m2 -t '+str(max_threads)+' -s >> bench-'+str(hash_value))
      print 'Done at '+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())


##############################################
# plotting part of the script
##############################################


if args.plot:
  file_name = 'bench-'+str(hash_value)
  # read lines of the benchmark files
  f = open(file_name)
  lines = f.readlines()
  f.close()

  # get
  # 1. dimensions of benchmark matrices
  # 2. threads for plot, stored in the first line of bench file
  dimensions = lines[0].strip().replace(' ','').split(',')
  
  if int(args.inc) == 0:
    # second line are the thread settings used
    plot_threads = lines[1].strip().replace(' ','').split(',')
  else:
    # if inc is set we cheat a bit and still use plot_threads and threads thus we
    # do not need to change the code for the plotting below:
    # There are 10 increasements of the sizes, that means, we have 11 values:
    plot_threads = []
    for k in range(0,int(args.count)+1):
      plot_threads.append(str(k))

  # get threads for plot, stored in the first line of bench file
  #plot_threads = f.readline().strip().replace(' ','').split(',')
  # for compatibility to the other scripts just store this again
  threads = plot_threads
  threads = list(map(lambda x: int(x) - 1, threads))


  for l in lines:
    for i in range(0,len(methods)):  
      if l.find(methods[i]) != -1:
        tmp = i
    if l.find('Real time:') != -1:
      time_series[tmp].append(\
          l.replace('Real time:','').replace('sec','').strip())
    if l.find('GFLOPS/sec:') != -1:
      # if the value is inf for infinity due to short computation time, we set
      # the GFLOPS value to be -1
      gflops_series[tmp].append(\
          l.replace('GFLOPS/sec:','').replace('inf','-1').strip())

  #plot this data

  #line style, sequential method only if start_threads == 1
  if int(args.alg) == 1:
    if start_threads == 1:
      stride = 1
      coloring = ['k','c','b','b','g','y','y','#7d053f','#7d053f','#7d053f','r','r','r']
      styles = ['None','-','-','--','-','-','-','-','--',':','-','--',':']
      markers = ['^','None','None','None','None','o','s','None','None',
        'None','None','None','None']
    else:
      stride = 1
      coloring = ['c','b','b','g','y','y','#7d053f','#7d053f','#7d053f','r','r','r']
      styles = ['-','-','--','-','-','-','-','--',':','-','--',':']
      markers = ['None','None','None','None','o','s','None','None',
        'None','None','None','None']
  if int(args.alg) == 2 or int(args.alg) == 3:
    if start_threads == 1:
      stride = 1
      coloring = ['k','c','b','y','#7d053f','#7d053f','#7d053f']
      styles = ['None','-','-','-','-','--',':']
      markers = ['^','None','None','o','None','None',
        'None']
    else:
      stride = 1
      coloring = ['c','b','y','#7d053f','#7d053f','#7d053f']
      styles = ['-','-','-','-','--',':']
      markers = ['None','None','o','None','None',
        'None']
  if int(args.alg) == 4:
    if start_threads == 1:
      stride = 1
      coloring = ['k','c','b','y','#7d053f']
      styles = ['None','-','-','-','-']
      markers = ['^','None','None','o','None']
    else:
      stride = 1
      coloring = ['c','b','y','#7d053f']
      styles = ['-','-','-','-']
      markers = ['None','None','o','None']

  pl.rc('legend',**{'fontsize':5})
  fig = pl.figure()
  ax = fig.add_subplot(111)
  fig.suptitle('Timings: '+file_name, fontsize=10)
  if int(args.alg) == 1:
    pl.title('Mat Mult uint64 Matrix dimensions: '+dimensions[0]+
    ' x '+dimensions[1]+', '+dimensions[1]+' x '+dimensions[2], fontsize=8)
  if int(args.alg) == 2 or int(args.alg) == 3:
    if int(args.inc) == 0:
      pl.title('Naive GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1], fontsize=8)
    else:
      pl.title('Naive GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1]+' increasing by '+dimensions[2]+' in each step using '+
      str(max_threads)+' threads', fontsize=8)
  if int(args.alg) == 4:
    if int(args.inc) == 0:
      pl.title('Cache-oblivious GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1], fontsize=8)
    else:
      pl.title('Cache-oblivious GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1]+' increasing by '+dimensions[2]+' in each step using '+
      str(max_threads)+' threads', fontsize=8)
  if int(args.inc) == 0:
    ax.set_xlabel('Number of threads', fontsize=7)
  else:
    ax.set_xlabel('Number of increasing steps', fontsize=7)
  ax.set_ylabel('Real time in seconds', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  group_labels = plot_threads

  #ax.set_xticklabels(group_labels)
  threads_tmp = range(0,len(plot_threads))
  # get right scale for a4 paper size
  scale_tmp = 38 / (len(plot_threads)) 
  threads = range(0,38,scale_tmp)
  tick_lbs = plot_threads
  ax.xaxis.set_ticks(threads)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methods)
  for i in range(0,len(methods)):
    p[i], = ax.plot(threads[0:len(time_series[i])], time_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize='4', label=i)
  # set 0 as min value for y and 1 as min value for x (threads)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0)
  if int(args.inc) == 0:
    ax.legend((methods),'upper right', shadow=True, fancybox=True)
  else:
    ax.legend((methods),'lower right', shadow=True, fancybox=True)

  # take real time of sequential computation to figure out the 
  # granularity of the yaxis
  tmp_ticks = ax.yaxis.get_majorticklocs()
  granu = tmp_ticks[len(tmp_ticks)-1] / (len(tmp_ticks)-1) / 5
  ax.yaxis.set_minor_locator(MultipleLocator(granu))
  pl.tick_params(axis='both', which='major', labelsize=6)
  pl.tick_params(axis='both', which='minor', labelsize=6)

  pl.savefig('timings-plot.pdf',papertype='a4',orientation='landscape')

  fig = pl.figure()
  ax = fig.add_subplot(111)
  fig.suptitle('GFLOPS/sec: '+file_name, fontsize=10)
  if int(args.alg) == 1:
    pl.title('Mat Mult uint64 Matrix dimensions: '+dimensions[0]+
    ' x '+dimensions[1]+', '+dimensions[1]+' x '+dimensions[2], fontsize=8)
  if int(args.alg) == 2 or int(args.alg) == 3:
    if int(args.inc) == 0:
      pl.title('Naive GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1], fontsize=8)
    else:
      pl.title('Naive GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1]+' increasing by '+dimensions[2]+' in each step using '+
      str(max_threads)+' threads', fontsize=8)
  if int(args.alg) == 4:
    if int(args.inc) == 0:
      pl.title('Cache-oblivious GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1], fontsize=8)
    else:
      pl.title('Cache-oblivious GEP uint64 Matrix dimensions: '+dimensions[0]+
      ' x '+dimensions[1]+' increasing by '+dimensions[2]+' in each step using '+
      str(max_threads)+' threads', fontsize=8)
  if int(args.inc) == 0:
    ax.set_xlabel('Number of threads', fontsize=7)
  else:
    ax.set_xlabel('Number of increasing steps', fontsize=7)
  ax.set_ylabel('GFLOPS per second', fontsize=8)

  pl.grid(b=True, which='major', color='k', linewidth=0.3)
  pl.grid(b=True, which='minor', color='k', linewidth=0.1, alpha=0.5)

  ax = pl.gca() 

  #ax.set_xticklabels(group_labels)
  threads_tmp = range(0,len(plot_threads))
  # get right scale for a4 paper size
  scale_tmp = 38 / (len(plot_threads)) 
  threads = range(0,38,scale_tmp)
  tick_lbs = plot_threads
  ax.xaxis.set_ticks(threads)
  ax.xaxis.set_ticklabels(tick_lbs)

  p = [None]*len(methods)
  for i in range(0,len(methods)):
    p[i], = ax.plot(threads[0:len(gflops_series[i])], gflops_series[i], c=coloring[i],
        ls=styles[i], marker=markers[i], markersize='4', label=i)
  # set 0 as min value for y and 1 as min value for x (threads)
  #pl.xlim(xmin=1)
  pl.ylim(ymin=0)
  if int(args.inc) == 0:
    ax.legend((methods),'upper left', shadow=True, fancybox=True)
  else:
    ax.legend((methods),'lower right', shadow=True, fancybox=True)

  # take gflops of best computation to figure out the 
  # granularity of the yaxis
  tmp_ticks = ax.yaxis.get_majorticklocs()
  # note that here "abs()" is needed since if computations are too fast we
  # set GFLOPS to -1 instead of infinity. Since the MultipleLocator must
  # be set to a positive integer value, we have to take care of this case.
  granu = abs(tmp_ticks[len(tmp_ticks)-1]) / (len(tmp_ticks)-1) / 5
  ax.yaxis.set_minor_locator(MultipleLocator(granu))

  pl.tick_params(axis='both', which='major', labelsize=6)
  pl.tick_params(axis='both', which='minor', labelsize=6)

  pl.savefig('gflops-plot.pdf',papertype='a4',orientation='landscape')
