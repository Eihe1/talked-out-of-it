#!/usr/bin/env bash
# llama-3.3 rerun on a second pinned provider (user, 11-08): CoreWeave fp16 instead of DeepInfra fp8.
# Everything else as rerun_pinned.sh (DeepSeek persuader/judge on DeepInfra with reasoning). Directory suffix _CW.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
PIN="$LL=coreweave/fp16"
ABL5="C0_earned C1_disclose C2a_hint C2b_ask__v5 C2c_ask_split__v5 C2d_ask_threat__v5 C2e_full__v5"
V7="C2b_ask C2c_ask_split C2d_ask_threat C2e_full"
V8="C3a_reframe C3b_social C3c_authority C3d_minimize C3e_reciprocity C3f_urgency C1_disclose__nopress C2b_ask__nopress C1_disclose__strict C2b_ask__strict"
r() { python -X utf8 run.py --model $LL --persuader-model $DS --judge-model $DS --conditions $1 --n $2 --pin "$PIN" \
        --tag "CW$3" --cap-tokens 4000000 --workers 6 > "rerunCW_$3.log" 2>&1; echo "done $3: $(grep -h 'provider_reported' rerunCW_$3.log)"; }
chainA() { r "$ABL5" 10 abl; r "$V7" 10 v7; }
chainB() { r "$V8" 10 v8; r "C2b_ask C3a_reframe" 20 conf; }
chainA & sleep 2; chainB & wait
echo ALL DONE
