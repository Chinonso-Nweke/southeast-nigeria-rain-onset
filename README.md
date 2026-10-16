# When do the rains start in south-east Nigeria?

An open analysis of 44 years of daily rainfall for five places in south-east Nigeria (Enugu, Nsukka, Abakaliki, Onitsha and Owerri). It estimates when the rains usually start, how often an early wet spell is followed by a dry spell (a "false start"), and how risky it has been to plant on a given date.

**Live page:** https://kendrick-chinonso.github.io/southeast-nigeria-rain-onset/

**Author:** Kendrick Chinonso. This is a first agricultural technology data project, and a work in progress.

![How the analysis works](method.svg)

## The question

A farmer who plants after the first rains can lose seedlings if a dry spell follows. A farmer who waits too long loses part of the season. This project defines "the rains have started" with a written rule, applies it to every year, and shows how much the answer depends on that rule.

## The rule

For each year, starting from 1 March, the rains have started on the first day when:

- at least **20 mm** of rain has fallen over **3 days in a row**, and
- there is **no dry spell of 7 days or more** (days under 1 mm) in the **next 30 days**.

A **false start** means an earlier wet spell met the first condition but was followed by a dry spell of 7 days or more.

The rule is adapted from Sivakumar (1988), who studied drier parts of West Africa and, in the version I know, started looking in May. I apply it to a wetter zone and start on 1 March, so the numbers are a working choice, not an official standard for south-east Nigeria. I confirmed that the paper exists and that a slide deck from the African Centre of Meteorological Application for Development (ACMAD) attributes this rule to it. I have not read the paper's full text.

## What it found so far

These numbers come from the 1981 to 2024 run. The live page updates itself each year, so these may differ slightly from what you see there.

| Place | Median start | False starts | Later-half shift* |
|---|---|---|---|
| Owerri | 1 April | 27% | +19 days |
| Onitsha | 9 April | 32% | +21 days |
| Abakaliki | 9 April | 16% | +30 days |
| Enugu | 17 April | 18% | +21 days |
| Nsukka | 24 April | 18% | +24 days |

*Average start date in the second half of the record minus the first half.

For Enugu, the answer changes with the rule:

| Rule | Median start | False starts | Later-half shift |
|---|---|---|---|
| 20 mm in 3 days, 7-day dry spell (working rule) | 17 April | 18% | +21 days |
| 15 mm in 3 days | 3 April | 27% | +17 days |
| 25 mm in 3 days | 22 April | 9% | +23 days |
| 5-day dry spell | 23 April | 36% | +24 days |
| 10-day dry spell | 4 April | 5% | +21 days |

- The median start moves by about three weeks depending on the rule, and the false start rate ranges from 5% to 36%. A false start percentage means nothing without its rule.
- At every place and under every rule tried for Enugu, the second half of the record starts later than the first half, by 17 to 30 days.
- For Enugu, the trend is +0.99 days per year over 1981 to 2024 (chance of a trend this large by luck: 0.001). Inside the two halves it is +1.49 days per year for 1981 to 2000 (0.128, only 20 years) and +1.65 days per year for 2001 to 2024 (0.019). I ran this check only for Enugu.

## Limits

- The rainfall values are **satellite and model estimates** (NASA POWER) for a grid cell of roughly 50 km. They are not rain gauge readings from a farm.
- All five places use the **same rainfall product**, so they are not five independent confirmations. A problem in the product itself could produce the same pattern everywhere.
- The later start is a pattern in this dataset. **It has not yet been checked against a second rainfall source** such as CHIRPS. That is the most important next step.
- The planting-date tool looks at rainfall only. It ignores soil, crop, seed and farm practice, so it is **not planting advice** for a particular farm.
- The Pidgin and Igbo versions of the page are drafts and have not been checked by a fluent speaker.
- Past patterns do not guarantee future seasons.

## Run it yourself

You need Python 3 with `pandas`, `numpy` and `requests`.

```
pip install pandas numpy requests
python test_onset.py     # checks that the rule behaves as described
python download_all.py   # downloads daily rainfall for the five places
python build_site.py     # computes everything and writes index.html
```

Open `index.html` in a browser. The `rain_*.csv` files are included, so you can skip the download step.

## Files

| File | What it does |
|---|---|
| `onset.py` | The rule: start of the rains and false starts for each year |
| `test_onset.py` | Seven checks on the rule (false start, no rain, rain before March, 6 vs 7 dry days) |
| `download_all.py` | Downloads daily rainfall from NASA POWER, with retries |
| `analyse_all.py` | Runs the rule at each place and summarises the results |
| `build_site.py`, `template.html` | Compute dry spell risk for planting dates and build the single-file page `index.html` |
| `.github/workflows/update.yml` | Re-runs everything every February with the latest year of data |

## Data and references

Daily precipitation (`PRECTOTCORR`) from the NASA Langley Research Center (LaRC) POWER Project, https://power.larc.nasa.gov/. Check the POWER site for its current wording on how to acknowledge the data.

Sivakumar, M. V. K. (1988). Predicting rainy season potential from the onset of rains in southern Sahelian and Sudanian climatic zones of West Africa. *Agricultural and Forest Meteorology, 42*(4), 295-305.

## Planned

- Check the results against a second rainfall source (CHIRPS).
- Crop-specific dry spell limits, once reliable sources are found.
- Checks of the Pidgin and Igbo text by fluent speakers.
