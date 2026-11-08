#!/usr/bin/env bash
# 11-08 late (user): controlled "safe exit" test. __exit = the inbox quotes the signal sheet / research note, so every
# episode knows the legitimate alternative. C0 / C1 / C2b (v7) x 20. Last experiment before writing.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
LL=meta-llama/llama-3.3-70b-instruct
G25=google/gemini-2.5-flash-lite
EX="C0_earned__exit C1_disclose__exit C2b_ask__exit"
r() { python -X utf8 run.py --model "$1" --persuader-model $DS --judge-model $DS --conditions $EX --n 20 --tag "$2" $3 \
        --cap-tokens 3000000 --workers 6 > "rerun_$2_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $2 $1: $(grep -h 'provider_reported' rerun_$2_$(echo $1 | tr '/' '_').log)"; }
r $G25 Xthink "--reasoning-on $G25" & sleep 2; r $LL Pexit "" & sleep 2; r $G25 Pexit "" & wait
echo ALL DONE
