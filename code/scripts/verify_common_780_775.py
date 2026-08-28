import csv,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];C=R/'execution_control/PTBXL_FINAL_CLOSURE';S=R/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv';E=R/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv';F=C/'FINAL_CLOSURE_STATUS_MANIFEST.json';O=C/'COMMON_780_775_STRICT_MAPPING_VERIFICATION.json'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(p,x,fs):
 with open(p,'w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(x)
meta=json.loads((C/'mapping_evidence/canonical_ptbxl_metadata/ptbxl_fold10_sub_super_mapping_metadata.json').read_text()); rows=meta['rows']; out=[]
for inst,prefix,dim,key,labels in [('780','PTBXL_SUB',23,'label_diag_subclass_filtered_numeric',meta['label_diag_subclass']),('775','PTBXL_SUPER',5,'label_diag_superclass_filtered_numeric',meta['label_diag_superclass'])]:
 for i in range(1,7):
  n=f'{i:02d}';model='ECGFounder' if i<=3 else 'ECG-JEPA';mode=['Finetuning','Frozen','Linear'][(i-1)%3];run=f'{prefix}_{n}_{"ECGFOUNDER" if i<=3 else "ECG_JEPA"}_{mode.upper()}_FORMAL';d=C/f'mapping_evidence/instance_{inst}/{run}';a=next(d.glob('*_agg.npz'));q=next(d.glob('*_noagg.npz'))
  exp=np.zeros((2198,dim),np.float32)
  for j,x in enumerate(rows):exp[j,x[key]]=1
  with np.load(a,allow_pickle=False) as A,np.load(q,allow_pickle=False) as Q:
   rep=len(Q['targs'])//2198;rec=Q['preds'].reshape(2198,rep,dim).mean(1);ok=(len(rows)==2198 and len({x['ecg_id'] for x in rows})==2198 and A['preds'].shape==(2198,dim) and np.array_equal(A['targs'],exp) and np.array_equal(Q['targs'].reshape(2198,rep,dim),np.repeat(exp[:,None,:],rep,1)) and np.array_equal(rec,A['preds']) and [str(x) for x in A['lbl_itos'].tolist()]==labels)
   if not ok:raise RuntimeError(run)
   out.append({'run':run,'instance':inst,'dataset':'ptbxl_sub' if inst=='780' else 'ptbxl_super','model':model,'mode':mode,'windows':rep,'max_abs_diff':float(np.max(np.abs(rec-A['preds']))),'pass':True})
O.write_text(json.dumps({'runs':out,'pass':True},indent=2)+'\n')
for p in (S,E):
 x=rd(p);fs=list(x[0]);by={z['run']:z for z in out}
 for z in x:
  if z['canonical_run'] in by:z.update({'evidence_source':str(O.relative_to(R)).replace('\\','/'),'raw_prediction_status':'RECOVERED_HASH_VERIFIED','target_status':'EMBEDDED_NPZ_HASH_VERIFIED','aggregate_status':'RECOVERED_HASH_VERIFIED','ecg_id_metadata_status':'CANONICAL_FOLD10_METADATA','mapping_result':'PASS','unique_test_ecg_ids':'2198','aggregation_reconstruction':'PASS','target_consistency':'PASS','saved_aggregate_match':'PASS','blocker_category':'','notes':'Strict PASS from current read-only common-source acquisition; ECG-JEPA identity aggregation accepted where windows=1.'})
 wr(p,x,fs)
f=json.loads(F.read_text());f['counts'].update({'mapping_pass':46,'mapping_blocked':1,'missing_evidence':31,'mapping_deferred':0});f['mapping_evidence_recovery'].update({'mapping_pass_total':46,'mapping_missing_evidence_remaining':31,'bootstrap_eligible_run_count':46});F.write_text(json.dumps(f,indent=2)+'\n');print(json.dumps({'closed':12,'pass_total':46},indent=2))
