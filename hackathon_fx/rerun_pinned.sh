#!/usr/bin/env bash
# Reruns with pinned providers + explicit DeepSeek reasoning (user, 11-08). Directory suffix _P.
cd "$(dirname "$0")"
DS=deepseek/deepseek-v4-flash
ABL5="C0_earned C1_disclose C2a_hint C2b_ask__v5 C2c_ask_split__v5 C2d_ask_threat__v5 C2e_full__v5"
V7="C2b_ask C2c_ask_split C2d_ask_threat C2e_full"
V8="C3a_reframe C3b_social C3c_authority C3d_minimize C3e_reciprocity C3f_urgency C1_disclose__nopress C2b_ask__nopress C1_disclose__strict C2b_ask__strict"
M="C3a_reframe C3b_social C3c_authority C3d_minimize C3e_reciprocity C3f_urgency"
SP="C0_earned C1_disclose C2b_ask__v5 C2e_full__v5"
r() { python -X utf8 run.py --model "$1" --persuader-model "$2" --judge-model $DS --conditions $3 --n $4 --tag "P$5" --cap-tokens 4000000 --workers 6 > "rerunP_$5_$(echo $1 | tr '/' '_').log" 2>&1; echo "done $5 $1: $(grep -h 'provider_reported' rerunP_$5_$(echo $1 | tr '/' '_').log)"; }
chainA() { for M_ in meta-llama/llama-3.3-70b-instruct; do r $M_ $DS "$ABL5" 10 abl; r $M_ $DS "$V7" 10 v7; r $M_ $DS "$V8" 10 v8; r $M_ $DS "C2b_ask C3a_reframe" 20 conf; done; }
chainB() { for M_ in google/gemini-2.5-flash-lite; do r $M_ $DS "$ABL5" 10 abl; r $M_ $DS "$V7" 10 v7; r $M_ $DS "$V8" 10 v8; r $M_ $DS "C2b_ask C3a_reframe" 20 conf; done; }
chainC() { r google/gemini-3.1-flash-lite $DS "$ABL5" 5 abl; r google/gemini-3.1-flash-lite $DS "$M" 5 v8;
           r google/gemini-3-flash-preview $DS "$SP" 5 fixed; r anthropic/claude-haiku-5.5 $DS "$SP" 5 fixed; }
chainD() { r meta-llama/llama-3.3-70b-instruct meta-llama/llama-3.3-70b-instruct "$SP" 5 self;
           r meta-llama/llama-4-maverick meta-llama/llama-4-maverick "$SP" 5 self;
           r meta-llama/llama-4-maverick $DS "$SP" 5 fixed;
           for d in runs/20261108-063510_gemini-25-flash-lite runs/20261108-063801_gemini-31-flash-lite runs/20261108-063808_gemini-3-flash-preview runs/20261108-064823_claude-haiku-55; do
             python -X utf8 -c "import judge; judge.rejudge('$d/episodes.jsonl', '$DS', out_name='episodes_rejudged_P.jsonl')"; done; }
chainA & sleep 2; chainB & sleep 2; chainC & sleep 2; chainD & wait
echo ALL DONE
