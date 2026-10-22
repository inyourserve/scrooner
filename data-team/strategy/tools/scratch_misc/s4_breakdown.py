import csv,collections,sys
d=sys.argv[1]
grp={r['company_id']:r for r in csv.DictReader(open(d+'/group_assignment_draft.csv'))}
cnt=collections.Counter(); bygrp=collections.defaultdict(collections.Counter); gtot=collections.Counter()
dpall=collections.Counter(); dpval=collections.Counter()
rows=[]
for r in csv.DictReader(open(d+'/cohort_cells.csv')):
    dpall[r['data_point_name']]+=1
    if r['has_value']=='t': dpval[r['data_point_name']]+=1
    if r['has_value']=='f' and r['gap_reason']=='':
        g=grp.get(r['company_id'],{}).get('group','?')
        cnt[r['data_point_name']]+=1; bygrp[r['data_point_name']][g]+=1; gtot[g]+=1
        rows.append((r['company_id'],r['data_point_name'],g))
print('total',sum(cnt.values()),'datapoints',len(cnt)); print('groups',dict(gtot))
gs=['corporate','bank','reit','insurer','other_financial']
gs+= [g for g in gtot if g not in gs]
print('rank,dp,noreason,cells,valued,'+','.join(gs))
cum=0
for i,(k,v) in enumerate(cnt.most_common()):
    cum+=v
    print(i+1,k,v,dpall[k],dpval[k],*[bygrp[k][g] for g in gs],'cum',cum,sep=',')
import pickle
pickle.dump(rows,open(sys.argv[2],'wb'))
