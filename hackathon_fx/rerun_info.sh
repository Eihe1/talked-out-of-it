#!/usr/bin/env bash
# 11-09 (user, after the senior's review): information-source experiment. Pure information (tip in the inbox, no chat,
# no Atlas profit in the note) and a 2 x 3 design: tip source (inbox + Atlas / Atlas only) x Atlas's behaviour
# (passes the tip on / + discloses its own trade / + explicit request, v5 wording). Same pins as the main ablation:
# persuader and judge DeepSeek-V4-Flash on DeepInfra with reasoning on; Llama-3.3 on DeepInfra fp8. 20 per cell.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
G25=google/gemini-2.5-flash-lite
INFO="C0_earned__pureinfo C0_earned__tell C1_disclose__tell C2b_ask__tell C0_earned__peer C1_disclose__peer C2b_ask__peer"
r() { python -X utf8 run.py --model "$1" --persuader-model $DS --judge-model $DS --conditions $2 --n $3 --tag "$4" $5 \
        --cap-tokens 4000000 --workers 8 > "rerun_$4_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $4 $1: $(grep -h 'provider_reported' rerun_$4_$(echo $1 | tr '/' '_').log)"; }
r $LL "$INFO" 20 Pinfo "" & sleep 2; r $G25 "$INFO" 20 Pinfo "" & wait
echo ALL DONE
