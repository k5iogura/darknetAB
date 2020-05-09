#!/bin/env python3
import re,sys,os,argparse
from math import ceil
from pdb import set_trace

args = argparse.ArgumentParser()
args.add_argument('log', type=str)
args.add_argument('-p', "--phrase",   type=str,default="detv3", choices=["detv3","class","seg"])
args.add_argument('-c', "--column",   type=int,default=20)
args.add_argument('-b', "--burn_in",  type=int,default=1)
args.add_argument('-s', "--stop_iter",type=int,default=1000000)
args = args.parse_args()
filename=args.log

#
# setup searching phrase in log files
# append phrase for new log format
#
if args.phrase == "detv3":
    reg = '([0-9]+):.* +([0-9.]+) *avg'
else:
    print(args.phrase, "Not suported")
    sys.exit(-1)
print('phrase to search iteration and loss:',reg)

#
# analyzing
#
iter2avg = [0]
iters = 0
with open(filename) as f:
    for l in f:
        w = l.strip().split()
        if len(w)==0:continue

        m = re.search(reg,l.strip())

        if m is None or len(m.groups())<2:continue
        iter2avg.append(float(m.groups()[1]))
        if iters>args.stop_iter:break
        iters+=1

N=len(iter2avg)
if N<args.burn_in:
    print("Not enough log length")
    sys.exit(-1)
Offset=int(N/args.column)
maximumj = max(iter2avg[args.burn_in:])
minimumj = min(iter2avg[args.burn_in:])
minimumi = [i for i,loss in enumerate(iter2avg) if loss == minimumj][0]
print('loss range:',maximumj,'to',minimumj)
assert minimumj > 0.0

#
# show results
#
print("-"*107)
print("|{:>11s} {:>12s} {:^80s}|".format("iteration","loss","bar"))
print("-"*107)
for i,loss in enumerate(iter2avg):
    if i%Offset != 0 or i == 0: continue
    sys.stdout.write("{:12d} {:12.6f} ".format(i,loss))
    for j in range(ceil(loss*((maximumj-minimumj)/args.column))):
        if j > 80:continue
        if j == 80:
            sys.stdout.write('|')
        else:
            sys.stdout.write('#')
    print('')
print("-"*107)
sys.stdout.write("MIN {:8d} {:12.6f} ".format(minimumi,minimumj))
for j in range(int(minimumj*((maximumj-minimumj)/args.column))):
    if j > 80:break
    sys.stdout.write('>')
print('')
print("-"*107)

