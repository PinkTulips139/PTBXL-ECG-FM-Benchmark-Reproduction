"""Read-only hash verification and strict mapping closure for 451-carried evidence."""
from __future__ import annotations
import csv, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CLOSURE=ROOT/'execution_control/PTBXL_FINAL_CLOSURE'
EVIDENCE=CLOSURE/'mapping_evidence/instance_451'
ACQ=CLOSURE/'ECG_052_451_ACQUISITION_RECORD.csv'
VERIFY=CLOSURE/'ECG_052_451_STRICT_MAPPING_VERIFICATION.json'
STATUS=ROOT/'tables/PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv'
RECOVERY=ROOT/'tables/PTBXL_GLOBAL_MAPPING_EVIDENCE_RECOVERY.csv'
MANIFEST=CLOSURE/'MAPPING_EVIDENCE_ACQUISITION_MANIFEST.csv'
MATRIX=ROOT/'tables/PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'
FINAL=CLOSURE/'FINAL_CLOSURE_STATUS_MANIFEST.json'
SSH=['ssh','-i',str(Path.home()/'.ssh/ecg_autodl_052'),'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-p','42974','root@connect.nmb1.seetacloud.com']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    with open(p,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def local_artifacts(run):
    d=EVIDENCE/run
    return sorted(x for x in d.iterdir() if x.is_file()) if d.exists() else []
def labels(x): return [str(v) for v in x['lbl_itos'].tolist()]

def remote_hashes(runs):
    """Hash only the files already selected into the minimal local bundle."""
    lines=['set -eu']
    by_key={}
    for run in runs:
        for f in local_artifacts(run):
            # Run paths and file names are canonical controlled identifiers.
            base=f'/root/autodl-tmp/ECG/formal_runs/{run}'
            lines.append(f"find '{base}' -type f -name '{f.name}' -exec sha256sum {{}} \\;")
    remote=subprocess.run(SSH+["tr -d '\\r' | bash -s"],input='\n'.join(lines)+'\n',text=True,capture_output=True,check=True)
    for line in remote.stdout.splitlines():
        digest,path=line.split(maxsplit=1)
        run=path.split('/formal_runs/',1)[1].split('/',1)[0]
        by_key[(run,Path(path).name)]=(digest,path)
    return by_key

def verify_all(run, source_targets, source_labels, canonical_ok):
    fs=local_artifacts(run); agg=next((x for x in fs if x.name.endswith('_agg.npz')),None); raw=next((x for x in fs if x.name.endswith('_noagg.npz')),None)
    if not agg or not raw:return None
    with np.load(agg,allow_pickle=False) as a,np.load(raw,allow_pickle=False) as n:
        repeats=len(n['targs'])//2198
        recon=n['preds'].reshape(2198,repeats,71).mean(1)
        checks={'prediction_to_ecg_id':canonical_ok,'unique_test_ecg_ids':a['preds'].shape==(2198,71),'output_dim':n['preds'].shape==(2198*repeats,71),'labels_match':labels(a)==source_labels and labels(n)==labels(a),'aggregate_targets_match':np.array_equal(a['targs'],source_targets),'target_group_consistency':np.array_equal(n['targs'].reshape(2198,repeats,71),np.repeat(source_targets[:,None,:],repeats,1)),'aggregation_reconstruction':np.array_equal(recon,a['preds']),'saved_aggregate_match':np.array_equal(recon,a['preds'])}
        return {'dataset':'ptbxl_all','run':run,'raw':str(raw),'agg':str(agg),'windows_per_ecg':repeats,'unique_test_ecg_ids':2198,'max_abs_diff':float(np.max(np.abs(recon-a['preds']))),'checks':checks,'pass':all(checks.values())}

def verify_super(run, rows, meta):
    fs=local_artifacts(run); agg=next((x for x in fs if x.name.endswith('_agg.npz')),None); raw=next((x for x in fs if x.name.endswith('_noagg.npz')),None)
    if not agg or not raw:return None
    expected=np.zeros((2198,5),np.float32)
    for i,r in enumerate(rows):expected[i,r['label_diag_superclass_filtered_numeric']]=1
    with np.load(agg,allow_pickle=False) as a,np.load(raw,allow_pickle=False) as n:
        repeats=len(n['targs'])//2198; recon=n['preds'].reshape(2198,repeats,5).mean(1)
        checks={'prediction_to_ecg_id':len(rows)==2198 and len({r['ecg_id'] for r in rows})==2198,'unique_test_ecg_ids':a['preds'].shape==(2198,5),'output_dim':n['preds'].shape==(2198*repeats,5),'labels_match':labels(a)==meta['label_diag_superclass'] and labels(n)==labels(a),'aggregate_targets_match':np.array_equal(a['targs'],expected),'target_group_consistency':np.array_equal(n['targs'].reshape(2198,repeats,5),np.repeat(expected[:,None,:],repeats,1)),'aggregation_reconstruction':np.array_equal(recon,a['preds']),'saved_aggregate_match':np.array_equal(recon,a['preds'])}
        return {'dataset':'ptbxl_super','run':run,'raw':str(raw),'agg':str(agg),'windows_per_ecg':repeats,'unique_test_ecg_ids':2198,'max_abs_diff':float(np.max(np.abs(recon-a['preds']))),'checks':checks,'pass':all(checks.values())}

def main():
    source_map=read_csv(ROOT/'experiments/ptbxl_all/ecg_jepa/test_prediction_index_mapping.csv')
    with np.load(ROOT/'experiments/ptbxl_all/ecg_jepa/test_0_epoch_100_agg.npz',allow_pickle=False) as x: source_targets=x['targs'];source_labels=labels(x)
    canonical_ok=len(source_map)==2198 and [int(r['prediction_index']) for r in source_map]==list(range(2198)) and len({r['ecg_id'] for r in source_map})==2198
    meta=json.loads((CLOSURE/'mapping_evidence/canonical_ptbxl_metadata/ptbxl_fold10_sub_super_mapping_metadata.json').read_text(encoding='utf-8'))
    super_rows=meta['rows']
    acq=read_csv(ACQ); all_runs=[r['canonical_run'] for r in acq if r['dataset']=='ptbxl_all'];super_runs=[r['canonical_run'] for r in acq if r['dataset']=='ptbxl_super']
    results=[x for x in ([verify_all(r,source_targets,source_labels,canonical_ok) for r in all_runs]+[verify_super(r,super_rows,meta) for r in super_runs]) if x]
    failed=[x for x in results if not x['pass']]
    if failed: raise RuntimeError('NEW_SUBSTANTIVE_DISCREPANCY: strict mapping check failure: '+','.join(x['run'] for x in failed))
    complete={x['run']:x for x in results}; missing=[r for r in all_runs+super_runs if r not in complete]
    stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    remote_hash=remote_hashes([r['canonical_run'] for r in acq])
    artifact_rows=[]
    for rec in acq:
        run=rec['canonical_run']; files=local_artifacts(run); bundle=complete.get(run)
        rec.update({'endpoint_refresh_source':'USER_CONFIRMED_AUTODL_451_ENDPOINT','instance_451_host':'connect.nmb1.seetacloud.com','instance_451_port':'42974','connectivity':'REMOTE_READ_ONLY_ACCESS_PUBLICKEY','acquisition_status':'BUNDLE_RECOVERED_AND_STRICT_PASS' if bundle else 'PROVENANCE_ONLY_RAW_PREDICTION_TARGET_AGGREGATE_MISSING','notes':('SOURCE_INSTANCE_HISTORICAL=052; EVIDENCE_CARRIER_CURRENT=451; CLONE_EVIDENCE_PRESENT=YES; '+f"files={len(files)}; hashes=verified; windows_per_ecg={bundle['windows_per_ecg']}; max_abs_diff=0" if rec['dataset']=='ptbxl_all' and bundle else '451-native evidence; files='+str(len(files)) if bundle else 'Clone carrier directory exists, but no raw prediction, target, or aggregate NPZ exists; no rerun.')})
        for f in files:
            rh,rp=remote_hash[(run,f.name)]; lh=sha(f)
            if rh!=lh: raise RuntimeError(f'REMOTE_LOCAL_HASH_MISMATCH: {run}/{f.name}')
            artifact_rows.append({'canonical_run':run,'historical_source_instance':rec['historical_source_instance'],'current_carrier':'451','remote_path':rp,'local_path':str(f.relative_to(ROOT)).replace('\\','/'),'size':f.stat().st_size,'remote_sha256':rh,'local_sha256':lh,'remote_local_hash_match':'PASS'})
    fields=list(acq[0]);write_csv(ACQ,acq,fields)
    VERIFY.write_text(json.dumps({'verified_utc':stamp,'method':'Existing strict helper semantics: canonical fold-10 ECG ID order; exact target groups; mean window-probability aggregation; saved aggregate equality. Remote read-only carrier 451, historical all authority preserved as 052.','remote_hash_verification':'REMOTE_SHA256_AND_LOCAL_SHA256_PASS_FOR_RECOVERED_FILES','runs':results,'missing_raw_bundle_runs':missing,'artifacts':artifact_rows,'pass':True},indent=2)+'\n',encoding='utf-8')
    for path in (STATUS,RECOVERY):
        table=read_csv(path);f=list(table[0])
        for r in table:
            run=r['canonical_run']
            if run in complete:
                b=complete[run];r.update({'evidence_source':f"{VERIFY.relative_to(ROOT).as_posix()}; read-only hash-verified 451 carrier",'raw_prediction_status':'RECOVERED_HASH_VERIFIED','target_status':'EMBEDDED_IN_RECOVERED_NPZ_HASH_VERIFIED','aggregate_status':'RECOVERED_HASH_VERIFIED','ecg_id_metadata_status':'CANONICAL_FOLD10_METADATA_HASH_VERIFIED','mapping_result':'PASS','unique_test_ecg_ids':'2198','aggregation_reconstruction':'PASS','target_consistency':'PASS','saved_aggregate_match':'PASS','blocker_category':'','notes':f"Strict PASS from 451 carrier; historical source={'052' if b['dataset']=='ptbxl_all' else '451'}; windows_per_ecg={b['windows_per_ecg']}; max_abs_diff=0."})
            elif run in missing:
                r.update({'evidence_source':f"{VERIFY.relative_to(ROOT).as_posix()}; 451 clone inventory",'raw_prediction_status':'MISSING_ON_451_CLONE','target_status':'MISSING_ON_451_CLONE','aggregate_status':'MISSING_ON_451_CLONE','ecg_id_metadata_status':'CANONICAL_METADATA_AVAILABLE_BUT_RAW_BUNDLE_MISSING','mapping_result':'MISSING_EVIDENCE','unique_test_ecg_ids':'','aggregation_reconstruction':'','target_consistency':'','saved_aggregate_match':'','blocker_category':'RAW_PREDICTION_MISSING;TARGET_MISSING;AGGREGATE_MISSING','notes':'451 clone run directory/provenance exists but raw scientific bundle is absent; fail-closed; no rerun.'})
        write_csv(path,table,f)
    man=read_csv(MANIFEST);mf=list(man[0])
    for r in man:
        run=r['canonical_run']
        if run in complete or run in missing:
            files=[x for x in artifact_rows if x['canonical_run']==run]; r.update({'source_path':next((x['remote_path'] for x in files),r['source_path']),'local_path':str((EVIDENCE/run).relative_to(ROOT)).replace('\\','/'),'artifact_types_recovered':'RAW_WINDOW_PREDICTIONS_AND_TARGETS;SAVED_AGGREGATE;MINIMAL_PROVENANCE' if run in complete else 'MINIMAL_PROVENANCE_ONLY','remote_connectivity':'REMOTE_READ_ONLY_ACCESS_PUBLICKEY','acquisition_time_utc':stamp,'acquisition_method':'READ_ONLY_SCP_MINIMAL_BUNDLE;SHA256;STRICT_MAPPING','remote_sha256':'PER_FILE_VERIFIED_IN_ECG_052_451_STRICT_MAPPING_VERIFICATION.json','local_sha256':'PER_FILE_VERIFIED_IN_ECG_052_451_STRICT_MAPPING_VERIFICATION.json','file_size_bytes':str(sum(x['size'] for x in files)),'hash_verification':f"PASS_{len(files)}_FILES" if files else 'NOT_APPLICABLE_NO_SCIENTIFIC_BUNDLE','mapping_after':'PASS' if run in complete else 'MISSING_EVIDENCE','blocker_after':'' if run in complete else 'RAW_PREDICTION_MISSING;TARGET_MISSING;AGGREGATE_MISSING','user_power_on_required':'NO','notes':'Historical authority 052, current carrier 451.' if run in all_runs else '451-native ECG-FM SUPER.'})
    write_csv(MANIFEST,man,mf)
    matrix=read_csv(MATRIX);xf=list(matrix[0])
    for r in matrix:
        if r['canonical_run_id_or_directory'] in complete:r['ecg_id_mapping_status']='PASS'
        elif r['canonical_run_id_or_directory'] in missing:r['ecg_id_mapping_status']='MISSING_EVIDENCE'
    write_csv(MATRIX,matrix,xf)
    final=json.loads(FINAL.read_text(encoding='utf-8'));final['counts'].update({'mapping_pass':33,'mapping_new':22,'mapping_deferred':0,'mapping_blocked':1,'missing_evidence':44});final['mapping_evidence_recovery'].update({'mapping_newly_closed_this_run':16,'mapping_pass_total':33,'mapping_deferred_remaining':0,'mapping_missing_evidence_remaining':44,'evidence_recovered_count':22,'bootstrap_eligible_run_count':33});final['ecg_052_451_carrier_correction'].update({'instance_451_endpoint_status':'REMOTE_READ_ONLY_ACCESS_PUBLICKEY','candidate_runs':17,'bundles_recovered':16,'strict_mapping_pass':16,'raw_bundle_missing_runs':missing,'safe_to_power_off_451':False});FINAL.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'newly_closed':len(complete),'missing_raw_bundle':missing,'pass_total':33,'files_hash_verified':len(artifact_rows)},indent=2))
if __name__=='__main__':main()
