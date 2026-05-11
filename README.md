# Social Coordination LLM Experiments

This repository packages the code set for the chapter **Affective Polarization in Large Language Models**.

The experiments are grouped as follows:

- **Pistacchio**: shared social identity as an intervention to test whether commonalities improve restaurant-choice coordination.
- **Fast Friends**: the same coordination setting, but using the **36 Questions for Increasing Closeness** protocol as the shared-commonality intervention.
- **Investment games**: trust-focused interactions, where shared-identity discussion is used to test whether trust changes, rather than coordination.

## Repository layout

```text
experiments/
  coordination/
    pistacchio/
      pistacchio_same_survey.py
      pistacchio_different_survey.py
    fast_friends/
      fast_friends_same.py
      fast_friends_diff.py
  trust/
    investment/
      investment_same_survey.py
      investment_diff_survey.py
      investment_diff_friends.py
scripts/
  run_fast_friends_same.sh
  run_fast_friends_diff.sh
  run_investment_same_survey.sh
  run_investment_diff_survey.sh
  run_pistacchio_same_survey.sh
  run_pistacchio_different_survey.sh
  legacy/
    investment_diff_suvery.sh
paper/
  Social_Coordination_Draft.pdf
```

## Requirements

The scripts use Python and AutoGen-style agents, plus a local Ollama server.

```bash
pip install -r requirements.txt
```

The code expects an `ideology.json` file in the repository root. A template is included at `data/ideology.json.example`.

## Notes

- The repository keeps the original filenames from the code set, but the folder structure now reflects the actual experimental role of each script.
- `investment_diff_suvery.sh` is preserved only as a legacy typo-named script.
