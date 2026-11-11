# QuickPizza API lab

ITDS362 Software Quality Assurance and Testing, API lab v2.0.
Target: https://quickpizza.grafana.com. Observed on 10 November 2026.

## Install and run

Python 3.10+, Git and curl are required. In Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe -m pytest -v --html=report.html --self-contained-html
Start-Process report.html
```

macOS/Linux: use `python3 -m venv .venv` and `.venv/bin/python` instead.
Run an independent case with `python -m pytest -v test_ratings.py::test_delete_rating`.
Do not run continuously against this shared service.

## Input domain model: POST /api/ratings

The API contract requires integer stars in [1,5], an existing pizza, and the
logged-in user's token. Each non-base case changes one characteristic only.

| Characteristic | Block | Representative | Test in test_create_rating.py |
|---|---|---|---|
| C1 value of stars | below 1 | 0 | test_stars_out_of_range[0] |
| C1 value of stars | 1 to 5 (base) | 3 | test_base_choice_is_saved |
| C1 value of stars | above 5 | 6 | test_stars_out_of_range[6] |
| C2 type of stars | whole number (base) | 3 | test_base_choice_is_saved |
| C2 type of stars | decimal | 3.5 | test_stars_type_is_refused[decimal] |
| C2 type of stars | text | "3" | test_stars_type_is_refused[text] |
| C2 type of stars | missing | field omitted | test_stars_type_is_refused[missing] |
| C3 pizza | exists (base) | fresh pizza_id fixture | test_base_choice_is_saved |
| C3 pizza | does not exist | 999999999 | test_nonexistent_pizza_is_refused |
| C4 token | user's own (base) | auth fixture | test_base_choice_is_saved |
| C4 token | none | no Authorization header | test_invalid_token_is_refused[none] |
| C4 token | wrong length | token short | test_invalid_token_is_refused[wrong-length] |

Base choice: 1+(3-1)+(4-1)+(2-1)+(3-1)=9 cases.
All combinations of the supplied model: 3*4*2*3=72 cases.
The supplied model is a practical abstraction: C1's numeric value applies when
stars is numeric, and the model does not enumerate every possible JSON type.

PUT boundaries use 0, 1, 5 and 6. Both accepted and refused updates are read back.
Ownership tests use a second fresh user and verify the owner's data is unchanged.

## Isolation and evidence

One session retains AWSALB cookies, keeping dependent calls on the same backend.
Every rating test creates a unique fictional user with a random ephemeral password; created ratings are removed
in fixture teardown. Public tokens are used only for reference data/pizza generation,
never to create or change ratings. The made-up 16-character token is used only
for the read-only Part B observation.

`probe_lab.py` executes the required curl probes and stores request JSON files
and sanitized observations under `evidence/`. Login credentials stay in memory
and are not written into evidence. It is a manual helper, not a pytest
test. `auth.txt` and `madeup.txt` contain only the two public/example tokens from
the assignment. No real credentials are required or committed.

See RESULTS.md for observations, the defect report and reflection answers;
report.html is the self-contained full-suite report. The intended suite contains
33 cases: 32 passing and one strict expected failure for Defect 1.

The optional no-session experiment was executed three times and removed from
the suite as directed because it is deliberately flaky.
