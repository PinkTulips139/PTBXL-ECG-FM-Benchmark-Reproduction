import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=R/'execution_control/PTBXL_FINAL_CLOSURE';A=C/'PARALLEL_451_RESIDUAL_SPECIAL_RECOVERY.csv';V=C/'PARALLEL_451_RESIDUAL_STRICT_MAPPING.csv';S=R/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv';E=R/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv';F=C/'FINAL_CLOSURE_STATUS_MANIFEST.json';O=C/'GLOBAL_CANONICAL_MERGE_AFTER_451_RESIDUAL_SPECIAL.json'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def wr(p,x,fs):
 with open(p,'w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(x)
a={ (x['dataset'].lower().replace('ptb-xl','ptbxl').replace('(','_').replace(')',''),x['model'],x['mode']):x for x in rd(A)};v=rd(V);assert len(v)==9 and all(x['strict_mapping_result']=='PASS' for x in v)
for p in(S,E):
 x=rd(p);fs=list(x[0]);n=0
 for z in x:
  key=(z['dataset'],z['model'],z['mode'])
  if key in a:
   q=a[key];z.update({'evidence_source':'execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_451_RESIDUAL_STRICT_MAPPING.csv; '+q['local_bundle_path'],'raw_prediction_status':'RECOVERED_HASH_VERIFIED','target_status':'EMBEDDED_NPZ_HASH_VERIFIED','aggregate_status':'RECOVERED_HASH_VERIFIED','ecg_id_metadata_status':'CANONICAL_FOLD10_METADATA','mapping_result':'PASS','unique_test_ecg_ids':'2198','aggregation_reconstruction':'PASS','target_consistency':'PASS','saved_aggregate_match':'PASS','blocker_category':'','notes':f"Recovered run {q['canonical_run']}; historical source 052, carrier 451; SHA256 PASS; strict mapping PASS."});n+=1
 assert n==9;wr(p,x,fs)
x=rd(S);counts={}
for z in x:counts[z['mapping_result']]=counts.get(z['mapping_result'],0)+1
assert sum(counts.values())==78
f=json.loads(F.read_text());f['counts'].update({'mapping_pass':counts.get('PASS',0),'mapping_blocked':counts.get('BLOCKED',0),'missing_evidence':counts.get('MISSING_EVIDENCE',0),'mapping_deferred':counts.get('DEFERRED',0)});f['mapping_evidence_recovery'].update({'mapping_pass_total':counts.get('PASS',0),'mapping_blocked_remaining':counts.get('BLOCKED',0),'mapping_missing_evidence_remaining':counts.get('MISSING_EVIDENCE',0),'bootstrap_eligible_run_count':counts.get('PASS',0)});f['parallel_451_residual_special_merge']={'runs_merged':9,'counts':counts,'historical_source':'052','carrier':'451','worker_branch_pending':True};F.write_text(json.dumps(f,indent=2)+'\n');O.write_text(json.dumps({'merged_runs':[q['canonical_run'] for q in a.values()],'mapping_counts':counts,'sum':sum(counts.values()),'worker_branch_pending':True},indent=2)+'\n');print(json.dumps(counts))
