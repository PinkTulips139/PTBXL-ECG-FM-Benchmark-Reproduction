"""Read-only, lossless projection of existing 780 PTB-XL fold-10 metadata."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "execution_control" / "PTBXL_FINAL_CLOSURE" / "mapping_evidence" / "canonical_ptbxl_metadata"
OUT = OUT_DIR / "ptbxl_fold10_sub_super_mapping_metadata.json"
MANIFEST = OUT_DIR / "ptbxl_fold10_sub_super_mapping_metadata_acquisition.json"
REMOTE_DF_SHA = "1484361a48b493dbdf32f683819574f25c7e8a669f5b76193f2f3ae94a1e949f"
REMOTE_LABELS_SHA = "bff316e0f084433b58ef5730ce773a41769576a24ba6bbe9b6889dfb8731294e"

REMOTE_SCRIPT = r'''/root/miniconda3/bin/python - <<'PY'
import json, pickle
import pandas as pd
root='/root/autodl-tmp/ECG/data/processed/ptb-xl/records500'
df=pd.read_pickle(root+'/df.pkl')
with open(root+'/lbl_itos.pkl','rb') as f: labels=pickle.load(f)
test=df[df.strat_fold==10].sort_index()
rows=[]
for ecg_id, row in test.iterrows():
    rows.append({'ecg_id':int(ecg_id),'patient_id':int(row.patient_id),'strat_fold':int(row.strat_fold),'label_diag_subclass_filtered_numeric':[int(x) for x in row.label_diag_subclass_filtered_numeric],'label_diag_superclass_filtered_numeric':[int(x) for x in row.label_diag_superclass_filtered_numeric]})
print(json.dumps({'source':'/root/autodl-tmp/ECG/data/processed/ptb-xl/records500','rows':rows,'label_diag_subclass':[str(x) for x in labels['label_diag_subclass']],'label_diag_superclass':[str(x) for x in labels['label_diag_superclass']]},separators=(',',':')))
PY'''

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    encoded = __import__('base64').b64encode(REMOTE_SCRIPT.encode()).decode()
    cmd = f"echo {encoded} | base64 -d | bash"
    proc = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-i", r"C:\Users\86151\.ssh\ecg_autodl_573", "-p", "24159", "root@connect.westc.seetacloud.com", cmd], check=True, capture_output=True)
    payload = json.loads(proc.stdout)
    if len(payload["rows"]) != 2198 or len({x["ecg_id"] for x in payload["rows"]}) != 2198:
        raise RuntimeError("fold-10 metadata projection is not 2,198 unique ECG IDs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest = {"source_instance":"780","source_df_path":"/root/autodl-tmp/ECG/data/processed/ptb-xl/records500/df.pkl","source_df_sha256":REMOTE_DF_SHA,"source_lbl_itos_path":"/root/autodl-tmp/ECG/data/processed/ptb-xl/records500/lbl_itos.pkl","source_lbl_itos_sha256":REMOTE_LABELS_SHA,"local_path":str(OUT.relative_to(ROOT)).replace("\\", "/"),"local_sha256":sha(OUT),"file_size_bytes":OUT.stat().st_size,"content":"lossless fold-10 projection only; ecg_id/order and existing filtered numeric labels; no signals or model output","remote_local_hash_match":"NOT_APPLICABLE_STREAMED_LOSSLESS_PROJECTION","acquired_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat()}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__': main()
