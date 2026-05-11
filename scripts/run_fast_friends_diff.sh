#!/bin/bash
export CUDA_VISIBLE_DEVICES=1

ideologies=("far-right" "center-right" "neutral" "center-left" "far-left")
models=("llama3.3:70b" "gemma3:27b")

for run in {1..3}; do
  echo "=========================="
  echo "Starting Run #$run"
  echo "=========================="

  for model in "${models[@]}"; do

    # Make model-safe name
    safe_model_name=$(echo "$model" | tr ':.' '_')

    # Create directories for this model
    mkdir -p "logs/${safe_model_name}"
    mkdir -p "sim_results/${safe_model_name}"
    mkdir -p "survey_results/${safe_model_name}"

    for alice in "${ideologies[@]}"; do
      for jack in "${ideologies[@]}"; do

        echo "Run #$run: model=$model, Alice=$alice, Jack=$jack"

        # Run simulation
        python3 fast_friends_diff.py "$model" "$alice" "$jack" "$run" \
          > "logs/${safe_model_name}/run_${run}_${alice}_vs_${jack}.log" 2>&1

        # Move generated files into correct folders
        # Simulation CSV (starts with fast_friends_diff/)
        sim_file=$(ls fast_friends_diff/${safe_model_name}_alice-${alice}_jack-${jack}_run-${run}_*.csv 2>/dev/null)
        if [[ -n "$sim_file" ]]; then
          mv "$sim_file" "sim_results/${safe_model_name}/"
        fi

        # Survey CSV (starts with affective/)
        survey_file=$(ls fast_friends_diff/affective_${safe_model_name}_alice-${alice}_jack-${jack}_run-${run}_*.csv 2>/dev/null)
        if [[ -n "$survey_file" ]]; then
          mv "$survey_file" "survey_results/${safe_model_name}/"
        fi

      done
    done
  done
done
