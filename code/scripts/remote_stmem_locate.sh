#!/usr/bin/env bash
# stdin-only, read-only directory locator restricted to the formal-runs root.
set -u
root="$1"
printf 'FORMAL_ROOT=%s\n' "$root"
if [ ! -d "$root" ]; then
  printf 'FORMAL_ROOT_MISSING\n'
  exit 0
fi
find "$root" -maxdepth 4 \( -type d -o -type f \) \
  \( -iname '*st*mem*' -o -iname '*run07*' -o -iname '*run08*' -o -iname '*run09*' -o -iname '*retry*03*' \) \
  -printf '%y|%p|%s|%TY-%Tm-%TdT%TH:%TM:%TS\n' | sort
