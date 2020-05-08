#!/bin/env python3
import re,sys,os,argparse
from pdb import set_trace

args = argparse.ArgumentParser()
args.add_argument('log', type=str,default="")
args.add_argument('-p', "--phrase", type=str,default="detv3", choices=["detv3","class","seg"])
args.add_argument('-c', "--column", type=int,default=20)
args.add_argument('-b', "--burn_in",type=int,default=1)
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
with open(filename) as f:
    for l in f:
        w = l.strip().split()
        if len(w)==0:continue

        m = re.search(reg,l.strip())

        if m is None or len(m.groups())<2:continue
        iter2avg.append(float(m.groups()[1]))

N=len(iter2avg)
if N<args.burn_in:
    print("Not enough log length")
    sys.exit(-1)
Offset=int(N/args.column)
maximumj = max(iter2avg[args.burn_in:])
minimumj = min(iter2avg[args.burn_in:])
minimumi = [i for i,loss in enumerate(iter2avg) if loss == minimumj][0]
assert minimumj > 0.0

#
# show results
#
for i,loss in enumerate(iter2avg):
    if i%Offset != 0 or i == 0: continue
    sys.stdout.write("{:10d} {:12.6f} ".format(i,loss))
    for _ in range(int(loss*((maximumj-minimumj)/args.column))):
        sys.stdout.write('#')
    print('')
sys.stdout.write("MIN {:6d} {:12.6f} ".format(minimumi,minimumj))
for _ in range(int(minimumj*((maximumj-minimumj)/args.column))):
    sys.stdout.write('>')
print('')

