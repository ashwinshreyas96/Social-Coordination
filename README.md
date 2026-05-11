# Social Coordination LLM Experiments

This repository packages the code set for the chapter **Affective Polarization in Large Language Models** from the attached draft.

The code is organized around three experiment families:

- **Affective probing / survey baselines**: ANES-style feeling thermometers, personality, trust, and in-group/out-group judgments.
- **Coordination games**: repeated restaurant selection tasks with and without shared identity cues.
- **Investment games**: trust-and-reciprocity style interactions with pre/post affective surveys.

The attached draft describes the use of Llama 3.3 70B and Gemma 3 27B, repeated prompting, and Ollama-based local inference for the survey and simulation workflows.

## Repository layout

```text
experiments/
  coordination/
    fast_friends_same.py
    fast_friends_diff.py
  investment/
    investment_same_survey.py
    investment_diff_survey.py
    investment_diff_friends.py
  legacy_pistacchio/
    pistacchio_same_survey.py
    pistacchio_different_survey.py
scripts/
  run_fast_friends_same.sh
  run_fast_friends_diff.sh
  run_investment_same_survey.sh
  run_investment_diff_survey.sh
  run_investment_diff_friends.sh
  run_pistacchio_same_survey.sh
  run_pistacchio_different_survey.sh
paper/
  Social_Coordination_Draft.pdf
```

## Requirements

The scripts use Python and AutoGen-style agents, plus a local Ollama server.

```bash
pip install -r requirements.txt
```

The code also expects a local `ideology.json` file. A template is provided at `data/ideology.json.example`.

## Running the experiments

Run the scripts from the repository root, for example:

```bash
bash scripts/run_fast_friends_same.sh
bash scripts/run_fast_friends_diff.sh
bash scripts/run_investment_same_survey.sh
bash scripts/run_investment_diff_survey.sh
bash scripts/run_investment_diff_friends.sh
```

Each script iterates over the ideology grid and model list used in the study. Output CSVs are written into experiment-specific folders, while logs go into `logs/` or `logs_different/` depending on the script.

## Output folders

The scripts generate run logs and CSVs under folders such as:

- `fast_friends_same/`
- `fast_friends_diff/`
- `same_survey/`
- `different_survey/`
- `invest_same_survey/`
- `invest_diff_survey/`
- `invest_diff_survey_friends/`

These are ignored by Git in the included `.gitignore`.

## Notes

- `pistacchio_*` files are preserved as legacy variants.
- `investment_diff_suvery.sh` was an original typo-named duplicate and is not needed in the cleaned workflow.
- The paper’s methodology uses ANES-style feeling thermometers, personality and trust items, and repeated runs for robustness.
