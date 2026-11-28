# Crotalus Tail-Band Ratios

**Can tail-band width distinguish Western Diamondback (*Crotalus atrox*) and Mojave (*C. scutulatus*) rattlesnakes? A blinded, repeatable morphometric test of a field character.**

## Project Information

- **Course:** BIOL 3340 / 5340 – Bioinformatics
- **Instructor:** Dr. Jeffery Demuth
- **Author:** R. Reed McClure (individual project)
- **Semester:** Fall 2026
- **Status:** Both blinded measurement rounds and the final analysis are complete; final report and presentation in preparation.

## Project Overview

Field guides commonly separate *C. scutulatus* from *C. atrox* by tail banding: light bands roughly twice as wide as the dark bands in *C. scutulatus*, and about equal in *C. atrox*. Cardwell et al. (2022) argue that this character is highly variable and overemphasized, but the ratio has not been measured across a large sample. This project measures light and dark band widths from iNaturalist photographs under blinded, repeated conditions and tests how well the light:dark ratio classifies individuals whose species was confirmed independently from head characters.

## Research Questions

1. How well does a light:dark tail-band width ratio threshold classify *C. atrox* and *C. scutulatus* within a region where both occur?
2. How repeatable is the measurement between blinded rounds?

## Dataset

Research-grade iNaturalist observations with Creative Commons-licensed photos, retrieved with the iNaturalist API (pyinaturalist) on November 14, 2026, restricted to the Trans-Pecos ecoregion (iNaturalist `place_id` 79259).

| | *C. atrox* | *C. scutulatus* |
|---|---|---|
| Research-grade observations (Trans-Pecos) | 2,372 | 607 |
| Licensed photos in those observations | 3,427 | 914 |
| Measurement set (iNaturalist identification) | 75 | 75 |
| Test set (species confirmed from head characters) | 25 | 25 |
| Measured in Round 1 | 90 | 91 |
| Measured in Round 2 | 86 | 86 |
| **Measured in both rounds (final analysis)** | **84** | **85** |

- One photo per individual (observation); no individual appears in more than one set.
- Test-set species were confirmed from non-tail characters (postocular stripe, crown scalation, dorsal speckling; Cardwell et al., 2022).
- **Photos are not redistributed in this repository.** `inat_photos.csv` links every record to its iNaturalist observation and photo URL with license and attribution.

## Repository Contents

| File | Description |
|---|---|
| `README.md` | This file: project overview, contents and reproduction instructions. |
| `ai_usage.md` | Documentation of AI assistance and how outputs were verified. |
| `environment.yml` | Python package versions. |
| `ColabNotebook/` | Google Colab notebook that runs data retrieval, duplicate checking and blinding. |
| `inat_pull.py` | Queries iNaturalist for both species (one row per photo) and downloads a reproducible random sample of photos. |
| `blind.py` | Copies selected photos into one folder under random codes in shuffled order and writes the code-to-species key separately. |
| `analyze_final.py` | Final analysis of both rounds: per-individual ratios, repeatability (ICC, Bland–Altman, class changes), logistic-regression threshold, test-set evaluation with bootstrapped CIs, and all figures. |
| `analyze_round1.py` | Preliminary Round 1-only analysis (superseded by `analyze_final.py`; kept for the record). |
| `data/inat_photos.csv` | Metadata for all licensed photos returned by the regional query. |
| `data/round1.csv`, `data/round2.csv` | Fiji Results tables for each round (band lengths in pixels, labeled by blinded code). |
| `data/key_round1.csv`, `data/key_round2.csv` | Code-to-species/set keys for each round. |
| `data/Round_1_Photo_Exclusions.md`, `data/Round_2_Photo_Exclusions.txt` | Codes excluded in each round and the reason for each. |
| `results/final_individuals.csv` | One row per individual: both rounds' codes, exclusion status, mean light and dark widths, and ratios. |
| `results/final_summary.txt` | Full statistics for the final analysis. |
| `results/fig1_ratio_by_species.png` | Ratio (mean of both rounds) by species and set, with fitted threshold and the published 1:1 and 2:1 expectations. |
| `results/fig2_roc.png` | ROC curves for the measurement and test sets. |
| `results/fig3_bland_altman.png` | Bland–Altman plot of agreement between rounds. |
| `results/fig4_round1_vs_round2.png` | Round 1 vs. Round 2 ratio for each individual, with the classification threshold. |

## Workflow

1. **Retrieve data** (`inat_pull.py`): query research-grade, CC-licensed observations of both species in the Trans-Pecos; download photos from a random sample of observations (fixed seed).
2. **Screen and sort:** keep photos with a clear tail showing at least two complete light and two complete dark bands; one photo per individual; assign 25 head-verified individuals per species to the test set and 75 per species to the measurement set. Photos are not cropped or edited.
3. **Check duplicates:** confirm no observation appears twice within or across sets.
4. **Blind** (`blind.py`): rename all 200 photos to random codes (A001–A200) in shuffled order; store the key separately and do not open it until measuring is finished.
5. **Measure** in Fiji/ImageJ, in code order: with the straight-line tool, measure the three complete light bands nearest the rattle, then the three complete dark bands (two and two if fewer are visible), along the visible center line of the tail (dorsal or lateral view), perpendicular to the band boundaries.
6. **Repeat:** at least three days after Round 1, re-blind all 200 photos with new codes (B001–B200) in a new random order and re-measure with the same protocol, making exclusion decisions afresh.
7. **Analyze** (`analyze_final.py`): ratio = mean light width / mean dark width. Repeatability: ICC(2,1) (two-way random effects, absolute agreement, single measurement) with bootstrapped CIs, Bland–Altman limits of agreement, and the proportion of individuals whose predicted species changes between rounds. Classification: each individual's mean ratio across rounds; logistic regression of species on ln(ratio) fit to the measurement set; Youden-optimal threshold applied unchanged to the test set; balanced accuracy, sensitivity, specificity and ROC-AUC with 2,000 stratified bootstrap resamples.

## Software and Dependencies

| Software or package | Version |
|---|---|
| Python | 3.13.18 |
| pyinaturalist | 0.21.1 |
| pandas | 3.0.5 |
| NumPy | 2.5.3 |
| SciPy | 1.18.1 |
| scikit-learn | 1.9.1 |
| matplotlib | 3.11.2 |
| requests | 2.32.4 |
| Fiji (ImageJ) | 1.54t |

## How to Reproduce the Analysis

**Re-run the final analysis from the included measurements:**

```bash
git clone https://github.com/MamushiSushi/Crotalus_tail_banding_ratios.git
cd Crotalus_tail_banding_ratios/data
pip install pandas numpy scipy scikit-learn matplotlib
python ../analyze_final.py
```

The script reads the six input files in `data/` and writes `final_summary.txt`, `final_individuals.csv` and the four figures to the same folder. Bootstrap CIs use a fixed seed (42).

**Rebuild the dataset from scratch:** open the notebook in `ColabNotebook/` in Google Colab and run the cells in order (connect Google Drive, install, set `PLACE_ID = 79259`, pull metadata, download photos). The random seed (42) reproduces the same observation sample; iNaturalist content can change over time, so counts may differ slightly from those reported here.

## Results

**Repeatability** (169 individuals measured in both rounds)

| Metric | Value |
|---|---|
| Exclusion agreement between rounds | 92.5% (Cohen's κ = 0.64) |
| ICC, individual band widths (light / dark) | 0.97 / 0.97 |
| **ICC, light:dark ratio** | **0.66 (95% CI 0.55–0.74)** |
| Bland–Altman bias (Round 2 − Round 1) | −0.09 (paired t-test p < 0.001) |
| 95% limits of agreement | −0.68 to +0.50 |
| Median between-round difference | 14% of the individual's ratio |
| Individuals changing predicted species between rounds | 25–30% |

**Classification** (mean ratio of both rounds)

| Metric | Value |
|---|---|
| Median ratio, *C. atrox* / *C. scutulatus* | 1.17 / 1.27 (Mann–Whitney p = 0.009) |
| *C. scutulatus* with ratio ≥ 2.0 | 7% |
| Fitted threshold (measurement set) | ratio ≥ 1.18 → *C. scutulatus* (Round 1 alone: 1.38) |
| Measurement-set ROC-AUC | 0.58 (95% CI 0.48–0.68) |
| **Test-set balanced accuracy** | **0.62 (95% CI 0.47–0.76)** |
| **Test-set ROC-AUC** | **0.71 (95% CI 0.55–0.85)** |
| Test-set sensitivity / specificity | 0.65 / 0.59 |
| Test-set AUC, tails with dark bands ≥ 8 px | 0.81 |

Individual band widths were measured very consistently, but the ratio was only moderately repeatable: bands are often only a few pixels wide, so small differences in edge placement change the ratio substantially, and the true difference between species is small. The two species differ slightly on average, but their distributions overlap extensively, few *C. scutulatus* approach the described 2:1 ratio, and the optimal threshold shifted between rounds. On independently identified individuals, the ratio classifies better than chance but far below the 90% balanced accuracy set as the criterion for a reliable field character. This supports Cardwell et al. (2022). Performance improves on higher-resolution tails, so part of the overlap reflects measurement noise rather than biology.

## Limitations

- Measurement-set labels come from iNaturalist identifications that may themselves have used tail banding.
- Blinding is partial: the whole snake is visible in uncropped photos, and the same person selected and measured them.
- Ratios were systematically slightly lower in Round 2, indicating drift in edge placement between sessions.
- View angle (dorsal vs. lateral), tail curvature and lighting vary among photos.
- The test set is small (22–23 per species measured in both rounds), so confidence intervals are wide.
- Results apply to the Trans-Pecos and may not hold elsewhere in the range.

## Project Progress

**Completed**
- [x] Proposal and revision following instructor feedback
- [x] iNaturalist query and photo download (Trans-Pecos)
- [x] Screening, set assembly and duplicate check
- [x] Round 1 blinding and measurement (181 measured, 19 excluded)
- [x] Round 2 blinded re-measurement (172 measured, 28 excluded)
- [x] Repeatability analysis (ICC, Bland–Altman, % changing class)
- [x] Final classification analysis and figures
- [x] Draft report

**Remaining**
- [ ] Time permitting: zero-shot multimodal LLM on the test set
- [ ] Final report and presentation

## AI Use and Reproducibility

Claude (Anthropic) was used to refine the project design, write and debug the retrieval, blinding, duplicate-check and analysis scripts, troubleshoot Colab and Fiji, and draft documentation. Scripts were tested on dummy data before use, and outputs were checked against the data (species counts, folder counts, zero duplicates, row counts per image, light/dark brightness checks, and consistency of the Round 2 key with Round 1). All measurements were made by the author. Details are in `ai_usage.md`.

Only Creative Commons-licensed photos are used, with attribution retained. Localities are reported only at the regional level, and observer usernames are not published in figures or tables.

## References

- Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. *The Lancet, 327*(8476), 307–310.
- Cardwell, M. D., Massey, D. J., Smelski, G., & Wüster, W. (2022). Mohave rattlesnake (*Crotalus scutulatus*) identification revisited. *Wilderness & Environmental Medicine, 33*(2), 210–218. https://doi.org/10.1016/j.wem.2022.01.003
- Ernst, C. H., & Ernst, E. M. (2003). *Snakes of the United States and Canada.* Smithsonian Books.
- iNaturalist. (2026). Research-grade observations of *Crotalus atrox* and *C. scutulatus*, Trans-Pecos ecoregion (place_id 79259). Retrieved November 14, 2026, from https://www.inaturalist.org
- Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine, 15*(2), 155–163.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
- Schindelin, J., et al. (2012). Fiji: An open-source platform for biological-image analysis. *Nature Methods, 9*(7), 676–682.
