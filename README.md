# When do the rains start in south-east Nigeria?

An open analysis of 45 years of daily rainfall for five places in south-east Nigeria (Enugu, Nsukka, Abakaliki, Onitsha and Owerri). It estimates when the rains usually start, how often an early wet spell is followed by a dry spell (a "false start"), and how risky it has been to plant on a given date.

**Live page:** https://github.com/Chinonso-Nweke/southeast-nigeria-rain-onset

**Author:** Chinonso Nweke. This is a first agricultural technology data project, and a work in progress.

![How the analysis works](method.svg)

## The question

A farmer who plants after the first rains can lose seedlings if a dry spell follows. A farmer who waits too long loses part of the season. This project defines "the rains have started" with a written rule, applies it to every year, and shows how much the answer depends on that rule.

## The rule

For each year, starting from 1 March, the rains have started on the first day when:

- at least **20 mm** of rain has fallen over **3 days in a row**, and
- there is **no dry spell longer than 7 days** (days under 1 mm) in the **next 30 days**.

A **false start** means an earlier wet spell met the first condition but was followed by a dry spell longer than 7 days.

The rule is adapted from Sivakumar (1988), who defined the onset of the rains as the date after 1 May when rainfall accumulated over 3 consecutive days is at least 20 mm and no dry spell within the next 30 days exceeds 7 days (I read the paper's text for this). Ati et al. (2002) compare this and other onset definitions for northern Nigeria. **What I changed (two things):** (1) I start looking on 1 March instead of 1 May, because the rains begin earlier in south-east Nigeria. (2) I count a day under 1 mm as dry, because the paper does not define a dry day. The 20 mm in 3 days, the 30-day window and the dry spell limit (longer than 7 days) are as in the paper. Sivakumar developed the rule for the Sahelian and Sudanian zones, so applying it to a wetter zone is my own choice and has not been validated for south-east Nigeria.

## What the page does

- **Check a planting date:** for any date from 1 March to 30 June and a dry spell length you choose, the share of years with such a dry spell in the next 30 days. It shows all years and the most recent 20 years side by side.
- **Rainfall source switch:** every chart and table can be viewed under NASA POWER or ERA5, so the disagreement between them is visible instead of hidden.
- **Do the sources agree?** An automatic audit rates the agreement at each place (weak, moderate or strong) and lists the reasons in plain words. The thresholds are my own rule of thumb and are written at the top of `audit.py`.
- **Best planting date:** an optimizer. You say how costly waiting a week is compared with losing a planting to a dry spell, and it picks the date with the lowest total loss, for all years and for the recent 20 years, under each rainfall source. It also gives a **robust date**: the date with the smallest worst-case regret across every source and period (minimax regret). A wide spread between the dates is itself a result. It is a simple model of rainfall risk and waiting cost, not a crop model.
- **Step-change test:** a Pettitt test (Pettitt, 1979) with a permutation check finds the single biggest jump in the start date and says whether it could be chance. This separates a sudden change, which can point to a change in the data source, from a gradual trend.
- **Data checks:** every rebuild checks for missing days, negative values and unusual years, and stops if the data is unreliable.
- Pidgin and Igbo versions of the main text, share buttons for WhatsApp and SMS, and a yearly automatic update.

## What it found so far

These numbers come from the 1981 to 2025 run with the rule above. The live page updates itself each year, so they may differ slightly from what you see there.

**NASA POWER**

| Place | Median start | False starts | Later-half shift* | Biggest jump in start date | Chance of a jump this big by luck | Yearly rain, first to second half |
|---|---|---|---|---|---|---|
| Owerri | 1 April | 24% | +18 days | 1997/1998 | 1.0% | 2275 to 1869 mm (-18%) |
| Onitsha | 7 April | 31% | +18 days | 1997/1998 | 0.7% | 2100 to 1700 mm (-19%) |
| Abakaliki | 11 April | 16% | +31 days | 2013/2014 | 0.2% | 1732 to 1349 mm (-22%) |
| Enugu | 13 April | 11% | +23 days | 1998/1999 | 0.8% | 1801 to 1427 mm (-21%) |
| Nsukka | 24 April | 16% | +29 days | 1998/1999 | 0.3% | 1618 to 1293 mm (-20%) |

*Average start date in the second half of the record minus the first half. Jump years are the first year of the later period, as the test reports them. Trends in the start date are +0.54 to +1.43 days per year (Enugu +1.12).

- At all five places NASA POWER shows a later start and a step in the start date that is unlikely to be luck within this dataset. Yearly rain in the same dataset falls by 18 to 22%.
- A false start percentage means nothing without its rule. These percentages are lower than in my earlier runs because the rule now follows the paper (a dry spell must exceed 7 days).

### Second-source check (ERA5)

I compared NASA POWER with ERA5, a weather reanalysis from the European Centre for Medium-Range Weather Forecasts (ECMWF), downloaded through the free Open-Meteo archive (`download_era5.py`, `compare_sources.py`). ERA5 is made with a different model, so agreement would be meaningful. It is still a model, not rain gauges, and its grid is about 25 km. Years compared: 1981 to 2025.

| Place | Later-half shift: NASA / ERA5 | Trend (days per year): NASA / ERA5 | Step in start date, p: ERA5 | Yearly rain change: NASA / ERA5 | Daily correlation | Yearly-total correlation |
|---|---|---|---|---|---|---|
| Enugu | +23 / +7 days | +1.12 / +0.42 | 0.089 | -21% / -6% | 0.37 | 0.08 |
| Nsukka | +29 / +3 days | +1.11 / +0.09 | 0.623 | -20% / -6% | 0.38 | 0.09 |
| Abakaliki | +31 / +7 days | +1.43 / +0.28 | 0.229 | -22% / -4% | 0.35 | 0.04 |
| Onitsha | +18 / +20 days | +0.54 / +0.76 | 0.016 | -19% / -3% | 0.32 | 0.00 |
| Owerri | +18 / +5 days | +0.55 / +0.13 | 0.716 | -18% / -3% | 0.35 | -0.09 |

- **Direction agrees, size mostly does not.** ERA5 also shows a later start at all five places, but only by 3 to 7 days at four of them, against 18 to 31 days in NASA POWER. Onitsha is the exception: ERA5 shows +20 days and a step that is unlikely to be luck (p = 0.016). A later start of 10 or more days is found at 5 of 5 places in NASA POWER and 1 of 5 in ERA5.
- **The fall in yearly rain appears only in NASA POWER.** ERA5 shows a fall of 3 to 6%, and none of the five places reaches a fall of 8%.
- **The two sources agree weakly.** Day-by-day correlation is 0.32 to 0.38, and five-day correlation 0.49 to 0.55. Correlation of yearly totals is close to zero (-0.09 to 0.09), so they do not agree on which years were wet or dry. The start dates they give for the same year differ by about 21 to 24 days on average (mean absolute difference). Average yearly rain also differs a lot at some places (Onitsha: 1896 mm in NASA, 1212 mm in ERA5).
- **What this means:** the later start is **not confirmed**. At least one of the two products does not track real year-to-year rainfall well here. This check cannot say which. As far as I know, reanalyses like ERA5 are weak for tropical rainfall, so a gauge-based source is the proper next test.

## What published studies say

I searched for published work on rainfall data quality in Nigeria. I read the abstracts or full pages of the studies below; I did not verify their figures independently.

- **NASA POWER against rain gauges.** Ellis and Samson (2026) compared NASA POWER with daily records from 20 Nigerian Meteorological Agency (NiMet) stations for 1982 to 2011. They report weak agreement from year to year, a very large overestimate of how often it rains (in the wet season, rain on 99% of days in POWER against 46% at the gauges), and trends that run opposite to the gauge trends. They conclude POWER is inadequate for hydroclimate monitoring in Nigeria. It does reproduce where the wetter and drier places are. This fits what my own check found, and it is a strong reason **not to report the NASA-based later start as a change in climate**.
- **Which products do better.** Datti et al. (2024) evaluated three satellite products against 42 NiMet gauges for 2002 to 2022 and recommend CHIRPS for research in Nigeria. ERA5 and NASA POWER were not among the products they tested.
- **Farmers and measured rainfall together.** Nnadi et al. (2019) surveyed 300 farm household heads in Anambra State and compared their answers with 31 years of rainfall data. Farmers reported later onset far more often in 2016 than in 1986, and the measured data pointed the same way, but the paper's own tests found the change in annual rainfall not statistically significant. My survey follows a similar idea, with a small sample and a different method.
- **What farmers in published surveys reported.** The only south-east survey I found that reports onset figures is Nnadi et al. (2019), above: in Anambra, 14.3% of 300 respondents reported a change in rainfall onset for 1986 and 87.7% for 2016, and 82.0% reported early cessation for 2016. Ozor et al. (2015) surveyed 108 farmers in Imo State; it reports no onset figures, and only 5% named changes in rainfall intensity and pattern as an impact. These are other researchers' surveys with different questions and samples. They are context for my own survey, not a substitute for it. Surveys I found for Oyo State (south-west) are outside these five places, so I did not use them. A study on climate perception and climate-smart rice farming in Ebonyi State (*Atmosphere*, 2021) appeared in my search, but I could not read it.
- **Long station records for Owerri.** One study (Ugwuegbulam et al., 2025) reports a weak upward trend in annual rainfall for Owerri over 1961 to 2020, about +2 mm per year. Its abstract does not say which station or provider the data came from, so I treat it as a caution, not as evidence either way. NASA POWER shows a fall of 18% at Owerri.

What this means for this project: the best next step is a comparison with gauge data. NiMet has a data request page (nimet.gov.ng/datarequest); its terms and cost are not described on the page I could read.

## Ground-truth survey (in progress)

The two rainfall sources disagree, and neither is a rain gauge measurement. To get independent evidence, I am running a short anonymous survey of farmers near the five places. It asks:

- whether the rains now start earlier or later than 20 to 30 years ago, and whether total rain has changed,
- which years from 2005 to 2025 they remember as late or early starts, or as years they lost seedlings to a dry spell,
- an open answer in their own words (English, Pidgin or Igbo).

The answers will be compared with the years each rainfall source calls late or early, and with its claim about yearly rain. Memory is imperfect, so this is supporting evidence, not proof. A separate optional form collects volunteers for daily rain reports from March 2027. Contact details are kept private and are not part of this repository. The script that creates both forms is in `survey/create_forms.gs`.

**Status:** collecting responses. No results yet.

## Limits

- The rainfall values are **satellite and model estimates** (NASA POWER) for a grid cell of roughly 50 km. They are not rain gauge readings from a farm.
- All five places use the **same rainfall product**, so they are not five independent confirmations. A problem in the product itself could produce the same pattern everywhere.
- The later start, and the fall in yearly rain that comes with it, are patterns in NASA POWER. A published comparison with 20 NiMet gauges (see "What published studies say") found NASA POWER weak on year-to-year agreement and its trends opposite to the gauges. **A first check against a second source (ERA5, below) did not reproduce them at the same size, so they are unconfirmed and should not be reported as a change in the climate.** A gauge-based source such as CHIRPS, or station records, is still needed.
- The planting-date tool looks at rainfall only. It ignores soil, crop, seed and farm practice, so it is **not planting advice** for a particular farm.
- The two rainfall sources agree weakly (see above), so treat the risk numbers and the best dates as indicative, not exact. The robust date shows the spread but does not say which source is right.
- The Pidgin and Igbo versions of the page are drafts and have not been checked by a fluent speaker.
- Past patterns do not guarantee future seasons.

## Run it yourself

You need Python 3 with `pandas`, `numpy` and `requests`.

```
pip install pandas numpy requests
python test_onset.py     # checks that the rule behaves as described
python test_new.py       # checks the step-change test, optimizer, robust date and auditor
python test_sources.py   # checks the ERA5 download and the comparison
python download_all.py   # downloads daily rainfall for the five places
python download_era5.py   # downloads ERA5 as the second source
python check_data.py     # quality checks on the downloaded files
python audit.py          # compares the two sources and writes audit_report.md
python build_site.py     # computes everything (about a minute) and writes index.html
```

Open `index.html` in a browser. The `rain_*.csv` and `era5_*.csv` files are included, so you can skip the download steps. The page works with NASA POWER alone if the ERA5 files are missing.

## Files

| File | What it does |
|---|---|
| `onset.py` | The rule: start of the rains and false starts for each year |
| `test_onset.py` | Eight checks on the rule (false start, no rain, rain before March, 7 vs 8 dry days, default settings) |
| `download_all.py` | Downloads daily rainfall from NASA POWER, with retries |
| `changepoint.py` | Pettitt step-change test with a permutation check |
| `optimize.py` | The planting-date optimizer (the page repeats it in JavaScript) |
| `check_data.py` | Data quality checks, for both sources |
| `audit.py` | The data auditor: rates how well the two sources agree and writes `audit_report.md` |
| `test_new.py` | Tests for the step-change test, optimizer, robust date, data checks and auditor |
| `download_era5.py`, `compare_sources.py`, `test_sources.py` | Second-source check against ERA5 |
| `net_test.py` | Shows which data servers your connection can reach |
| `analyse_all.py` | Runs the rule at each place and summarises the results |
| `build_site.py`, `template.html` | Compute dry spell risk for planting dates and build the single-file page `index.html` |
| `.github/workflows/update.yml` | Re-runs everything every February with the latest year of data |

## Data and references

Daily precipitation (`PRECTOTCORR`) from the NASA Langley Research Center (LaRC) POWER Project, https://power.larc.nasa.gov/. Check the POWER site for its current wording on how to acknowledge the data.

Ati, O. F., Stigter, C. J., & Oladipo, E. O. (2002). A comparison of methods to determine the onset of the growing season in northern Nigeria. *International Journal of Climatology, 22*(6), 731-742. https://doi.org/10.1002/joc.712

Datti, A. D., Zeng, G., Tarnavsky, E., Cornforth, R., Pappenberger, F., Abdullahi, B. A., & Onyejuruwa, A. (2024). Evaluation of satellite-based rainfall estimates against rain gauge observations across agro-climatic zones of Nigeria, West Africa. *Remote Sensing, 16*(10), 1755. https://doi.org/10.3390/rs16101755

Ellis, A. W., & Samson, B. (2026). Comparative assessment of POWER and CMAP satellite-derived rainfall products for hydroclimate monitoring in Nigeria. *Theoretical and Applied Climatology, 157*(4), 228. https://doi.org/10.1007/s00704-026-06121-1

Nnadi, O. I., Liwenga, E. T., Lyimo, J. G., & Madukwe, M. C. (2019). Impacts of variability and change in rainfall on gender of farmers in Anambra, Southeast Nigeria. *Heliyon, 5*(7), e02085. https://doi.org/10.1016/j.heliyon.2019.e02085

Ugwuegbulam, J. C., Osuagwu, J. C., & Nwoke, H. U. (2025). Rainfall variability and long-term trends in Owerri, southeastern Nigeria. *International Journal of Engineering Technology Research & Management, 9*(10), 346-351. https://doi.org/10.5281/zenodo.17435171

Ozor, N., Umunakwe, P. C., Ani, A. O., & Nnadi, F. N. (2015). Perceived impacts of climate change among rural farmers in Imo State, Nigeria. *African Journal of Agricultural Research, 10*(14), 1756-1764. https://doi.org/10.5897/AJAR2015.9618

Pettitt, A. N. (1979). A non-parametric approach to the change-point problem. *Journal of the Royal Statistical Society, Series C (Applied Statistics), 28*(2), 126-135.
Sivakumar, M. V. K. (1988). Predicting rainy season potential from the onset of rains in southern Sahelian and Sudanian climatic zones of West Africa. *Agricultural and Forest Meteorology, 42*(4), 295-305.



## Cite and reuse

The page has a suggested citation and buttons that download the results as CSV or JSON (one row per place, source and year). To rerun everything, follow the run instructions above. To add a DOI, archive the repository on Zenodo, then paste the DOI into `DOI = ""` near the top of `build_site.py` and rebuild.

Data credits: NASA POWER (NASA Langley Research Center, funded through the NASA Earth Science Division). [Weather data by Open-Meteo.com](https://open-meteo.com/), CC BY 4.0, serving ERA5 from the Copernicus Climate Change Service. The Open-Meteo free API is for non-commercial use.

Additional references: Hersbach et al. (2020), The ERA5 global reanalysis, QJRMS 146, 1999-2049, https://doi.org/10.1002/qj.3803. Zippenfenig (2023), Open-Meteo.com Weather API, https://doi.org/10.5281/ZENODO.7970649.

## Planned

- Check against a gauge-based source (CHIRPS, or station records). CHIRPS from NOAA's server could not be reached from my connection, and CHIRPS's own server needs large downloads.
- Collect ground truth from farmers (daily rain reports and recalled start dates), to calibrate which source to trust.
- Crop-specific dry spell limits, once reliable sources are found.
- Checks of the Pidgin and Igbo text by fluent speakers.
