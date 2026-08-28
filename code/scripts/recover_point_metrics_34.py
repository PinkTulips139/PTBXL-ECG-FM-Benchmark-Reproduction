import csv,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];C=R/'execution_control/PTBXL_FINAL_CLOSURE';S=R/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv';M=R/'tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv';OUTC=C/'POINT_METRIC_PROVENANCE_RECOVERY_34.csv';OUTJ=C/'POINT_METRIC_PROVENANCE_RECOVERY_34.json'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def metric(t,p,l):
 from clinical_ts.utils.eval_utils_cafa import multiclass_roc_curve
 return float(list(multiclass_roc_curve(t,p,classes=l)[2].values())[-1])
def find(row):
 run=row['canonical_run']; roots=[C/'mapping_evidence/instance_451'/run,C/'mapping_evidence/instance_780'/run,C/'mapping_evidence/instance_775'/run]
 res=rd(C/'PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv') if (C/'PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv').exists() else []
 for x in res:
  if x['dataset'].lower().replace('ptb-xl','ptbxl').replace('(','_').replace(')','')==row['dataset'] and x['model']==row['model'] and x['mode']==row['mode']:roots.append(R/x['local_bundle_path'])
 if run=='PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015':roots.append(C/'mapping_evidence/instance_451/PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015_RETRY_01')
 for d in roots:
  if d.exists():
   a=list(d.rglob('*_agg.npz'));n=list(d.rglob('*_noagg.npz'))
   if len(a)==1 and len(n)==1:return a[0],n[0]
 # Original all Finetuning PASS use unique model-scoped archived aggregate/noagg pair.
 if row['dataset']=='ptbxl_all' and row['mode']=='Finetuning':
  slug={'ECGFounder':'ecgfounder','ECG-JEPA':'ecg_jepa','ST-MEM':'st_mem','MERL':'merl','ECGFM-KED':'ecgfm_ked','HuBERT-ECG':'hubert_ecg','ECG-CPC':'ecg_cpc','ECG-FM':'ecg_fm','S4':'s4','Net1D':'net1d'}.get(row['model'])
  if slug:
   fs=list((R/'experiments/ptbxl_all'/slug).rglob('*_agg.npz'));ns=list((R/'experiments/ptbxl_all'/slug).rglob('*_noagg.npz'))
   if len(fs)==1 and len(ns)==1:return fs[0],ns[0]
 return None,None
def main():
 s=[x for x in rd(S) if x['mapping_result']=='PASS'];m=rd(M); missing=[x for x in s if not next((y for y in m if y['dataset']==x['dataset'] and y['model']==x['model'] and y['mode']==x['mode']),{}).get('ours_macro_auroc')]
 if len(s)!=55 or len(missing)!=34:raise RuntimeError(f'COUNT_MISMATCH pass={len(s)} missing={len(missing)}')
 out=[]
 for x in missing:
  a,n=find(x); z={'dataset':x['dataset'],'model':x['model'],'mode':x['mode'],'canonical_run':x['canonical_run'],'saved_metric_present':'NO','saved_metric':'','saved_metric_source':'','recomputed_metric':'','metric_implementation':'clinical_ts.utils.eval_utils_cafa.multiclass_roc_curve (locked mcrc_flat semantics)','point_metric_match':'NOT_APPLICABLE_HISTORICAL_ABSENT','point_metric_gate':'BLOCKED_EXISTING_EVIDENCE','aggregate_path':'','target_path':'','mapping_evidence':x['evidence_source'],'hash_provenance':'','notes':''}
  if a and n:
   with np.load(a,allow_pickle=False) as A:
    t=A['targs'];p=A['preds'];l=[str(q) for q in A['lbl_itos'].tolist()]; val=metric(t,p,l)
   z.update({'recomputed_metric':repr(val),'point_metric_gate':'PASS_RECOVERED_FROM_CANONICAL_ARTIFACTS','aggregate_path':str(a.relative_to(R)).replace('\\','/'),'target_path':str(a.relative_to(R)).replace('\\','/'),'hash_provenance':'STRICT_MAPPING_PASS','notes':'HISTORICAL_SAVED_POINT_METRIC_ABSENT=YES; deterministic closure-derived record-level aggregate metric.'})
  else:z['notes']='Canonical aggregate/target pair not uniquely resolvable from existing local PASS provenance.'
  out.append(z)
 fs=list(out[0]);
 with open(OUTC,'w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(out)
 OUTJ.write_text(json.dumps({'expected':34,'recovered':sum(x['point_metric_gate'].startswith('PASS') for x in out),'unresolved':sum(x['point_metric_gate'].startswith('BLOCKED') for x in out),'runs':out},indent=2)+'\n')
 print(json.dumps({'expected':34,'recovered':sum(x['point_metric_gate'].startswith('PASS') for x in out),'unresolved':sum(x['point_metric_gate'].startswith('BLOCKED') for x in out)}))
if __name__=='__main__':main()
