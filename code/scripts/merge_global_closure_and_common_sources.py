"""Deterministic canonical merge of finalized Run015, JEPA adjudication, and common sources."""
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
S=ROOT/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv';R=ROOT/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv';M=ROOT/'tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv';F=C/'FINAL_CLOSURE_STATUS_MANIFEST.json';P=C/'PARALLEL_COMMON_CONTROLLER_SOURCE_RESOLUTION.json';J=C/'ECG_JEPA_AGG_NOAGG_DISCREPANCY_ADJUDICATION.json';OUT=C/'GLOBAL_CANONICAL_MERGE_AFTER_ECG_JEPA_ADJUDICATION.json'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(p,x,fs):
 with open(p,'w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(x)
def main():
 p=json.loads(P.read_text());j=json.loads(J.read_text());assert p['common_actual_source_resolved']==12 and not j['new_substantive_discrepancy']
 common={r:'780' for r in p['actual_source_evidence']['instance_780']['runs']}|{r:'775' for r in p['actual_source_evidence']['instance_775']['runs']}
 je=set(r for v in p['actual_source_evidence'].values() for r in v['runs'] if 'ECG_JEPA' in r)
 for path in (S,R):
  rows=rd(path);fs=list(rows[0])
  for x in rows:
   run=x['canonical_run']
   if run in common:
    inst=common[run];extra=' ECG-JEPA agg/noagg byte identity is adjudicated as legal identity aggregation; it is not a mapping blocker.' if run in je else ''
    x.update({'evidence_source':f'execution_control/PTBXL_FINAL_CLOSURE/PARALLEL_COMMON_CONTROLLER_SOURCE_RESOLUTION.json; execution_control/PTBXL_FINAL_CLOSURE/remote_{inst}_minimal_bundle_sha256.txt','raw_prediction_status':'REMOTE_HASH_INVENTORIED_NOT_LOCAL','target_status':'REMOTE_HASH_INVENTORIED_NOT_LOCAL','aggregate_status':'REMOTE_HASH_INVENTORIED_NOT_LOCAL','ecg_id_metadata_status':'CANONICAL_FOLD10_METADATA_AVAILABLE','mapping_result':'MISSING_EVIDENCE','unique_test_ecg_ids':'','aggregation_reconstruction':'','target_consistency':'','saved_aggregate_match':'','blocker_category':'REMOTE_REOPEN_REQUIRED','notes':f'Actual execution source proven: instance {inst}; 573/871 retained only as planned bindings. No local scientific bundle exists, so strict mapping was not run.{extra}'})
  wr(path,rows,fs)
 rows=rd(M);fs=list(rows[0])
 for x in rows:
  run=x['canonical_run_id_or_directory']
  if run in common:
   inst=common[run];extra=' ECG-JEPA identity aggregation adjudicated; hash equality is not a scientific artifact failure.' if run in je else ''
   x['notes']=(x.get('notes','')+' '+f'Actual source proven by parallel read-only SHA inventory: instance {inst}; scientific objects not local for strict mapping.'+extra).strip();x['ecg_id_mapping_status']='MISSING_EVIDENCE'
 wr(M,rows,fs)
 state=rd(S);counts={}
 for x in state:counts[x['mapping_result']]=counts.get(x['mapping_result'],0)+1
 if sum(counts.values())!=78:raise RuntimeError(counts)
 final=json.loads(F.read_text());stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat();final['counts'].update({'mapping_pass':counts.get('PASS',0),'mapping_blocked':counts.get('BLOCKED',0),'missing_evidence':counts.get('MISSING_EVIDENCE',0),'mapping_deferred':counts.get('DEFERRED',0)});final['mapping_evidence_recovery'].update({'mapping_pass_total':counts.get('PASS',0),'mapping_deferred_remaining':counts.get('DEFERRED',0),'mapping_blocked_remaining':counts.get('BLOCKED',0),'mapping_missing_evidence_remaining':counts.get('MISSING_EVIDENCE',0),'bootstrap_eligible_run_count':counts.get('PASS',0)});final['global_canonical_merge_after_ecg_jepa_adjudication']={'merged_utc':stamp,'formal_runs_complete':'78/78','common_actual_source_resolved':'12/12','common_mapping_newly_closed':0,'common_mapping_still_missing':12,'common_remote_reopen_required':12,'ecg_jepa_discrepancy_status':'CLOSED_NO_SCIENTIFIC_FAILURE','worker_archive_branch_pending':True,'mapping_counts':counts,'new_substantive_discrepancy':False};F.write_text(json.dumps(final,indent=2)+'\n')
 OUT.write_text(json.dumps({'merged_utc':stamp,'inputs':[str(P.relative_to(ROOT)).replace('\\','/'),str(J.relative_to(ROOT)).replace('\\','/'),'RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json'],'deterministic_precedence':'latest proven run-level evidence supersedes older inventory status; historical provenance retained','formal_run_count':78,'mapping_counts':counts,'common':{'expected':12,'actual_source_resolved':12,'mapping_already_pass':0,'mapping_newly_closed':0,'mapping_still_missing':12,'remote_reopen_required':12},'ecg_jepa_discrepancy_status':'CLOSED_NO_SCIENTIFIC_FAILURE','worker_archive_branch_pending':True,'new_substantive_discrepancy':False},indent=2)+'\n')
 print(json.dumps({'counts':counts,'common_remote_reopen_required':12},indent=2))
if __name__=='__main__':main()
