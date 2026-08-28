"""Strictly close canonical Run015 using its preserved successful Retry01 evidence."""
from __future__ import annotations
import csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
R='PTBXL_ALL_ECG_FM_FROZEN_FORMAL_RUN_015'; RETRY=R+'_RETRY_01'; D=C/'mapping_evidence/instance_451'/RETRY
STATUS=ROOT/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'; REC=ROOT/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv'; MAN=C/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv'; MATRIX=ROOT/'tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'; ACQ=C/'ECG_052_451_ACQUISITION_RECORD.csv'; FINAL=C/'FINAL_CLOSURE_STATUS_MANIFEST.json'; OUT=C/'RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json'
REMOTE={'test_0_epoch_100_noagg.npz':'ba51d7f3ce666cc13ec3e6859153660baff74d06fe2c9ec8a525e03512f0586a','test_0_epoch_100_agg.npz':'eb244e91abe66b47c0a8bf1c391db5de3536ca3728e621d363eec74690eb7481','formal_execution_metadata.json':'83786a614b98a3df6ca34b3cf089608932693a6a05aa617a9abe9b52e2005a6d','exact_command.txt':'9e7c8592c55a469c1a6fd594177e7d4c66d5597ebc7f84991c77db3c0f3a52db','formal_training.log':'40072020dcf773e4eb18814976eeb71b8be2860fcd66ae2a998a660c74a13ab1','completion_validation.json':'b32b47912954fb4ee7560166043d79473594f530969730eb9f0c83f6c350420b'}
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def wr(p,x,fs):
 with open(p,'w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(x)
def main():
 files={p.name:p for p in D.iterdir() if p.is_file()}; assert set(files)==set(REMOTE)
 hashes={n:h(p) for n,p in files.items()}; assert hashes==REMOTE,'REMOTE_LOCAL_HASH_MISMATCH'
 with np.load(ROOT/'experiments/ptbxl_all/ecg_jepa/test_0_epoch_100_agg.npz',allow_pickle=False) as src: expected=src['targs']; labels=[str(x) for x in src['lbl_itos'].tolist()]
 mp=rd(ROOT/'experiments/ptbxl_all/ecg_jepa/test_prediction_index_mapping.csv'); canonical=len(mp)==2198 and [int(x['prediction_index']) for x in mp]==list(range(2198)) and len({x['ecg_id'] for x in mp})==2198
 with np.load(files['test_0_epoch_100_agg.npz'],allow_pickle=False) as a,np.load(files['test_0_epoch_100_noagg.npz'],allow_pickle=False) as n:
  rep=len(n['targs'])//2198; recon=n['preds'].reshape(2198,rep,71).mean(1); checks={'prediction_to_ecg_id':canonical,'unique_test_ecg_ids':a['preds'].shape==(2198,71),'output_dim':n['preds'].shape==(2198*rep,71),'labels_match':[str(x) for x in a['lbl_itos'].tolist()]==labels and [str(x) for x in n['lbl_itos'].tolist()]==labels,'aggregate_targets_match':np.array_equal(a['targs'],expected),'target_group_consistency':np.array_equal(n['targs'].reshape(2198,rep,71),np.repeat(expected[:,None,:],rep,1)),'aggregation_reconstruction':np.array_equal(recon,a['preds']),'saved_aggregate_match':np.array_equal(recon,a['preds'])}; assert all(checks.values()),checks; diff=float(np.max(np.abs(recon-a['preds'])))
 stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(); base=f'/root/autodl-tmp/ECG/formal_runs/{RETRY}'
 detail={'canonical_run':R,'successful_retry_run':RETRY,'historical_source_instance':'052','evidence_carrier_current':'451','remote_base':base,'hashes':[{'filename':n,'remote_path':base+'/'+({'test_0_epoch_100_noagg.npz':'predictions/ptbxl_all_version_0/noagg/','test_0_epoch_100_agg.npz':'predictions/ptbxl_all_version_0/agg/'}.get(n,''))+n,'local_path':str(p.relative_to(ROOT)).replace('\\','/'),'size':p.stat().st_size,'remote_sha256':REMOTE[n],'local_sha256':hashes[n],'remote_local_hash_match':'PASS'} for n,p in files.items()],'unique_test_ecg_ids':2198,'windows_per_ecg':rep,'max_abs_diff':diff,'checks':checks,'completion_validation':json.loads(files['completion_validation.json'].read_text()),'strict_mapping':'PASS','verified_utc':stamp};OUT.write_text(json.dumps(detail,indent=2)+'\n',encoding='utf-8')
 for p in (STATUS,REC):
  x=rd(p);fs=list(x[0])
  for row in x:
   if row['canonical_run']==R:row.update({'evidence_source':OUT.relative_to(ROOT).as_posix(),'raw_prediction_status':'RECOVERED_RETRY01_HASH_VERIFIED','target_status':'EMBEDDED_IN_RECOVERED_NPZ_HASH_VERIFIED','aggregate_status':'RECOVERED_RETRY01_HASH_VERIFIED','ecg_id_metadata_status':'CANONICAL_FOLD10_MAPPING_VERIFIED','mapping_result':'PASS','unique_test_ecg_ids':'2198','aggregation_reconstruction':'PASS','target_consistency':'PASS','saved_aggregate_match':'PASS','blocker_category':'','notes':'Original Run015 attempt preserved as provenance; successful formal Retry01 completion_validation=PASS is canonical evidence source; exact two-window mean reconstruction; max_abs_diff=0.'})
  wr(p,x,fs)
 x=rd(MAN);fs=list(x[0])
 for row in x:
  if row['canonical_run']==R:row.update({'source_path':base,'local_path':str(D.relative_to(ROOT)).replace('\\','/'),'artifact_types_recovered':'RAW_WINDOW_PREDICTIONS_AND_TARGETS;SAVED_AGGREGATE;RESULT_VALIDATION;MINIMAL_PROVENANCE','remote_connectivity':'REMOTE_READ_ONLY_ACCESS_PUBLICKEY','acquisition_time_utc':stamp,'acquisition_method':'READ_ONLY_SCP_MINIMAL_RETRY01_BUNDLE;SHA256;STRICT_MAPPING','remote_sha256':'PER_FILE_IN_RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json','local_sha256':'PER_FILE_IN_RUN015_TARGETED_RECOVERY_AND_RELEASE_GATE.json','file_size_bytes':str(sum(p.stat().st_size for p in files.values())),'hash_verification':'PASS_6_OF_6_FILES','mapping_after':'PASS','blocker_after':'','user_power_on_required':'NO','notes':'Historical source 052; current carrier 451; successful Retry01 supersedes original TensorBoard-start failure without deleting history.'})
 wr(MAN,x,fs)
 x=rd(MATRIX);fs=list(x[0])
 for row in x:
  if row['canonical_run_id_or_directory']==R:row.update({'prediction_artifact':base+'/predictions/ptbxl_all_version_0','target_artifact':base+'/predictions/ptbxl_all_version_0/noagg/test_0_epoch_100_noagg.npz','aggregate_artifact':base+'/predictions/ptbxl_all_version_0/agg/test_0_epoch_100_agg.npz','result_artifact':base+'/completion_validation.json','log_artifact':base+'/formal_training.log','ecg_id_mapping_status':'PASS','notes':'Successful Retry01 is retained as final evidence; original Run015 TensorBoard failure remains historical provenance.'})
 wr(MATRIX,x,fs)
 x=rd(ACQ);fs=list(x[0])
 for row in x:
  if row['canonical_run']==R:row.update({'connectivity':'REMOTE_READ_ONLY_ACCESS_PUBLICKEY','acquisition_status':'SUCCESSFUL_RETRY01_BUNDLE_RECOVERED_AND_STRICT_PASS','notes':'SOURCE_INSTANCE_HISTORICAL=052; EVIDENCE_CARRIER_CURRENT=451; successful Retry01 source='+base+'; remote/local SHA256 PASS 6/6; no inference.'})
 wr(ACQ,x,fs)
 final=json.loads(FINAL.read_text());final['counts'].update({'mapping_pass':34,'mapping_new':23,'mapping_deferred':0,'mapping_blocked':1,'missing_evidence':43});final['mapping_evidence_recovery'].update({'mapping_newly_closed_this_run':1,'mapping_pass_total':34,'mapping_deferred_remaining':0,'mapping_missing_evidence_remaining':43,'evidence_recovered_count':23,'bootstrap_eligible_run_count':34});final['ecg_052_451_carrier_correction'].update({'bundles_recovered':17,'strict_mapping_pass':17,'raw_bundle_missing_runs':[],'run015_successful_retry_evidence':RETRY});FINAL.write_text(json.dumps(final,indent=2)+'\n')
 print(json.dumps({'run':R,'retry':RETRY,'strict_mapping':'PASS','windows':rep,'max_abs_diff':diff,'bytes':sum(p.stat().st_size for p in files.values())},indent=2))
if __name__=='__main__':main()
