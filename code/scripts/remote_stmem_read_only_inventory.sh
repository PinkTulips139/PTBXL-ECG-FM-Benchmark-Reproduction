#!/usr/bin/env bash
# stdin-only, read-only remote inventory for one ST-MEM instance.
set -u
printf 'REMOTE_READ_ONLY_ACCESS=YES\n'
printf 'ACTIVE_PROCESS_CHECK\n'
ps -eo pid=,args= | grep -E '[p]ython.*(main_lite|controller|ptbxl)' || true
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader 2>/dev/null || true
printf 'CANONICAL_DIRS\n'
for d in "$@"; do
  printf 'RUN_DIR=%s\n' "$d"
  if [ -d "$d" ]; then
    find "$d" -maxdepth 3 -type f -printf '%p|%s|%TY-%Tm-%TdT%TH:%TM:%TS\n' | sort
  else
    printf 'MISSING_DIR\n'
  fi
done
