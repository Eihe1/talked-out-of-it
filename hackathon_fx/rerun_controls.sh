#!/usr/bin/env bash
# 11-08 late (user): C0 controls (no chat / note without Atlas's USD/JPY profit / no tip), ablation 10 -> 20 per
# cell, and a reasoning-on gemini-2.5 pilot (to read reasoning traces). Pinned providers as in §13.6-13.7.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
G25=google/gemini-2.5-flash-lite
ABL5="C0_earned C1_disclose C2a_hint C2b_ask__v5 C2c_ask_split__v5 C2d_ask_threat__v5 C2e_full__v5"
CTL="C0_earned__nochat C0_earned__noatlas C0_earned__notip"
CW="$LL=coreweave/fp16"
r() { python -X utf8 run.py --model "$1" --persuader-model $DS --judge-model $DS --conditions $2 --n $3 --tag "$4" $5 \
        --cap-tokens 4000000 --workers 6 > "rerun_$4_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $4 $1: $(grep -h 'provider_reported' rerun_$4_$(echo $1 | tr '/' '_').log)"; }
chainA() { r $LL "$CTL" 20 Pctl ""; r $LL "$ABL5" 10 Pabl ""; }
chainB() { r $LL "$CTL" 20 CWctl "--pin $CW"; r $LL "$ABL5" 10 CWabl "--pin $CW"; }
chainC() { r $G25 "$CTL" 20 Pctl ""; r $G25 "$ABL5" 10 Pabl ""; }
chainD() { r $G25 "C0_earned C1_disclose C2b_ask C2e_full__v5" 5 Rthink "--reasoning-on $G25"; }
chainA & sleep 2; chainB & sleep 2; chainC & sleep 2; chainD & wait
echo ALL DONE
