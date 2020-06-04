#!/usr/bin/env python3
import sys,os,json,argparse,re
from pycocotools.cocoeval import COCOeval
from pycocotools.coco import COCO
from io import StringIO
from pdb import set_trace

aliases={'couch':'sofa', 'motorcycle':'motorbike', 'tv':'tvmonitor','airplane':'aeroplane'}

def check(f):
    assert os.path.exists(f),'not found {}'.fotmat(f)
    return str(f)

args=argparse.ArgumentParser()
grp1=args.add_argument_group()
args.add_argument('-r',  '--result_json',         type=check, required=True, help='anywhere/coco_results.json')
args.add_argument('-g',  '--groundtruth_json',    type=check, required=True, help='anywhere/instance_val2014.json')
grp1.add_argument('-cnf','--category_names_file', type=check, default=None,  help='anywhere/voc.names')
grp1.add_argument('-cn', '--category_names',      type=str,   default=None,  nargs='+', help='anywhere/voc.names')
args=args.parse_args()

resf = args.result_json
cocoGt = COCO(args.groundtruth_json)
cocoDt = cocoGt.loadRes(resf)

evalCatNames=[]
evalCatIds=[]
if args.category_names_file is not None:
    with open(args.category_names_file) as f: evalCatNames=[i.strip() for i in f]
if args.category_names is not None:
    evalCatNames=args.category_names
if len(evalCatNames)>0:
    name2id={}
    with open(args.groundtruth_json) as f: gt=json.load(f)
    for i in gt['categories']:
        name,nid=i['name'],i['id']
        name2id[name]=nid
        if name in aliases.keys():
            alias_name=aliases[name]
            name2id[alias_name]=nid
        if re.search(' ',name) is not None:
            name=re.sub(' ','',name)
            name2id[name]=nid
    print("{}".format(sorted(list(set(name2id)))))
    del gt
    for name in evalCatNames:
        nid = name2id.get(name,None)
        if nid is None:
            print("specified category name {} is not in categories of {}".format(name,args.groundtruth_json))
            continue
        evalCatIds.append(nid)

with open(resf) as f:
    xx=json.load(f)
    ids=[i['image_id'] for i in xx]
    ids=sorted(list(set(ids)))

annType='bbox'
cocoEval = COCOeval(cocoGt, cocoDt, annType)
cocoEval.params.imgIds = ids
if len(evalCatIds)>0:cocoEval.params.catIds = evalCatIds
cocoEval.evaluate()
cocoEval.accumulate()

original_stdout = sys.stdout
string_stdout = StringIO()
sys.stdout = string_stdout
cocoEval.summarize()
sys.stdout = original_stdout

mean_ap = cocoEval.stats[0].item()  # stats[0] records AP@[0.5:0.95]
detail = string_stdout.getvalue()

print(mean_ap)
print(detail)
