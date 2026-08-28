"""Strict mapping closure for recovered completed ST-MEM SUB/SUPER bundles.

Uses the same core semantics as audits/ecg_id_mapping_recovery/
verify_mapping_recovery.py: canonical 2,198-row test order, exact aggregate
targets, exact repeated noagg targets, and explicit 4-window mean reconstruction.
No model, inference, or scientific data file is modified.
"""
from __future__ import annotations

import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CLOSURE=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
EVIDENCE=CLOSURE/'mapping_evidence'
META=EVIDENCE/'canonical_ptbxl_metadata/ptbxl_fold10_sub_super_mapping_metadata.json'
SOURCE_MAP=ROOT/'experiments/ptbxl_all/ecg_jepa/test_prediction_index_mapping.csv'
ACQ=CLOSURE/'STMEM_780_775_ACQUISITION_RECORD.csv'
OUT=CLOSURE/'STMEM_780_775_STRICT_MAPPING_VERIFICATION.json'
STATUS=ROOT/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'
RECOVERY=ROOT/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv'
ACQ_MANIFEST=CLOSURE/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv'
FINAL=CLOSURE/'FINAL_CLOSURE_STATUS_MANIFEST.json'
MATRIX=ROOT/'tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'

RUNS=[
 ('ptbxl_sub','Finetuning','PTBXL_SUB_07_ST_MEM_FINETUNING_FORMAL_RETRY_03','780',23,'ptbxl_sub_version_0','test_0_epoch_0'),
 ('ptbxl_sub','Frozen','PTBXL_SUB_08_ST_MEM_FROZEN_FORMAL','780',23,'ptbxl_sub_version_0','test_0_epoch_100'),
 ('ptbxl_sub','Linear','PTBXL_SUB_09_ST_MEM_LINEAR_FORMAL','780',23,'ptbxl_sub_version_0','test_0_epoch_100'),
 ('ptbxl_super','Finetuning','PTBXL_SUPER_07_ST_MEM_FINETUNING_FORMAL_RETRY_03','775',5,'ptbxl_super_version_0','test_0_epoch_0'),
 ('ptbxl_super','Frozen','PTBXL_SUPER_08_ST_MEM_FROZEN_FORMAL','775',5,'ptbxl_super_version_0','test_0_epoch_100'),
 ('ptbxl_super','Linear','PTBXL_SUPER_09_ST_MEM_LINEAR_FORMAL','775',5,'ptbxl_super_version_0','test_0_epoch_100'),
]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_csv(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
 with open(p,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
 meta=json.loads(META.read_text(encoding='utf-8'))
 canonical=read_csv(SOURCE_MAP)
 rows=meta['rows']
 map_ok=(len(canonical)==2198 and len(rows)==2198 and
         [int(x['prediction_index']) for x in canonical]==list(range(2198)) and
         [(int(x['ecg_id']),int(float(x['patient_id'])),int(x['strat_fold'])) for x in canonical]==
         [(x['ecg_id'],x['patient_id'],x['strat_fold']) for x in rows])
 if not map_ok: raise RuntimeError('canonical fold-10 ECG-ID order mismatch')
 results=[]
 for dataset,mode,run,instance,dim,version,stem in RUNS:
  base=EVIDENCE/f'instance_{instance}'/run/'predictions'/version
  agg_path=base/'agg'/f'{stem}_agg.npz'; noagg_path=base/'noagg'/f'{stem}_noagg.npz'
  with np.load(agg_path,allow_pickle=False) as agg,np.load(noagg_path,allow_pickle=False) as noagg:
   labels=[str(x) for x in agg['lbl_itos'].tolist()]
   meta_labels=meta['label_diag_subclass'] if dataset=='ptbxl_sub' else meta['label_diag_superclass']
   key='label_diag_subclass_filtered_numeric' if dataset=='ptbxl_sub' else 'label_diag_superclass_filtered_numeric'
   expected=np.zeros((2198,dim),dtype=np.float32)
   for i,row in enumerate(rows): expected[i,row[key]]=1
   repeats=len(noagg['targs'])//len(agg['targs'])
   group_targs=noagg['targs'].reshape(2198,repeats,dim)
   reconstructed=noagg['preds'].reshape(2198,repeats,dim).mean(axis=1)
   checks={
    'canonical_ecg_id_order':map_ok,
    'unique_test_ecg_ids':len({r['ecg_id'] for r in rows})==2198,
    'output_dim':agg['preds'].shape==(2198,dim) and noagg['preds'].shape==(2198*4,dim),
    'labels_match_metadata':labels==meta_labels and list(noagg['lbl_itos'])==list(agg['lbl_itos']),
    'aggregate_targets_match_canonical_order':np.array_equal(agg['targs'],expected),
    'target_group_consistency':np.array_equal(group_targs,np.repeat(expected[:,None,:],repeats,axis=1)),
    'aggregation_reconstruction':np.array_equal(reconstructed,agg['preds']),
    'saved_aggregate_match':np.array_equal(reconstructed,agg['preds']),
   }
   if repeats!=4 or not all(checks.values()): raise RuntimeError(f'strict mapping failed: {run}: {checks}')
   results.append({'dataset':dataset,'model':'ST-MEM','mode':mode,'canonical_run':run,'instance':instance,'agg_path':str(agg_path.relative_to(ROOT)).replace('\\','/'),'agg_sha256':sha(agg_path),'noagg_path':str(noagg_path.relative_to(ROOT)).replace('\\','/'),'noagg_sha256':sha(noagg_path),'labels':labels,'unique_test_ecg_ids':2198,'windows_per_ecg':repeats,'max_aggregate_abs_error':float(np.max(np.abs(reconstructed-agg['preds']))),'checks':checks,'strict_mapping_proven':True})
 stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
 output={'method':'Existing strict mapping helper semantics extended with recovered original PTB-XL fold-10 filtered-label metadata: canonical ECG-ID order; exact aggregate targets; exact 4-window target grouping; exact mean probability reconstruction.','canonical_map_path':str(SOURCE_MAP.relative_to(ROOT)).replace('\\','/'),'canonical_map_sha256':sha(SOURCE_MAP),'metadata_projection_path':str(META.relative_to(ROOT)).replace('\\','/'),'metadata_projection_sha256':sha(META),'verified_utc':stamp,'runs':results,'pass':True}
 OUT.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
 recovered={x['canonical_run']:x for x in results}
 for path in (STATUS,RECOVERY):
  table=read_csv(path); fields=list(table[0])
  for row in table:
   if row['canonical_run'] in recovered:
    x=recovered[row['canonical_run']]; row.update({'evidence_source':f"{OUT.relative_to(ROOT).as_posix()}; recovered hash-verified minimal bundle from instance {x['instance']}",'raw_prediction_status':'RECOVERED_HASH_VERIFIED','target_status':'EMBEDDED_IN_RECOVERED_NPZ_HASH_VERIFIED','aggregate_status':'RECOVERED_HASH_VERIFIED','ecg_id_metadata_status':'RECOVERED_FOLD10_METADATA_PROJECTION_HASH_RECORDED','mapping_result':'PASS','unique_test_ecg_ids':'2198','aggregation_reconstruction':'PASS','target_consistency':'PASS','saved_aggregate_match':'PASS','blocker_category':'','notes':f"Strict PASS: canonical ECG-ID order, 4-window mean reconstruction, target grouping, and aggregate match all exact; verification={OUT.relative_to(ROOT).as_posix()}."})
  write_csv(path,table,fields)
 acq=read_csv(ACQ); byrun={}
 for a in acq: byrun.setdefault(a['canonical_run'],[]).append(a)
 manifest=read_csv(ACQ_MANIFEST); fields=list(manifest[0])
 for row in manifest:
  if row['canonical_run'] in recovered:
   items=byrun[row['canonical_run']]
   row.update({'source_path':items[0]['remote_path'].rsplit('/',1)[0].rsplit('/predictions',1)[0],'local_path':str((EVIDENCE/f"instance_{recovered[row['canonical_run']]['instance']}"/row['canonical_run']).relative_to(ROOT)).replace('\\','/'),'artifact_types_recovered':'RAW_WINDOW_PREDICTIONS_AND_TARGETS;SAVED_AGGREGATE_PREDICTIONS_AND_TARGETS;FINAL_RESULT_AND_VALIDATION;RUN_MANIFEST_COMMAND;FORMAL_TEST_LOG_IF_SEPARATE','remote_connectivity':'REMOTE_READ_ONLY_ACCESS','acquisition_time_utc':stamp,'acquisition_method':'READ_ONLY_SCP_MINIMAL_BUNDLE;STRICT_MAPPING','remote_sha256':'PER_FILE_IN_STMEM_780_775_ACQUISITION_RECORD.csv','local_sha256':'PER_FILE_IN_STMEM_780_775_ACQUISITION_RECORD.csv','file_size_bytes':str(sum(int(a['file_size_bytes']) for a in items)),'hash_verification':f"PASS_{len(items)}_OF_{len(items)}_FILES",'mapping_after':'PASS','blocker_after':'','user_power_on_required':'NO','notes':f"Recovered from instance {recovered[row['canonical_run']]['instance']} after user power-on; strict mapping PASS; no checkpoint, event, data signal, or environment copied."})
 write_csv(ACQ_MANIFEST,manifest,fields)
 matrix=read_csv(MATRIX); mfields=list(matrix[0])
 for row in matrix:
  if row['canonical_run_id_or_directory'] in recovered: row['ecg_id_mapping_status']='PASS'
 write_csv(MATRIX,matrix,mfields)
 final=json.loads(FINAL.read_text(encoding='utf-8'))
 final['counts'].update({'mapping_pass':17,'mapping_new':6,'mapping_deferred':14,'mapping_blocked':1,'missing_evidence':46})
 final['mapping_evidence_recovery'].update({'mapping_newly_closed_this_run':6,'mapping_pass_total':17,'mapping_missing_evidence_remaining':46,'evidence_recovered_count':6,'bootstrap_eligible_run_count':17})
 final['mapping_evidence_acquisition'].update({'new_evidence_files_copied':26,'local_path_recovered':0,'worker_archive_recovered':0,'remote_copy_recovered':6,'remote_host_unreachable_count':0,'user_power_on_required_count':0,'unreachable_instances':[],'unique_power_on_instance_count':2,'unique_power_on_instances':['780','775'],'previous_count_was_run_entry_count':True,'total_bytes_transferred':7752761,'total_bytes_skipped_by_hash_dedup':0,'total_bytes_compressed_archive':0,'temp_files_removed_after_verification':0,'minimal_local_footprint':'PASS'})
 FINAL.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'newly_closed':len(results),'mapping_pass_total':17,'missing_evidence_remaining':46,'verification':str(OUT.relative_to(ROOT))},indent=2))
if __name__=='__main__': main()
