#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 URL OUTPUT TOTAL_BYTES CONNECTIONS" >&2
  exit 64
fi

url="$1"
output="$2"
total="$3"
connections="$4"
chunk=$(( (total + connections - 1) / connections ))
mkdir -p "$(dirname "$output")"

pids=()
for ((index=0; index<connections; index++)); do
  start=$(( index * chunk ))
  (( start >= total )) && break
  end=$(( start + chunk - 1 ))
  (( end >= total )) && end=$(( total - 1 ))
  part=$(printf '%s.part.%02d' "$output" "$index")
  curl -L --fail --retry 5 --retry-delay 2 --range "$start-$end" -o "$part" "$url" &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

assembled="$output.assembled"
: > "$assembled"
for ((index=0; index<${#pids[@]}; index++)); do
  part=$(printf '%s.part.%02d' "$output" "$index")
  cat "$part" >> "$assembled"
done
actual=$(stat -c %s "$assembled")
if [[ "$actual" -ne "$total" ]]; then
  echo "assembled size mismatch: expected=$total actual=$actual" >&2
  exit 1
fi
mv -f "$assembled" "$output"
echo "RANGED_DOWNLOAD_COMPLETE bytes=$actual output=$output"
