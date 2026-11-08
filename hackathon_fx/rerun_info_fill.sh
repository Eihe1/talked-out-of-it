#!/usr/bin/env bash
# 11-09: refill the 23 Llama-3.3 episodes of rerun_info.sh that crashed on HTTP 429 (15 C1_disclose__peer, 8 C2b_ask__peer).
# Same settings, fewer workers. Crashed episodes are excluded by final_tables.load_suffix.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
for spec in "C1_disclose__peer 15" "C2b_ask__peer 8"; do
  set -- $spec
  python -X utf8 run.py --model $LL --persuader-model $DS --judge-model $DS --conditions $1 --n $2 --tag Pinfo \
    --cap-tokens 1000000 --workers 3 > "rerun_Pinfo_fill_$1.log" 2>&1
  echo "done $1: $(grep -h 'provider_reported' rerun_Pinfo_fill_$1.log)"
done
