#!/usr/bin/python

import sys
import fnmatch
import os
import glob
import shutil
import argparse
import time
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import pylab as pl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

currentdir = os.getcwd()

parser = argparse.ArgumentParser(description='Visualizes already\
computed benchmarks from F4RT.')
parser.add_argument('-d', '--directory', required=True,
    help='Directory where the benchmark file is included.')

args = parser.parse_args()

# list of all methods
methods = ['Raw sequential','Open MP collapse(1) outer loop',
'Open MP collapse(1) inner loop','Open MP collapse(2)',
'Intel TBB 1D auto partitioner','Intel TBB 1D affinity partitioner',
'Intel TBB 1D simple partitioner','Intel TBB 2D auto partitioner',
'Intel TBB 2D affinity partitioner','Intel TBB 2D simple partitioner']

# lists for all methods we have, those are lists of lists:
# E.g. time_series[i] is a list of len(threads) elements of the timings
# of methods[i]. 
time_series = list()
gflops_series = list()

for i in range(0,len(methods)):
  time_series.append(list())
  gflops_series.append(list())

# go to directory
os.chdir(args.directory)

file_name = ''
# find bench file
for files in glob.glob("bench-*"):
  file_name = files

# read lines of the benchmark files
f = open(file_name)
lines = f.readlines()
f.close()

# get
# 1. dimensions of benchmark matrices
# 2. threads for plot, stored in the first line of bench file
dimensions = lines[0].strip().replace(' ','').split(',')
# second line are the thread settings used
plot_threads = lines[1].strip().replace(' ','').split(',')

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

#line style
coloring = ['k^','b-','b--','g-','m-','m--','m:','r-','r--','r:']

pl.rc('legend',**{'fontsize':5})
fig = pl.figure()
ax = fig.add_subplot(111)
fig.suptitle('Timings: '+file_name, fontsize=10)
pl.title('Matrix dimensions: '+dimensions[0]+
' x '+dimensions[1]+', '+dimensions[1]+' x '+dimensions[2], fontsize=8)
ax.set_xlabel('Number of threads', fontsize=7)
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
  p[i], = ax.plot(threads[0:len(time_series[i])], time_series[i], coloring[i], label=i)
# set 0 as min value for y and 1 as min value for x (threads)
#pl.xlim(xmin=1)
pl.ylim(ymin=0)
ax.legend((methods),'upper right', shadow=True, fancybox=True)

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
pl.title('Matrix dimensions: '+dimensions[0]+
' x '+dimensions[1]+', '+dimensions[1]+' x '+dimensions[2], fontsize=8)
ax.set_xlabel('Number of threads', fontsize=8)
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
  p[i], = ax.plot(threads[0:len(gflops_series[i])], gflops_series[i],coloring[i], label=i)
# set 0 as min value for y and 1 as min value for x (threads)
#pl.xlim(xmin=1)
pl.ylim(ymin=0)
ax.legend((methods),'upper left', shadow=True, fancybox=True)

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
