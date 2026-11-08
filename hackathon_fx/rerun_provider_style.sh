#!/usr/bin/env bash
# 11-08 late (user): (1) llama on AkashML fp8 (same precision as DeepInfra, other provider) in the explicit-
# persuasion cells; (2) deepseek-v4-flash-0731 as PERSUADER on DeepInfra fp8 / BaseTen fp8 / BaseTen fp32
# (targets llama DeepInfra, gemini-2.5; C2b vs C3a); (3) persuader writing styles (v7 C2b + one style).
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
Q=deepseek/deepseek-v4-flash-0731
LL=meta-llama/llama-3.3-70b-instruct
G25=google/gemini-2.5-flash-lite
PUSH="C2b_ask__v5 C2c_ask_split__v5 C2d_ask_threat__v5 C2e_full__v5 C2b_ask C2c_ask_split C2d_ask_threat C2e_full"
STY="C4a_formal C4b_casual C4c_terse C4d_emotional"
r() { python -X utf8 run.py --model "$1" --persuader-model "$2" --judge-model $DS --conditions $3 --n $4 --tag "$5" $6 \
        --cap-tokens 4000000 --workers 4 > "rerun_$5_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $5 $1: $(grep -h 'provider_reported' rerun_$5_$(echo $1 | tr '/' '_').log)"; }
chainA() { r $LL $DS "$PUSH" 10 AKpush "--pin $LL=akashml/fp8"; }
chainB() { r $LL $Q "C2b_ask C3a_reframe" 20 QP_di "--pin $Q=deepinfra/fp8"; r $G25 $Q "C2b_ask C3a_reframe" 20 QP_di "--pin $Q=deepinfra/fp8"; }
chainC() { r $LL $Q "C2b_ask C3a_reframe" 20 QP_b8 "--pin $Q=baseten/fp8"; r $G25 $Q "C2b_ask C3a_reframe" 20 QP_b8 "--pin $Q=baseten/fp8"; }
chainD() { r $LL $Q "C2b_ask C3a_reframe" 20 QP_b32 "--pin $Q=baseten/fp32"; r $G25 $Q "C2b_ask C3a_reframe" 20 QP_b32 "--pin $Q=baseten/fp32"; }
chainE() { r $LL $DS "$STY" 20 Sty ""; r $G25 $DS "$STY" 20 Sty ""; }
chainA & sleep 2; chainB & sleep 2; chainC & sleep 2; chainD & sleep 2; chainE & wait
echo ALL DONE
