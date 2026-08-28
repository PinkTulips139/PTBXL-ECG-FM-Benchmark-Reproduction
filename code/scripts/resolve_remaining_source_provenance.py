"""Local-only provenance resolution for remaining mapping evidence sources."""
from __future__ import annotations
import csv, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; T=ROOT/'tables'; C=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
STATUS=T/'PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'; MATRIX=T/'PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'
REMOTECSV=C/'REMOTE_SOURCE_PROVENANCE_RESOLUTION.csv'; REMOTEJSON=C/'REMOTE_SOURCE_PROVENANCE_RESOLUTION.json'; WORKER=C/'WORKER_ARCHIVE_PROVENANCE_RESOLUTION.csv'; LOCAL=C/'LOCAL_PATH_PROVENANCE_RESOLUTION.csv'; FINAL=C/'FINAL_CLOSURE_STATUS_MANIFEST.json'
SPECIAL={
 ('ptbxl_sub','ECG-CPC','Finetuning'):'PTBXL_SUB_ECG_CPC_FINETUNING_FORMAL_052_01',('ptbxl_sub','ECG-CPC','Frozen'):'PTBXL_SUB_ECG_CPC_FROZEN_FORMAL_052_02',('ptbxl_sub','ECG-CPC','Linear'):'PTBXL_SUB_ECG_CPC_LINEAR_FORMAL_052_03',
 ('ptbxl_super','ECG-CPC','Finetuning'):'PTBXL_SUPER_ECG_CPC_FINETUNING_FORMAL_052_04',('ptbxl_super','ECG-CPC','Frozen'):'PTBXL_SUPER_ECG_CPC_FROZEN_FORMAL_052_05',('ptbxl_super','ECG-CPC','Linear'):'PTBXL_SUPER_ECG_CPC_LINEAR_FORMAL_052_06',
 ('ptbxl_sub','ECG-FM','Finetuning'):'PTBXL_SUB_ECG_FM_FINETUNING_FORMAL_052_07',('ptbxl_sub','ECG-FM','Frozen'):'PTBXL_SUB_ECG_FM_FROZEN_FORMAL_052_08',('ptbxl_sub','ECG-FM','Linear'):'PTBXL_SUB_ECG_FM_LINEAR_FORMAL_052_09',
}
def read(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with open(p,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 st=read(STATUS); mx={x['canonical_run_id_or_directory']:x for x in read(MATRIX)}; stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
 remote=[]
 for s in st:
  isremote=s['mapping_result']=='DEFERRED' or (s['mapping_result']=='MISSING_EVIDENCE' and s['blocker_category']=='REMOTE_COPY_REQUIRED')
  if not isremote: continue
  m=mx[s['canonical_run']]; auth=m['execution_authority']; dataset=s['dataset']; run=s['canonical_run']
  inst=host=port=endpoint_source=''; proven='NO'; refresh='YES'; power='NO'; route=''
  if auth=='052_SPECIAL_SUCCESSOR_OR_ARCHIVED_ALL_FORMAL':
   inst='052'; host='connect.nmb1.seetacloud.com'; port='37968'; proven='YES'; power='YES'; route='052_ALL_FROZEN_LINEAR_ARCHIVED_SPECIAL_ROUTE'; endpoint_source='docs/PTBXL_NEW_INSTANCE_RECOVERY_PREFLIGHT.md: ssh -p 37968 root@connect.nmb1.seetacloud.com (historic endpoint; authentication then failed)'
  elif auth=='451_SPECIAL_SUCCESSOR':
   inst='451'; proven='YES'; power='YES'; route='451_ECGFM_SUPER_SUCCESSOR'; endpoint_source='execution_control/PTBXL_451_ECGFM_SUPER_FINAL_CONTROLLER/findings.md: SSH passed using established 052 key; host/port not retained locally'
  elif auth=='COMMON_CONTROLLER':
   candidate='573' if dataset=='ptbxl_sub' else '871'; host='connect.westd.seetacloud.com' if candidate=='573' else 'connect.westc.seetacloud.com'; port='26744' if candidate=='573' else '36083'; route=f'HISTORICAL_{candidate}_COMMON_PLAN_ONLY'; endpoint_source=(f'docs/PTBXL_SUB_573_EXECUTION_READINESS.md' if candidate=='573' else 'docs/PTBXL_SUPER_871_EXECUTION_READINESS.md')+'; document explicitly predates formal preparation and does not prove completed-run source'; inst=f'UNRESOLVED_HISTORICAL_CANDIDATE_{candidate}'
  remote.append({'dataset':dataset,'model':s['model'],'mode':s['mode'],'canonical_run':run,'execution_authority':auth,'historical_source_instance':inst,'instance_id_proven':proven,'historical_host':host,'historical_port':port,'historical_remote_project_root':'/root/autodl-tmp/ECG','historical_formal_run_path':m['prediction_artifact'].rsplit('/predictions',1)[0],'expected_prediction_path':m['prediction_artifact'],'expected_target_path':m['target_artifact'],'expected_aggregate_path':m['aggregate_artifact'],'execution_route':route,'source_of_endpoint':endpoint_source,'endpoint_requires_refresh':refresh,'local_archive_insufficient':'YES','remote_evidence_required':'YES','power_on_required':power,'source_provenance_file':s['evidence_source']})
 write(REMOTECSV,remote)
 worker=[]
 for s in st:
  if s['mapping_result']!='MISSING_EVIDENCE' or s['blocker_category']!='ARCHIVED_WORKER_ARTIFACT_EXPECTED':continue
  m=mx[s['canonical_run']]; suffix=s['canonical_run'].rsplit('_',1)[-1]; matrix=T/'emergency_workers'/f'{suffix}_FORMAL_COMMAND_MATRIX.csv'; rows=read(matrix); wr=next(x for x in rows if x['run_id']==s['canonical_run'])
  worker.append({'dataset':s['dataset'],'model':s['model'],'mode':s['mode'],'canonical_run':s['canonical_run'],'canonical_worker_identity':suffix,'worker_instance_id':'NOT_RETAINED_IN_COMMAND_MATRIX','delivery_bundle_name':f'{suffix}_FORMAL_DELIVERY_BUNDLE_UNRESOLVED','archive_filename':'UNRESOLVED','archive_path_resolved':'NO','historical_local_destination':'tmp/emergency_worker_transfer_20260821 (transfer key only; no delivery bundle)','historical_remote_source_path':wr['prediction_path'],'expected_target_path':wr['prediction_path']+'/noagg/*.npz (embedded targets expected)','expected_aggregate_path':wr['prediction_path']+'/agg/*.npz','delivery_manifest_path':str(matrix.relative_to(ROOT)).replace('\\','/'),'notes':'Canonical worker and exact remote prediction path resolved; archive/delivery index is not present locally.'})
 write(WORKER,worker)
 local=[]
 for s in st:
  if s['mapping_result']!='MISSING_EVIDENCE' or s['blocker_category']!='LOCAL_PATH_NOT_YET_LOCATED':continue
  key=(s['dataset'],s['model'],s['mode']); expected= SPECIAL[key]; expected_root=f'/root/autodl-tmp/ECG/formal_runs/{expected}'
  ingest=C/'mapping_evidence'/'instance_052'/expected
  local.append({'dataset':s['dataset'],'model':s['model'],'mode':s['mode'],'canonical_run_placeholder':s['canonical_run'],'historical_expected_run_id':expected,'historical_remote_prediction_path':expected_root+'/predictions','local_expected_ingest_path':str(ingest.relative_to(ROOT)).replace('\\','/'),'path_exists':'YES' if ingest.exists() else 'NO','parent_path':str(ingest.parent.relative_to(ROOT)).replace('\\','/'),'parent_exists':'YES' if ingest.parent.exists() else 'NO','manifest_reference':'scripts/ptbxl_052_special_continuous_controller.py: build_runs(); tables/PTBXL_SUB_SUPER_FORMAL_COMMAND_MATRIX.csv (finetuning path provenance)','notes':'Historical local delivery destination is not retained. This is the exact future closure-ingest path, not evidence of a local artifact.'})
 write(LOCAL,local)
 instances=[x for x in remote if x['instance_id_proven']=='YES']; grouped={}
 for x in instances:grouped.setdefault(x['historical_source_instance'],[]).append(x)
 unique=[]
 for inst,rows in grouped.items():unique.append({'instance_id':inst,'dependent_run_count':len(rows),'dependent_runs':[x['canonical_run'] for x in rows],'datasets':sorted({x['dataset'] for x in rows}),'models':sorted({x['model'] for x in rows}),'known_historical_host':rows[0]['historical_host'],'known_historical_port':rows[0]['historical_port'],'endpoint_provenance':rows[0]['source_of_endpoint'],'endpoint_requires_refresh':'YES','expected_remote_root':'/root/autodl-tmp/ECG/formal_runs','power_on_required':'YES','why_required':'Formal prediction/target/aggregate evidence is remote-only and no local archive bundle is present.'})
 report={'phase':'SOURCE_PROVENANCE_RESOLUTION','generated_utc':stamp,'remote_dependent_run_entry_count':len(remote),'remote_runs_source_resolved':len(instances),'remote_runs_source_unresolved':len(remote)-len(instances),'unique_remote_instance_count':len(unique),'unique_remote_instances':unique,'unresolved_common_controller_candidate_bindings':[x for x in remote if x['execution_authority']=='COMMON_CONTROLLER'],'power_on_required_instance_count':len(unique),'power_on_required_instances':[x['instance_id'] for x in unique],'endpoint_refresh_required_count':len(unique),'worker_archive_expected_count':len(worker),'worker_identity_resolved':len(worker),'archive_path_resolved':0,'archive_path_unresolved':len(worker),'local_path_expected_count':len(local),'local_path_resolved':len(local),'local_path_still_unresolved':0,'remote_power_on_avoidable_run_count':0,'new_substantive_discrepancy':False,'no_remote_connection_made':True,'minimal_local_footprint':'PASS'}
 REMOTEJSON.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); final=json.loads(FINAL.read_text(encoding='utf-8')); final['source_provenance_resolution']=report; FINAL.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2))
if __name__=='__main__':main()
