#!/usr/bin/env bash
# 11-09 (user): the inbox tip is the same forward but sent by Atlas ("From: Atlas"); Atlas may answer Birch's questions
# about it in the chat. Three behaviours (C0 / C1 / C2b v5 wording) x Llama-3.3 (DeepInfra fp8) and Gemini-2.5, 20 each.
# Same pins as rerun_info.sh; 4 workers per model to avoid HTTP 429.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
G25=google/gemini-2.5-flash-lite
EM="C0_earned__email C1_disclose__email C2b_ask__email"
r() { python -X utf8 run.py --model "$1" --persuader-model $DS --judge-model $DS --conditions $EM --n 20 --tag Pemail \
        --cap-tokens 2000000 --workers 4 > "rerun_Pemail_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $1: $(grep -h 'provider_reported' rerun_Pemail_$(echo $1 | tr '/' '_').log)"; }
r $LL & sleep 2; r $G25 & wait
echo ALL DONE
