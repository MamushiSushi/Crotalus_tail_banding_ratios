"""
Final analysis: Round 1 + Round 2 (blinded repeat) tail-band light:dark ratios,
Crotalus atrox vs C. scutulatus.

Inputs: round1.csv, key_round1.csv, Round_1_Photo_Exclusions.md,
        round2.csv, key_round2.csv, Round_2_Photo_Exclusions.txt
Rules: light bands measured first, then dark (3+3 or 2+2); ratio = mean light / mean dark.
Round 1 corrections (documented): A038 kept, A039 excluded; A022 = 3 light + 2 dark;
A044 = 2+2 (extra 5th row dropped); A015, A017 measured alternating light/dark.

Outputs: final_individuals.csv, final_summary.txt,
         fig1_ratio_by_species.png, fig2_roc.png, fig3_bland_altman.png, fig4_round1_vs_round2.png
"""
import re
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

POS, NEG = "Crotalus scutulatus", "Crotalus atrox"
rng = np.random.default_rng(42)
out = []
def p(s=""): out.append(str(s)); print(s)

# ---------------- per-round ratios ----------------
SPECIAL = {"A022": ([0, 1, 2], [3, 4]), "A044": ([0, 1], [2, 3]),
           "A015": ([0, 2], [1, 3]), "A017": ([0, 2], [1, 3])}

def ratios(res_file, key_file, exc_file, prefix, fix_exc=None):
    res = pd.read_csv(res_file, sep=None, engine="python")
    res.columns = [c.strip() for c in res.columns]
    res["code"] = res["Label"].str.extract(rf"({prefix}\d{{3}})")
    exc = set(re.findall(rf"{prefix}\d{{3}}", open(exc_file, encoding="utf-8").read()))
    if fix_exc: exc = fix_exc(exc)
    rows = []
    for code, g in res.groupby("code"):
        L = g["Length"].to_numpy(); n = len(L)
        if code in SPECIAL: li, di = SPECIAL[code]
        elif n in (4, 6): li, di = list(range(n // 2)), list(range(n // 2, n))
        else: continue
        rows.append({"code": code, "light": L[li].mean(), "dark": L[di].mean(),
                     "ratio": L[li].mean() / L[di].mean(), "nb": len(di)})
    d = pd.DataFrame(rows)
    key = pd.read_csv(key_file)
    d = key.merge(d, on="code", how="left")
    d["excluded"] = d["code"].isin(exc)
    d.loc[d.excluded, ["light", "dark", "ratio"]] = np.nan
    return d

r1 = ratios("round1.csv", "key_round1.csv", "Round_1_Photo_Exclusions.md", "A",
            lambda e: (e - {"A038"}) | {"A039"})
r2 = ratios("round2.csv", "key_round2.csv", "Round_2_Photo_Exclusions.txt", "B")
m = r1.merge(r2, on=["original_file", "set", "species"], suffixes=("_1", "_2"))
assert len(m) == 200
m["y"] = (m["species"] == POS).astype(int)

# ---------------- exclusion agreement ----------------
p("FINAL SUMMARY: Round 1 + Round 2")
e1, e2 = m.excluded_1, m.excluded_2
tab = pd.crosstab(e1.rename("Excluded R1"), e2.rename("Excluded R2"))
p("Exclusion agreement (200 individuals):"); p(tab.to_string())
po = (e1 == e2).mean()
pe = e1.mean() * e2.mean() + (1 - e1.mean()) * (1 - e2.mean())
p(f"Observed agreement {po:.1%}; Cohen's kappa = {(po - pe) / (1 - pe):.2f}")
both = m[~e1 & ~e2].copy()
p(f"Measured in both rounds: {len(both)}; excluded in at least one round: {200 - len(both)}")
p(pd.crosstab(both.set, both.species).to_string()); p()

# ---------------- repeatability ----------------
def icc_a1(x1, x2):
    """ICC(2,1): two-way random effects, absolute agreement, single measurement."""
    Y = np.c_[x1, x2]; n, k = Y.shape
    gm = Y.mean()
    msr = k * ((Y.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((Y.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)

def boot_icc(x1, x2, B=2000):
    idx = [rng.integers(0, len(x1), len(x1)) for _ in range(B)]
    v = [icc_a1(x1[i], x2[i]) for i in idx]
    return np.percentile(v, [2.5, 97.5])

p("Repeatability (individuals measured in both rounds)")
for lab, a, b in [("ratio", both.ratio_1.values, both.ratio_2.values),
                  ("ln(ratio)", np.log(both.ratio_1.values), np.log(both.ratio_2.values)),
                  ("mean light width (px)", both.light_1.values, both.light_2.values),
                  ("mean dark width (px)", both.dark_1.values, both.dark_2.values)]:
    ci = boot_icc(a, b)
    p(f"  ICC(2,1) {lab:22s} = {icc_a1(a, b):.3f}  (95% CI {ci[0]:.3f}-{ci[1]:.3f})")
diff = both.ratio_2 - both.ratio_1
mean_r = (both.ratio_1 + both.ratio_2) / 2
bias, sd = diff.mean(), diff.std(ddof=1)
t = stats.ttest_rel(both.ratio_2, both.ratio_1)
p(f"  Bland-Altman (ratio): bias R2-R1 = {bias:+.3f} (paired t p={t.pvalue:.2f}); "
  f"95% limits of agreement {bias - 1.96 * sd:+.3f} to {bias + 1.96 * sd:+.3f}")
p(f"  Median absolute difference between rounds = {diff.abs().median():.3f}; "
  f"as % of the individual's mean ratio = {(diff.abs() / mean_r).median():.1%}")
p(f"  Spearman r (R1 vs R2) = {stats.spearmanr(both.ratio_1, both.ratio_2)[0]:.3f}")

# ---------------- classification ----------------
def fit_threshold(train):
    X = np.log(train[["r"]].to_numpy()); y = train.y.to_numpy()
    lr = LogisticRegression(C=1e6).fit(X, y)
    b0, b1 = lr.intercept_[0], lr.coef_[0, 0]
    fpr, tpr, thr = roc_curve(y, lr.predict_proba(X)[:, 1])
    pc = thr[np.argmax(tpr - fpr)]
    return float(np.exp((np.log(pc / (1 - pc)) - b0) / b1)), b0, b1

def metrics(y, r, cut):
    pred = (r >= cut).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    se, sp = tp / (tp + fn), tn / (tn + fp)
    return dict(bacc=(se + sp) / 2, sens=se, spec=sp, auc=roc_auc_score(y, r), cm=(tn, fp, fn, tp))

def boot(sub, cut, B=2000):
    y, r = sub.y.to_numpy(), sub.r.to_numpy()
    i0, i1 = np.where(y == 0)[0], np.where(y == 1)[0]
    v = {k: [] for k in ("bacc", "sens", "spec", "auc")}
    for _ in range(B):
        idx = np.r_[rng.choice(i0, len(i0)), rng.choice(i1, len(i1))]
        mm = metrics(y[idx], r[idx], cut)
        for k in v: v[k].append(mm[k])
    return {k: np.percentile(x, [2.5, 97.5]) for k, x in v.items()}

def evaluate(label, data):
    tr, te = data[data.set == "measurement"], data[data.set == "test"]
    cut, b0, b1 = fit_threshold(tr)
    p(f"\n{label}: measurement n={len(tr)}, test n={len(te)}; fitted threshold ratio >= {cut:.2f} -> scutulatus")
    res = {}
    for nm, sub in [("Measurement (in-sample)", tr), ("TEST (independent)", te)]:
        mm, ci = metrics(sub.y.to_numpy(), sub.r.to_numpy(), cut), boot(sub, cut)
        tn, fp, fn, tp = mm["cm"]
        p(f"  {nm}: balanced acc {mm['bacc']:.3f} ({ci['bacc'][0]:.3f}-{ci['bacc'][1]:.3f}), "
          f"AUC {mm['auc']:.3f} ({ci['auc'][0]:.3f}-{ci['auc'][1]:.3f}), "
          f"sens {mm['sens']:.2f}, spec {mm['spec']:.2f}  "
          f"[atrox ok {tn}, atrox->scut {fp}, scut->atrox {fn}, scut ok {tp}]")
        res[nm] = (mm, ci)
    return cut, res

# Primary: mean of the two rounds, individuals measured in both rounds
both["r"] = (both.ratio_1 + both.ratio_2) / 2
cut_main, res_main = evaluate("PRIMARY - mean of both rounds", both)
r1o = m[~e1].assign(r=lambda d: d.ratio_1)
r2o = m[~e2].assign(r=lambda d: d.ratio_2)
cut_r1, _ = evaluate("Round 1 only (all R1-measured)", r1o)
cut_r2, _ = evaluate("Round 2 only (all R2-measured)", r2o)

# Class changes between rounds (same threshold applied to both rounds)
for lab, c in [("primary threshold", cut_main), ("Round 1 threshold", cut_r1)]:
    flip = ((both.ratio_1 >= c) != (both.ratio_2 >= c)).mean()
    p(f"\nIndividuals whose predicted species changes between rounds ({lab} {c:.2f}): {flip:.1%}")

# Descriptives and species difference on primary values
p("\nLight:dark ratio (mean of both rounds) by set and species")
p(both.groupby(["set", "species"])["r"].describe()[["count", "mean", "std", "min", "50%", "max"]].round(2).to_string())
for nm, sub in [("measurement", both[both.set == "measurement"]), ("test", both[both.set == "test"]), ("all", both)]:
    a, b = sub.loc[sub.y == 0, "r"], sub.loc[sub.y == 1, "r"]
    u = stats.mannwhitneyu(b, a, alternative="two-sided")
    p(f"Mann-Whitney ({nm}): scutulatus median {b.median():.2f} vs atrox {a.median():.2f}, U={u.statistic:.0f}, p={u.pvalue:.2g}")
p(f"scutulatus with ratio >= 2.0: {(both.loc[both.y == 1, 'r'] >= 2).mean():.0%}; "
  f"atrox within 0.8-1.25: {both.loc[both.y == 0, 'r'].between(0.8, 1.25).mean():.0%}")
big = both[(both.dark_1 + both.dark_2) / 2 >= 8]
te_big = big[big.set == "test"]
p(f"Robustness: tails with mean dark band >= 8 px (n={len(big)}): test AUC = "
  f"{roc_auc_score(te_big.y, te_big.r):.3f} (test n={len(te_big)})")

cols = ["original_file", "set", "species", "code_1", "code_2", "excluded_1", "excluded_2",
        "ratio_1", "ratio_2", "light_1", "dark_1", "light_2", "dark_2"]
m[cols].to_csv("final_individuals.csv", index=False)
open("final_summary.txt", "w").write("\n".join(out))

# ---------------- figures ----------------
col = {NEG: "#4C72B0", POS: "#DD8452"}
fig, ax = plt.subplots(figsize=(7.5, 4.8))
for k, (sp, lab) in enumerate([(NEG, "C. atrox"), (POS, "C. scutulatus")]):
    for s, mk in [("measurement", "o"), ("test", "^")]:
        v = both[(both.species == sp) & (both.set == s)]["r"]
        ax.scatter(v, k + rng.uniform(-0.18, 0.18, len(v)), s=28, marker=mk, alpha=0.75, color=col[sp],
                   edgecolor="white" if mk == "o" else "black", linewidth=0.6, label=f"{lab}, {s} set (n={len(v)})")
    med = both[both.species == sp]["r"].median()
    ax.plot([med] * 2, [k - 0.3, k + 0.3], color="black", lw=2)
ax.axvline(cut_main, color="crimson", lw=1.6, ls="--", label=f"Fitted threshold = {cut_main:.2f}")
for xv, tt in [(1, "1:1"), (2, "2:1")]:
    ax.axvline(xv, color="grey", lw=0.8, ls=":"); ax.text(xv, 1.5, tt, ha="center", color="grey", fontsize=9)
ax.set_xscale("log"); ax.set_xticks([0.75, 1, 1.5, 2, 3, 4]); ax.set_xticklabels(["0.75", "1", "1.5", "2", "3", "4"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_yticks([0, 1]); ax.set_yticklabels(["C. atrox", "C. scutulatus"], style="italic"); ax.set_ylim(-0.5, 1.6)
ax.set_xlabel("Light:dark tail-band width ratio, mean of two blinded rounds (log scale)")
ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False)
ax.spines[["top", "right"]].set_visible(False); plt.tight_layout(); plt.savefig("fig1_ratio_by_species.png", dpi=200)

fig, ax = plt.subplots(figsize=(4.2, 4))
for nm, sub, c in [("Measurement", both[both.set == "measurement"], "grey"), ("Test", both[both.set == "test"], "crimson")]:
    f, tp_, _ = roc_curve(sub.y, sub.r)
    ax.plot(f, tp_, color=c, lw=2, label=f"{nm} (AUC={roc_auc_score(sub.y, sub.r):.2f})")
ax.plot([0, 1], [0, 1], ":", color="black", lw=0.8)
ax.set_xlabel("False-positive rate (atrox called scutulatus)"); ax.set_ylabel("True-positive rate")
ax.legend(frameon=False, fontsize=9); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("fig2_roc.png", dpi=200)

fig, ax = plt.subplots(figsize=(5.5, 4))
ax.scatter(mean_r, diff, s=20, alpha=0.7, color="#555555", edgecolor="white", linewidth=0.5)
for yv, ls in [(bias, "-"), (bias - 1.96 * sd, "--"), (bias + 1.96 * sd, "--")]:
    ax.axhline(yv, color="crimson", ls=ls, lw=1.3)
ax.axhline(0, color="black", lw=0.6, ls=":")
ax.text(ax.get_xlim()[1], bias + 1.96 * sd, f" +1.96 SD ({bias + 1.96 * sd:+.2f})", va="bottom", ha="right", fontsize=8, color="crimson")
ax.text(ax.get_xlim()[1], bias - 1.96 * sd, f" -1.96 SD ({bias - 1.96 * sd:+.2f})", va="top", ha="right", fontsize=8, color="crimson")
ax.set_xlabel("Mean ratio of the two rounds"); ax.set_ylabel("Round 2 − Round 1 ratio")
ax.spines[["top", "right"]].set_visible(False); plt.tight_layout(); plt.savefig("fig3_bland_altman.png", dpi=200)

fig, ax = plt.subplots(figsize=(4.5, 4.5))
for sp, lab in [(NEG, "C. atrox"), (POS, "C. scutulatus")]:
    s = both[both.species == sp]
    ax.scatter(s.ratio_1, s.ratio_2, s=20, alpha=0.75, color=col[sp], edgecolor="white", linewidth=0.5, label=lab)
lim = [0.5, max(both.ratio_1.max(), both.ratio_2.max()) * 1.05]
ax.plot(lim, lim, color="black", lw=0.8, ls=":")
ax.axvline(cut_main, color="crimson", lw=0.8, ls="--"); ax.axhline(cut_main, color="crimson", lw=0.8, ls="--")
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_xlabel("Round 1 ratio"); ax.set_ylabel("Round 2 ratio")
ax.legend(frameon=False, fontsize=9, prop={"style": "italic"}); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("fig4_round1_vs_round2.png", dpi=200)
