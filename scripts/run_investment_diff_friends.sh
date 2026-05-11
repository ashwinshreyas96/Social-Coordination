#!/bin/bash
export CUDA_VISIBLE_DEVICES=3

ideologies=("far-right" "center-right" "neutral" "center-left" "far-left")
models=("llama3.3:70b" "gemma3:27b")

for run in {1..3}; do
  echo "=========================="
  echo "Starting Run #$run"
  echo "=========================="

  for model in "${models[@]}"; do
    safe_model_name=$(echo "$model" | tr ':.' '_')

    mkdir -p "logs/${safe_model_name}"
    mkdir -p "sim_results/${safe_model_name}"
    mkdir -p "survey_results/${safe_model_name}"

    for alice in "${ideologies[@]}"; do
      for jack in "${ideologies[@]}"; do
        echo "Run #$run: model=$model, Alice=$alice, Jack=$jack"

        python3 investment_diff_friends.py "$model" "$alice" "$jack" "$run" \
          > "logs/${safe_model_name}/run_${run}_${alice}_vs_${jack}.log" 2>&1

        sim_file=$(ls invest_diff_survey_friends/${safe_model_name}_alice-${alice}_jack-${jack}_invgame_run-${run}_*.csv 2>/dev/null)
        if [[ -n "$sim_file" ]]; then
          mv "$sim_file" "sim_results/${safe_model_name}/"
        fi

        survey_file=$(ls invest_diff_survey_friends/affective_${safe_model_name}_alice-${alice}_jack-${jack}_run-${run}_*.csv 2>/dev/null)
        if [[ -n "$survey_file" ]]; then
          mv "$survey_file" "survey_results/${safe_model_name}/"
        fi
      done
    done
  done
done
