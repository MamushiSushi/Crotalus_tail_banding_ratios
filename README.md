# Crotalus Tail-Band Ratios

**Can tail-band width distinguish Western Diamondback (*Crotalus atrox*) and Mojave (*C. scutulatus*) rattlesnakes? A blinded, repeatable morphometric test of a field character.**

## Project Information

- **Course:** BIOL 3340 / 5340 – Bioinformatics
- **Instructor:** Dr. Jeffery Demuth
- **Author:** R. Reed McClure (individual project)
- **Semester:** Fall 2026
- **Status:** Round 1 measurements and analysis complete; Round 2 (repeatability) in progress.

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
| Analyzed after Round 1 exclusions | 90 | 91 |

- One photo per individual (observation); no individual appears in more than one set.
- Test-set species were confirmed from non-tail characters (postocular stripe, crown scalation, dorsal speckling; Cardwell et al., 2022).
- **Photos are not redistributed in this repository.** `inat_photos.csv` links every record to its iNaturalist observation and photo URL with license and attribution.

## Repository Contents

| File | Description |
|---|---|
| `README.md` | This file: project overview, contents and reproduction instructions. |
| `ai_usage.md` | Documentation of AI assistance and how outputs were verified. |
| `environment.yml` | Python package versions. |
| `tailband_colab.ipynb` | Google Colab notebook that runs data retrieval, duplicate checking and blinding. |
| `inat_pull.py` | Queries iNaturalist for both species (one row per photo) and downloads a reproducible random sample of photos. |
| `blind.py` | Copies selected photos into one folder under random codes in shuffled order and writes the code-to-species key separately. |
| `analyze_round1.py` | Computes per-individual light:dark ratios, logistic-regression threshold, test-set evaluation with bootstrapped CIs, and figures. |
| `data/inat_photos.csv` | Metadata for all licensed photos returned by the regional query. |
| `data/round1.csv` | Fiji Results table, Round 1 (band lengths in pixels, labeled by blinded code). |
| `data/Round_1_Photo_Exclusions.md` | Codes excluded during Round 1 and the reason for each. |
| `data/key_round1.csv` | Code-to-species/set key. *Added after Round 2 measurements are complete.* |
| `results/round1_ratios.csv` | One row per individual: mean light and dark widths, ratio, set, species. |
| `results/round1_summary.txt` | Full Round 1 statistics. |
| `results/fig1_ratio_by_species.png` | Ratio by species and set, with fitted threshold and the published 1:1 and 2:1 expectations. |
| `results/fig2_roc.png` | ROC curves for the measurement and test sets. |

## Workflow

1. **Retrieve data** (`inat_pull.py`): query research-grade, CC-licensed observations of both species in the Trans-Pecos; download photos from a random sample of observations (fixed seed).
2. **Screen and sort:** keep photos with a clear tail showing at least two complete light and two complete dark bands; one photo per individual; assign 25 head-verified individuals per species to the test set and 75 per species to the measurement set. Photos are not cropped or edited.
3. **Check duplicates:** confirm no observation appears twice within or across sets.
4. **Blind** (`blind.py`): rename all 200 photos to random codes (A001–A200) in shuffled order; store the key separately and do not open it until measuring is finished.
5. **Measure** in Fiji/ImageJ, in code order: with the straight-line tool, measure the three complete light bands nearest the rattle, then the three complete dark bands (two and two if fewer are visible), along the visible center line of the tail (dorsal or lateral view), perpendicular to the band boundaries.
6. **Analyze** (`analyze_round1.py`): ratio = mean light width / mean dark width; logistic regression of species on ln(ratio) fit to the measurement set; Youden-optimal threshold applied unchanged to the test set; balanced accuracy, sensitivity, specificity and ROC-AUC with 2,000 stratified bootstrap resamples.
7. **Repeat:** re-blind with new codes (B001–B200) at least three days after Round 1 and re-measure to estimate repeatability (ICC, Bland–Altman, proportion changing predicted species).

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

**Re-run the Round 1 analysis from the included measurements:**

```bash
git clone https://github.com/MamushiSushi/Crotalus_tail_banding_ratios.git
cd Crotalus_tail_banding_ratios
pip install pandas numpy scipy scikit-learn matplotlib
python analyze_round1.py data/round1.csv data/key_round1.csv data/Round_1_Photo_Exclusions.md
```

Outputs (`round1_ratios.csv`, `round1_summary.txt`, `fig1_ratio_by_species.png`, `fig2_roc.png`) are written to the current folder.

**Rebuild the dataset from scratch:** open `tailband_colab.ipynb` in Google Colab and run the cells in order (connect Google Drive, install, set `PLACE_ID = 79259`, pull metadata, download photos). The random seed (42) reproduces the same observation sample; iNaturalist content can change over time, so counts may differ slightly from those reported here.

## Preliminary Results (Round 1)

181 of 200 individuals were measurable (19 excluded for curled, obscured, canted, overexposed or aberrant tails).

| Metric | Value |
|---|---|
| Median ratio, *C. atrox* (all) | 1.19 |
| Median ratio, *C. scutulatus* (all) | 1.32 |
| *C. scutulatus* with ratio ≥ 2.0 | 11% |
| Fitted threshold (measurement set) | ratio ≥ 1.38 → *C. scutulatus* |
| Measurement-set ROC-AUC | 0.54 (95% CI 0.44–0.64) |
| **Test-set balanced accuracy** | **0.63 (95% CI 0.50–0.75)** |
| **Test-set ROC-AUC** | **0.68 (95% CI 0.53–0.83)** |
| Test-set sensitivity / specificity | 0.46 / 0.79 |
| Test-set AUC, tails with dark bands ≥ 8 px | 0.77 |

The ratio distributions of the two species overlap extensively, and few *C. scutulatus* approach the described 2:1 ratio. On independently identified individuals the ratio classifies better than chance but far below a reliable field standard, consistent with Cardwell et al. (2022). Performance improves on higher-resolution tails, indicating that part of the overlap reflects measurement noise.

## Limitations

- Measurement-set labels come from iNaturalist identifications that may themselves have used tail banding.
- Blinding is partial: the whole snake is visible in uncropped photos, and the same person selected and measured them.
- View angle (dorsal vs. lateral), tail curvature and lighting vary among photos.
- The test set is small (24 per species after exclusions), so confidence intervals are wide.
- Results apply to the Trans-Pecos and may not hold elsewhere in the range.

## Project Progress

**Completed**
- [x] Proposal and revision following instructor feedback
- [x] iNaturalist query and photo download (Trans-Pecos)
- [x] Screening, set assembly and duplicate check
- [x] Round 1 blinding and measurement (181 measured, 19 excluded)
- [x] Round 1 analysis and figures
- [x] Draft report

**Remaining**
- [ ] Round 2 blinded re-measurement
- [ ] Repeatability analysis (ICC, Bland–Altman, % changing class)
- [ ] Optional: zero-shot multimodal LLM on the test set
- [ ] Finalize repository documentation
- [ ] Final report and presentation

## AI Use and Reproducibility

Claude (Anthropic) was used to refine the project design, write and debug the retrieval, blinding, duplicate-check and analysis scripts, troubleshoot Colab and Fiji, and draft documentation. Scripts were tested on dummy data before use, and outputs were checked against the data (species counts, folder counts, zero duplicates, row counts per image, light/dark brightness checks). All measurements were made by the author. Details are in `ai_usage.md`.

Only Creative Commons-licensed photos are used, with attribution retained. Localities are reported only at the regional level, and observer usernames are not published in figures or tables.

## References

- Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. *The Lancet, 327*(8476), 307–310.
- Cardwell, M. D., Massey, D. J., Smelski, G., & Wüster, W. (2022). Mohave rattlesnake (*Crotalus scutulatus*) identification revisited. *Wilderness & Environmental Medicine, 33*(2), 210–218. https://doi.org/10.1016/j.wem.2022.01.003
- Ernst, C. H., & Ernst, E. M. (2003). *Snakes of the United States and Canada.* Smithsonian Books.
- iNaturalist. (2026). Research-grade observations of *Crotalus atrox* and *C. scutulatus*, Trans-Pecos ecoregion (place_id 79259). Retrieved November 14, 2026, from https://www.inaturalist.org
- Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine, 15*(2), 155–163.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
- Schindelin, J., et al. (2012). Fiji: An open-source platform for biological-image analysis. *Nature Methods, 9*(7), 676–682.
