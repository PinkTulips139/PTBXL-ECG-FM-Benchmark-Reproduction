"""Persist Wave-2 fail-closed classifications without touching scientific data."""
from __future__ import annotations
import csv, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'tables'; C=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
STATUS=T/'PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'; RECOVERY=T/'PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv'
ACQ=C/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv'; ACQJSON=C/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.json'; FINAL=C/'FINAL_CLOSURE_STATUS_MANIFEST.json'; OUT=C/'REMAINING_MAPPING_RECOVERY_WAVE_2_CLASSIFICATION.json'
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with open(p,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
 for p in (STATUS,RECOVERY):
  rows=read(p)
  for r in rows:
   if r['mapping_result']=='DEFERRED':
    r['blocker_category']='REMOTE_COPY_REQUIRED'; r['notes']='Wave 2 targeted local evidence check found no corresponding Frozen/Linear raw prediction, target, or aggregate bundle; require the archived 052 remote copy.'
   elif r['mapping_result']=='MISSING_EVIDENCE':
    old=r['blocker_category']
    if old=='REMOTE_COPY_NOT_YET_ARCHIVED': r['blocker_category']='REMOTE_COPY_REQUIRED'
    elif old=='ARCHIVED_WORKER_ARTIFACT_EXPECTED': r['blocker_category']='ARCHIVED_WORKER_ARTIFACT_EXPECTED'
    elif old=='LOCAL_PATH_NOT_YET_LOCATED': r['blocker_category']='LOCAL_PATH_NOT_YET_LOCATED'
  write(p,rows)
 acq=read(ACQ)
 for r in acq:
  if r['mapping_after']=='DEFERRED':
   r['classification_before']='REMOTE_COPY_REQUIRED'; r['remote_connectivity']='NOT_ATTEMPTED_ENDPOINT_UNAVAILABLE_IN_LOCAL_PROVENANCE'
  elif r['mapping_after']=='MISSING_EVIDENCE' and r['classification_before']=='REMOTE_COPY_NOT_YET_ARCHIVED':
   r['classification_before']='REMOTE_COPY_REQUIRED'; r['remote_connectivity']='NOT_ATTEMPTED_ENDPOINT_UNAVAILABLE_IN_LOCAL_PROVENANCE'
 write(ACQ,acq)
 status=read(STATUS)
 def count(pred): return sum(pred(r) for r in status)
 remote=[r for r in acq if r['mapping_after'] in ('DEFERRED','MISSING_EVIDENCE') and r['classification_before']=='REMOTE_COPY_REQUIRED']
 source_groups={}
 for r in remote:
  key=r['source_authority']; source_groups.setdefault(key,[]).append(r['canonical_run'])
 report={'phase':'REMAINING_MAPPING_RECOVERY_WAVE_2','generated_utc':stamp,'no_training_inference_or_bootstrap':True,'deferred_before':14,'deferred_closed_this_run':0,'deferred_remaining':count(lambda r:r['mapping_result']=='DEFERRED'),'missing_evidence_before':46,'missing_evidence_recovered_this_run':0,'missing_evidence_remaining':count(lambda r:r['mapping_result']=='MISSING_EVIDENCE'),'missing_evidence_classification':{'LOCAL_ARTIFACT_NOW_AVAILABLE':0,'LOCAL_PATH_NOT_YET_LOCATED':count(lambda r:r['mapping_result']=='MISSING_EVIDENCE' and r['blocker_category']=='LOCAL_PATH_NOT_YET_LOCATED'),'ARCHIVED_WORKER_ARTIFACT_EXPECTED':count(lambda r:r['mapping_result']=='MISSING_EVIDENCE' and r['blocker_category']=='ARCHIVED_WORKER_ARTIFACT_EXPECTED'),'REMOTE_COPY_REQUIRED':count(lambda r:r['mapping_result']=='MISSING_EVIDENCE' and r['blocker_category']=='REMOTE_COPY_REQUIRED'),'RAW_PREDICTION_MISSING':0,'TARGET_MISSING':0,'AGGREGATE_MISSING':0,'ECG_ID_METADATA_MISSING':0,'ORDERING_NOT_PROVEN':0,'OTHER':0},'deferred_remote_copy_required':count(lambda r:r['mapping_result']=='DEFERRED' and r['blocker_category']=='REMOTE_COPY_REQUIRED'),'historical_blocked':count(lambda r:r['mapping_result']=='BLOCKED'),'remote_source_groups':source_groups,'unique_power_on_instance_count':0,'unique_power_on_instances':[],'reason_no_power_on_request':'No currently recorded host/port exists for the 12 COMMON_CONTROLLER or 3 451 source entries; no endpoint was guessed or contacted.','local_archive_search_scope':['experiments/ptbxl_all','execution_control/PTBXL_052_ALL_SPECIAL_FROZEN_LINEAR_CONTROLLER','execution_control/PTBXL_052_OVERNIGHT_BATCH_A','tables/emergency_workers','tmp/emergency_worker_transfer_20260821'],'local_or_worker_bundle_recovered':0,'new_substantive_discrepancy':False}
 OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 acqjson=json.loads(ACQJSON.read_text(encoding='utf-8')); acqjson['wave_2']=report; ACQJSON.write_text(json.dumps(acqjson,indent=2)+'\n',encoding='utf-8')
 final=json.loads(FINAL.read_text(encoding='utf-8')); final['remaining_mapping_recovery_wave_2']=report; FINAL.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
