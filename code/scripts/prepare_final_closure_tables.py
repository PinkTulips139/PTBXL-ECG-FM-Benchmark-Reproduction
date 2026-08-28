import csv,json
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; T=R/'tables'; C=R/'execution_control/PTBXL_FINAL_CLOSURE'
def rd(p):
 with open(p,encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def key(x):return x['dataset'],x['model'],x['mode']
def write_csv(p,rows):
 with open(p,'w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 status={key(x):x for x in rd(T/'PTBXL_GLOBAL_MAPPING_CLOSURE_STATUS.csv')}; matrix=rd(T/'PTBXL_GLOBAL_FORMAL_RUN_COMPLETION_MATRIX.csv'); boot={key(x):x for x in rd(C/'FINAL_CPU_BOOTSTRAP_77_RUNS.csv')}
 paper={x['model']:x['paper_macro_auroc'] for x in rd(T/'PTBXL_ALL_REPRODUCTION_RESULTS.csv')}
 rows=[]
 for m in matrix:
  k=key(m);s=status[k];b=boot.get(k,{})
  paper_v=paper.get(m['model'],'NOT_AVAILABLE_IN_LOCAL_PAPER_EXTRACT') if m['dataset']=='ptbxl_all' and m['mode']=='Finetuning' else 'NOT_APPLICABLE_OR_NOT_LOCATED'
  ours=b.get('point_macro_auroc') or m['ours_macro_auroc']
  diff=''
  try:diff=repr(float(ours)-float(paper_v))
  except:pass
  rows.append({'dataset':m['dataset'],'model':m['model'],'mode':m['mode'],'canonical_run':m['canonical_run_id_or_directory'],'paper_macro_auroc':paper_v,'ours_macro_auroc':ours,'difference_ours_minus_paper':diff,'ci95_low':b.get('ci_low',''),'ci95_high':b.get('ci_high',''),'best_epoch':m['best_epoch'],'runtime':m['runtime'],'mapping_status':s['mapping_result'],'bootstrap_status':b.get('bootstrap_status','NOT_ELIGIBLE_HISTORICAL_BLOCKER'),'execution_authority':m['execution_authority'],'provenance':b.get('provenance',s['evidence_source'])})
 summary=[]
 for r in rows:
  summary.append({'dataset':r['dataset'],'model':r['model'],'mode':r['mode'],'canonical_run':r['canonical_run'],'mapping_status':r['mapping_status'],'bootstrap_status':r['bootstrap_status'],'point_macro_auroc':r['ours_macro_auroc'],'ci_low':r['ci95_low'],'ci_high':r['ci95_high'],'iterations':'1000' if r['bootstrap_status']=='COMPLETED' else '','helper_path':'upstream/ecg-fm-benchmarking/code/clinical_ts/utils/bootstrap_utils.py::empirical_bootstrap' if r['bootstrap_status']=='COMPLETED' else '','provenance':r['provenance']})
 write_csv(C/'FINAL_BOOTSTRAP_SUMMARY.csv',summary);(C/'FINAL_BOOTSTRAP_SUMMARY.json').write_text(json.dumps({'generated_utc':datetime.now(timezone.utc).isoformat(),'completed':sum(x['bootstrap_status']=='COMPLETED' for x in summary),'blocked':sum('BLOCKED' in x['bootstrap_status'] for x in summary),'runs':summary},indent=2)+'\n')
 names={'ptbxl_all':'DRAFT_TABLE3_PTBXL_ALL.csv','ptbxl_sub':'DRAFT_TABLE4_PTBXL_SUB.csv','ptbxl_super':'DRAFT_TABLE5_PTBXL_SUPER.csv'}
 for d,n in names.items():write_csv(T/n,[x for x in rows if x['dataset']==d])
 report=C/'FINAL_CLOSURE_REPORT_DRAFT.md'
 report.write_text(f'''# ECG Foundation Model Benchmark Reproduction — Final Closure Draft\n\n## Scope and authority\n\n- Locked executable authority: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`.\n- Formal scope: 78 entries across PTB-XL(all), PTB-XL(sub), and PTB-XL(super).\n- Formal completion: 78/78.\n\n## Mapping closure\n\n- Strict mapping PASS: 77/78.\n- Historical blocker: `PTBXL_ALL_ECGFOUNDER_FROZEN_FORMAL_RUN_001`; preserved historical target-group consistency failure. No artifact or sidecar was changed.\n\n## Bootstrap closure\n\n- Contract: 1,000 bootstrap iterations, 95% CI, ECG-record unit, N=2,198, record-level aggregated Macro AUROC.\n- Accepted helper: `clinical_ts.utils.bootstrap_utils.empirical_bootstrap`.\n- Completed: 72; blocked for existing provenance: 5; failed: 0.\n\n## Draft display provenance\n\n- Table 3 draft: `tables/DRAFT_TABLE3_PTBXL_ALL.csv`.\n- Table 4 draft: `tables/DRAFT_TABLE4_PTBXL_SUB.csv`.\n- Table 5 draft: `tables/DRAFT_TABLE5_PTBXL_SUPER.csv`.\n- Bootstrap summary: `execution_control/PTBXL_FINAL_CLOSURE/FINAL_BOOTSTRAP_SUMMARY.csv`.\n\n## Limitations\n\nFive mapping-PASS PTB-XL(all) entries remain bootstrap-blocked because no canonical aggregate/target pair was uniquely locatable from local provenance. This is not imputed or reconstructed.\n\n*Draft only; not a release or manuscript-final report.*\n''',encoding='utf-8')
 print(json.dumps({'rows':len(rows),'bootstrap_completed':sum(x['bootstrap_status']=='COMPLETED' for x in summary),'bootstrap_blocked':sum('BLOCKED' in x['bootstrap_status'] for x in summary)}))
if __name__=='__main__':main()
