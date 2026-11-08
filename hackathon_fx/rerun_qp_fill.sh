#!/usr/bin/env bash
# Refill the 24 episodes of the 0731-persuader runs that failed with HTTP 429 on BaseTen (same tags, 2 workers).
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash; Q=deepseek/deepseek-v4-flash-0731
LL=meta-llama/llama-3.3-70b-instruct; G25=google/gemini-2.5-flash-lite
r() { python -X utf8 run.py --model "$1" --persuader-model $Q --judge-model $DS --conditions $2 --n $3 --tag "$4" --pin "$Q=$5" \
        --cap-tokens 1000000 --workers 2 > "rerun_fill_$4_$2_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $4 $2 $1: $(grep -h 'provider_reported' rerun_fill_$4_$2_$(echo $1 | tr '/' '_').log)"; }
r $LL C2b_ask 1 QP_b8 baseten/fp8; r $LL C3a_reframe 2 QP_b8 baseten/fp8
r $G25 C2b_ask 10 QP_b8 baseten/fp8; r $G25 C3a_reframe 3 QP_b8 baseten/fp8
r $G25 C2b_ask 7 QP_b32 baseten/fp32; r $G25 C3a_reframe 1 QP_b32 baseten/fp32
echo ALL DONE
