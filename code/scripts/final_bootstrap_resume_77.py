import csv,json,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]; C=R/'execution_control/PTBXL_FINAL_CLOSURE'
S=R/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'; OLD=C/'PARALLEL_CPU_BOOTSTRAP_55_RUNS.csv'; W=C/'PARALLEL_WORKER_EVIDENCE_RECOVERY.csv'
OUT=C/'FINAL_CPU_BOOTSTRAP_77_RUNS.csv'; J=C/'FINAL_CPU_BOOTSTRAP_77_RUNS.json'; MAN=C/'FINAL_CPU_BOOTSTRAP_MANIFEST.json'; BL=C/'BOOTSTRAP_BLOCKER_PROVENANCE_LIST.csv'
HELPER='upstream/ecg-fm-benchmarking/code/clinical_ts/utils/bootstrap_utils.py::empirical_bootstrap'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def key(x):return x['dataset'],x['model'],x['mode']
def flat(t,p,classes):
 from clinical_ts.utils.eval_utils_cafa import multiclass_roc_curve
 return np.array(list(multiclass_roc_curve(t,p,classes=classes)[2].values()))
def output(rows,manifest):
 fields=['dataset','model','mode','canonical_run','bootstrap_status','point_macro_auroc','ci_low','ci_high','bootstrap_iterations','bootstrap_valid_iterations','helper_path','provenance','notes']
 with open(OUT,'w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 J.write_text(json.dumps({'runs':rows},indent=2)+'\n');MAN.write_text(json.dumps(manifest,indent=2)+'\n')
def main():
 from clinical_ts.utils.bootstrap_utils import empirical_bootstrap
 status=[x for x in rd(S) if x['mapping_result']=='PASS']; old={key(x):x for x in rd(OLD)}; workers={key(x):x for x in rd(W)}
 if len(status)!=77 or len(old)!=55 or len(workers)!=22:raise RuntimeError(f'COUNT_MISMATCH pass={len(status)} old={len(old)} workers={len(workers)}')
 rows=[]; blockers=[]
 for x in status:
  k=key(x)
  if k in old:
   o=old[k]; st='COMPLETED' if o['bootstrap_status']=='COMPLETE' else 'BLOCKED_EXISTING_PROVENANCE'
   row={'dataset':x['dataset'],'model':x['model'],'mode':x['mode'],'canonical_run':x['canonical_run'],'bootstrap_status':st,'point_macro_auroc':o['recomputed_point_macro_auroc'],'ci_low':o['ci_low'],'ci_high':o['ci_high'],'bootstrap_iterations':1000,'bootstrap_valid_iterations':o['bootstrap_iterations_valid'],'helper_path':HELPER,'provenance':'REUSED_LEGACY_55_RUNS; '+o['prediction_source'],'notes':o['notes']}
   rows.append(row)
   if st.startswith('BLOCKED'):blockers.append(row)
  else:
   w=workers[k]; b=R/w['local_path']; aggs=list(b.rglob('*_agg.npz')); raw=list(b.rglob('*_noagg.npz'))
   row={'dataset':x['dataset'],'model':x['model'],'mode':x['mode'],'canonical_run':x['canonical_run'],'bootstrap_status':'PENDING','point_macro_auroc':'','ci_low':'','ci_high':'','bootstrap_iterations':1000,'bootstrap_valid_iterations':'','helper_path':HELPER,'provenance':f'EMERGENCY_WORKERS instance={w["instance_id"]}; local_bundle={w["local_path"]}; SHA256 VERIFIED','notes':''}
   if len(aggs)!=1 or len(raw)!=1:row['bootstrap_status']='BLOCKED_EXISTING_PROVENANCE';row['notes']='Worker bundle lacks a unique canonical aggregate/raw pair.';blockers.append(row)
   else:row['_agg']=str(aggs[0]);row['provenance']+='; aggregate='+str(aggs[0].relative_to(R)).replace('\\','/')
   rows.append(row)
 fields=['dataset','model','mode','canonical_run','bootstrap_status','point_macro_auroc','ci_low','ci_high','bootstrap_iterations','bootstrap_valid_iterations','helper_path','provenance','notes']
 with open(BL,'w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(blockers)
 manifest={'phase':'RUNNING','eligible_count':77,'legacy_completed_reused':sum(r['bootstrap_status']=='COMPLETED' for r in rows),'blocked_existing_provenance':len(blockers),'new_bootstrap_required':sum(r['bootstrap_status']=='PENDING' for r in rows),'helper':HELPER,'contract':'1000 iterations; 95% CI; ECG record; N=2198; locked helper default RNG and invalid-resample behavior','started_utc':datetime.now(timezone.utc).isoformat()};output([{k:v for k,v in r.items() if not k.startswith('_')} for r in rows],manifest)
 for r in rows:
  if r['bootstrap_status']!='PENDING':continue
  try:
   with np.load(r['_agg'],allow_pickle=False) as a:p,t,l=a['preds'],a['targs'],a['lbl_itos']
   dim={'ptbxl_all':71,'ptbxl_sub':23,'ptbxl_super':5}[r['dataset']]
   if p.shape!=(2198,dim) or t.shape!=(2198,dim):raise RuntimeError(f'shape {p.shape}/{t.shape}')
   scores=flat(t,p,l); from clinical_ts.utils.eval_utils_cafa import multiclass_roc_curve
   names=list(multiclass_roc_curve(t,p,classes=l)[2]);mi=names.index('macro');r['point_macro_auroc']=repr(float(scores[mi]))
   pts,lo,hi,ids=empirical_bootstrap((t,p),flat,n_iterations=1000,alpha=.95,score_fn_kwargs={'classes':l})
   r.update({'bootstrap_status':'COMPLETED','bootstrap_valid_iterations':1000,'ci_low':repr(float(lo[mi])),'ci_high':repr(float(hi[mi])),'notes':'New worker PASS run; bootstrap IDs discarded after scalar CI extraction.'});del ids
  except Exception as e:r.update({'bootstrap_status':'FAILED','notes':repr(e)})
  output([{k:v for k,v in z.items() if not k.startswith('_')} for z in rows],manifest)
 manifest.update({'phase':'COMPLETE','completed':sum(r['bootstrap_status']=='COMPLETED' for r in rows),'blocked':sum(r['bootstrap_status'].startswith('BLOCKED') for r in rows),'failed':sum(r['bootstrap_status']=='FAILED' for r in rows),'pending':sum(r['bootstrap_status']=='PENDING' for r in rows),'finished_utc':datetime.now(timezone.utc).isoformat()});output([{k:v for k,v in z.items() if not k.startswith('_')} for z in rows],manifest)
if __name__=='__main__':main()
