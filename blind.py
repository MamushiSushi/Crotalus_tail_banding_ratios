"""
Blind tail crops for measurement.

Expected input layout (crop each photo to the tail only first):
    crops/
      measurement/Crotalus_atrox/*.jpg
      measurement/Crotalus_scutulatus/*.jpg
      test/Crotalus_atrox/*.jpg
      test/Crotalus_scutulatus/*.jpg

Usage:
    python blind.py round1                      # all crops -> blind/round1/  (codes A001...)
    python blind.py round2                      # all crops again, NEW codes  (codes B001...)
    python blind.py round2 --fraction 0.5       # or a random half

Outputs:
    blind/roundN/<code>.jpg          images to measure (no species, set, or obs ID in the name)
    blind/roundN_measurements.csv    sheet to fill in, rows already in random order
    keys/key_roundN.csv              code -> species/set/original file  (DON'T OPEN until done)

Measure in the order the sheet lists. In Fiji: straight-line tool, press M for each band
(light1, dark1, light2, dark2, light3, dark3 from the rattle forward), copy the lengths into
the sheet. Units don't matter (pixels are fine) because only the ratio is used.
"""
import argparse
import csv
import os
import random
import shutil

EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
COLS = ["code", "L1", "D1", "L2", "D2", "L3", "D3", "excluded", "exclusion_reason", "notes"]


def collect(root):
    items = []
    for set_name in sorted(os.listdir(root)):
        set_dir = os.path.join(root, set_name)
        if not os.path.isdir(set_dir):
            continue
        for species in sorted(os.listdir(set_dir)):
            sp_dir = os.path.join(set_dir, species)
            if not os.path.isdir(sp_dir):
                continue
            for f in sorted(os.listdir(sp_dir)):
                if f.lower().endswith(EXTS):
                    items.append({"set": set_name, "species": species.replace("_", " "),
                                  "original_file": os.path.join(sp_dir, f)})
    return items


def blind(round_name, root, fraction, seed):
    items = collect(root)
    if not items:
        raise SystemExit(f"No images found under {root}/<set>/<species>/")
    rng = random.Random(seed)
    if fraction < 1:
        items = rng.sample(items, k=max(1, round(len(items) * fraction)))
    rng.shuffle(items)

    prefix = {"round1": "A", "round2": "B"}.get(round_name, "C")
    outdir = os.path.join("blind", round_name)
    if os.path.exists(outdir):
        raise SystemExit(f"{outdir} already exists - delete it first if you really want to redo this round")
    os.makedirs(outdir)
    os.makedirs("keys", exist_ok=True)

    key_rows = []
    for i, it in enumerate(items, 1):
        code = f"{prefix}{i:03d}"
        ext = os.path.splitext(it["original_file"])[1].lower()
        shutil.copy2(it["original_file"], os.path.join(outdir, code + ext))
        key_rows.append({"code": code, **it})

    # Measurement sheet in a SECOND independent random order, so sheet order != code order
    sheet_codes = [r["code"] for r in key_rows]
    rng.shuffle(sheet_codes)
    with open(os.path.join("blind", f"{round_name}_measurements.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for c in sheet_codes:
            w.writerow({"code": c})

    with open(os.path.join("keys", f"key_{round_name}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["code", "set", "species", "original_file"])
        w.writeheader()
        w.writerows(key_rows)

    print(f"{round_name}: {len(key_rows)} images -> {outdir}/")
    print(f"Fill in blind/{round_name}_measurements.csv in the listed order.")
    print(f"Key saved to keys/key_{round_name}.csv - don't open it until measuring is finished.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("round", choices=["round1", "round2", "round3"])
    ap.add_argument("--crops", default="crops")
    ap.add_argument("--fraction", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=None, help="leave unset for an unpredictable order")
    a = ap.parse_args()
    blind(a.round, a.crops, a.fraction, a.seed)
