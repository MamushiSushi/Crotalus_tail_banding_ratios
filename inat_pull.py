"""
Pull CC-licensed, research-grade iNaturalist photos of Crotalus atrox and C. scutulatus.

Step 1 builds a metadata table with ONE ROW PER PHOTO (not per observation),
because tail close-ups are often the 2nd-4th photo of an observation.
Step 2 downloads photos from the iNaturalist open-data bucket (licensed photos only).

Run in Colab or on Bridges-2:
    pip install pyinaturalist pandas requests
    python inat_pull.py metadata                 # -> inat_photos.csv (all localities)
    python inat_pull.py metadata --place-id 1234 # one iNat place only (ID from an Explore URL)
    python inat_pull.py metadata --bbox 29 -105 32 -103   # or a custom box: SW lat/lng, NE lat/lng
    python inat_pull.py download --n 1500        # random sample per species -> photos/<species>/
"""
import argparse
import os
import time

import pandas as pd
import requests
from pyinaturalist import get_observations  # handles paging + iNat rate limits

SPECIES = ["Crotalus atrox", "Crotalus scutulatus"]
LICENSES = ["CC0", "CC-BY", "CC-BY-NC", "CC-BY-SA", "CC-BY-NC-SA", "CC-BY-ND", "CC-BY-NC-ND"]
META = "inat_photos.csv"


def pull_metadata(place_id=None, bbox=None):
    region = {}
    if place_id:
        region["place_id"] = place_id
    if bbox:
        region.update(dict(zip(["swlat", "swlng", "nelat", "nelng"], bbox)))
    print("Region filter:", region or "none (all localities)")
    rows = []
    for sp in SPECIES:
        print(f"Querying {sp} ...")
        resp = get_observations(
            taxon_name=sp,
            quality_grade="research",
            photo_license=LICENSES,
            photos=True,
            page="all",
            **region,
        )
        obs_list = resp["results"]
        print(f"  {len(obs_list)} observations")
        for o in obs_list:
            # pyinaturalist returns location as [lat, lng]; the raw API returns "lat,lng"
            loc = o.get("location")
            if isinstance(loc, str) and loc:
                lat, lon = (float(x) for x in loc.split(","))
            elif isinstance(loc, (list, tuple)) and len(loc) == 2:
                lat, lon = float(loc[0]), float(loc[1])
            else:
                lat, lon = None, None
            for i, p in enumerate(o.get("photos", [])):
                if not p.get("license_code"):
                    continue  # unlicensed photo inside a licensed observation: skip
                rows.append(
                    {
                        "species": sp,
                        "obs_id": o["id"],
                        "photo_id": p["id"],
                        "photo_index": i,  # 0 = first photo of the observation
                        "n_photos_in_obs": len(o.get("photos", [])),
                        "license": p["license_code"],
                        "attribution": p.get("attribution"),
                        "url_large": p["url"].replace("square", "large"),
                        "lat": lat,
                        "lon": lon,
                        "coords_obscured": o.get("obscured"),
                        "positional_accuracy_m": o.get("positional_accuracy"),
                        "observed_on": o.get("observed_on"),
                        "observer": (o.get("user") or {}).get("login"),
                        "obs_url": f"https://www.inaturalist.org/observations/{o['id']}",
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv(META, index=False)
    print(df.groupby("species").agg(photos=("photo_id", "size"), observations=("obs_id", "nunique")))
    print(f"Saved {META}")


def download(n_per_species, seed=42):
    df = pd.read_csv(META)
    for sp, grp in df.groupby("species"):
        # sample observations (not photos) so one snake can't dominate, then keep all its photos
        obs = grp["obs_id"].drop_duplicates().sample(
            n=min(n_per_species, grp["obs_id"].nunique()), random_state=seed
        )
        sub = grp[grp["obs_id"].isin(obs)]
        outdir = os.path.join("photos", sp.replace(" ", "_"))
        os.makedirs(outdir, exist_ok=True)
        print(f"{sp}: downloading {len(sub)} photos from {len(obs)} observations")
        for _, r in sub.iterrows():
            ext = os.path.splitext(r["url_large"].split("?")[0])[1] or ".jpg"  # drop ?timestamp
            path = os.path.join(outdir, f"{r['obs_id']}_{r['photo_id']}{ext}")
            if os.path.exists(path):
                continue
            try:
                resp = requests.get(r["url_large"], timeout=30)
                resp.raise_for_status()
                with open(path, "wb") as f:
                    f.write(resp.content)
            except Exception as e:  # keep going; log failures
                print("  failed:", r["url_large"], e)
            time.sleep(0.2)  # be polite even though the open-data bucket has no download cap


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["metadata", "download"])
    ap.add_argument("--n", type=int, default=1500, help="observations to sample per species")
    ap.add_argument("--place-id", type=int, default=None,
                    help="iNaturalist place ID (from the place_id= number in an Explore URL)")
    ap.add_argument("--bbox", type=float, nargs=4, default=None,
                    metavar=("SWLAT", "SWLNG", "NELAT", "NELNG"),
                    help="custom bounding box instead of a named place")
    a = ap.parse_args()
    if a.step == "metadata":
        pull_metadata(a.place_id, a.bbox)
    else:
        download(a.n)
