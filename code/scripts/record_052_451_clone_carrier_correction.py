"""Record the user-confirmed 052->451 evidence-carrier correction; no network."""
from __future__ import annotations
import csv, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'; T=ROOT/'tables'
STATUS=T/'PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'; MATRIX=T/'PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'; ACQ=C/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv'; FINAL=C/'FINAL_CLOSURE_STATUS_MANIFEST.json'; OUT=C/'ECG_052_451_ACQUISITION_RECORD.csv'
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with open(p,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 st=read(STATUS); mx={r['canonical_run_id_or_directory']:r for r in read(MATRIX)}; stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(); rows=[]; carrier_runs=set()
 for r in st:
  m=mx[r['canonical_run']]; auth=m['execution_authority']
  if auth not in ('052_SPECIAL_SUCCESSOR_OR_ARCHIVED_ALL_FORMAL','451_SPECIAL_SUCCESSOR'): continue
  if r['mapping_result'] not in ('DEFERRED','MISSING_EVIDENCE'): continue
  historical='052' if auth=='052_SPECIAL_SUCCESSOR_OR_ARCHIVED_ALL_FORMAL' else '451'
  carrier_runs.add(r['canonical_run'])
  rows.append({'historical_source_instance':historical,'evidence_carrier_current':'451','recover_from_451_clone':'YES' if historical=='052' else 'NOT_APPLICABLE_451_NATIVE','dataset':r['dataset'],'model':r['model'],'mode':r['mode'],'canonical_run':r['canonical_run'],'expected_052_path':m['prediction_artifact'] if historical=='052' else '','expected_451_path':m['prediction_artifact'],'endpoint_refresh_source':'LOCAL_SSH_CONFIG_AND_451_CONTROLLER_RECORDS_CHECKED__NO_CURRENT_451_HOST_PORT_RETAINED','instance_451_host':'','instance_451_port':'','connectivity':'PENDING_ENDPOINT_REFRESH_NO_CONNECTION_ATTEMPT','acquisition_status':'NOT_STARTED','notes':'User correction: 052 unavailable; only 451 clone may be read. No host/port guessed and no connection made.'})
 write(OUT,rows)
 acq=read(ACQ)
 for r in acq:
  if r['canonical_run'] in carrier_runs:
   r['source_instance_or_worker']='451_CLONE_CARRIER_PENDING_ENDPOINT_REFRESH' if r['dataset']=='ptbxl_all' else '451_PENDING_ENDPOINT_REFRESH'
   r['remote_connectivity']='PENDING_ENDPOINT_REFRESH_NO_CONNECTION_ATTEMPT'
   r['user_power_on_required']='NO'
 write(ACQ,acq)
 final=json.loads(FINAL.read_text(encoding='utf-8')); final['ecg_052_451_carrier_correction']={'recorded_utc':stamp,'052_connectivity':'UNAVAILABLE_AND_NOT_REQUIRED','052_power_on_attempt_required':False,'source_instance_historical_for_all_frozen_linear':'052','evidence_carrier_current':'451','recover_from_451_clone':True,'instance_451_endpoint_refresh_source':'Local SSH config and 451 controller records; no current host/port retained','instance_451_endpoint_status':'PENDING_USER_PROVIDED_CURRENT_AUTODL_ENDPOINT','candidate_runs':len(rows),'no_remote_connection_made':True}; FINAL.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8'); print(json.dumps(final['ecg_052_451_carrier_correction'],indent=2))
if __name__=='__main__':main()
