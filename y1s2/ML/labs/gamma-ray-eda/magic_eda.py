"""
MAGIC Gamma Telescope Dataset - Exploratory Data Analysis
==========================================================
Dataset Source: UCI Machine Learning Repository
Download: https://archive.ics.uci.edu/ml/datasets/MAGIC+Gamma+Telescope
File expected: magic04.data (no header row)
Run: python magic_eda.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150})

# ── 1. Load Dataset ───────────────────────────────────────────────────────────
COLUMNS = [
    "fLength", "fWidth", "fSize", "fConc", "fConc1",
    "fAsym", "fM3Long", "fM3Trans", "fAlpha", "fDist", "class"
]

df = pd.read_csv("magic04.data", header=None, names=COLUMNS)

# Encode target: g (gamma/signal) = 1, h (hadron/background) = 0
df["label"] = (df["class"] == "g").astype(int)

# ── 2. Basic Info ─────────────────────────────────────────────────────────────
print("=" * 60)
print("SHAPE:", df.shape)
print("=" * 60)

print("\n── df.info() ──")
df.info()

print("\n── df.head() ──")
print(df.head().to_string())

# ── 3. Null / Missing Values ──────────────────────────────────────────────────
print("\n── Null Counts ──")
null_counts = df.isnull().sum()
null_pct    = (df.isnull().sum() / len(df) * 100).round(2)
null_df     = pd.DataFrame({"null_count": null_counts, "null_%": null_pct})
print(null_df)

# ── 4. Descriptive Statistics ─────────────────────────────────────────────────
print("\n── Descriptive Stats (Numerical Features) ──")
print(df.drop(columns=["class", "label"]).describe().to_string())

# ── 5. Class Breakdown ────────────────────────────────────────────────────────
print("\n── Class Distribution ──")
print(df["class"].value_counts())
print(f"Signal (gamma) rate: {df['label'].mean():.4f}  ({df['label'].mean()*100:.2f}%)")

print("\n── Mean feature values by class ──")
print(df.groupby("class")[["fAlpha", "fConc", "fWidth", "fLength"]].mean())


# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_COLS = ["fLength", "fWidth", "fSize", "fConc", "fConc1",
                "fAsym", "fM3Long", "fM3Trans", "fAlpha", "fDist"]

# ── Chart 1: Class Count ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
counts = df["class"].value_counts().sort_index()
labels = ["Hadron / Background (h)", "Gamma / Signal (g)"]
colors = ["#d9534f", "#5cb85c"]
bars = ax.bar(labels, counts.values, color=colors,
              edgecolor="white", linewidth=1.5, width=0.5)
for bar, val in zip(bars, counts.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 30,
        str(val), ha="center", va="bottom", fontweight="bold", fontsize=12
    )
ax.set_title("Class Distribution (Signal vs. Background)", fontsize=14, fontweight="bold")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig("chart1_class_count.png")
plt.show()

# ── Chart 2: fAlpha Distribution by Class ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
for cls, label, color in [("g", "Gamma (Signal)", "#5cb85c"),
                           ("h", "Hadron (Background)", "#d9534f")]:
    df[df["class"] == cls]["fAlpha"].plot.hist(
        bins=40, alpha=0.65, color=color, edgecolor="white",
        linewidth=0.6, label=label, ax=ax
    )
ax.set_title("fAlpha Distribution by Class", fontsize=14, fontweight="bold")
ax.set_xlabel("fAlpha (degrees)")
ax.set_ylabel("Count")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart2_falpha_distribution.png")
plt.show()

# ── Chart 3: fWidth Distribution by Class ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
for cls, label, color in [("g", "Gamma (Signal)", "#5cb85c"),
                           ("h", "Hadron (Background)", "#d9534f")]:
    df[df["class"] == cls]["fWidth"].plot.hist(
        bins=40, alpha=0.65, color=color, edgecolor="white",
        linewidth=0.6, label=label, ax=ax
    )
ax.set_title("fWidth Distribution by Class", fontsize=14, fontweight="bold")
ax.set_xlabel("fWidth (mm)")
ax.set_ylabel("Count")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart3_fwidth_distribution.png")
plt.show()

# ── Chart 4: Mean Feature Value by Class (Bar Chart) ─────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
features_to_compare = ["fLength", "fWidth", "fConc", "fConc1", "fAlpha", "fDist"]
mean_by_class = df.groupby("class")[features_to_compare].mean()
x = np.arange(len(features_to_compare))
width = 0.35
bars1 = ax.bar(x - width/2, mean_by_class.loc["g"], width,
               label="Gamma (Signal)", color="#5cb85c", edgecolor="white", linewidth=1.2)
bars2 = ax.bar(x + width/2, mean_by_class.loc["h"], width,
               label="Hadron (Background)", color="#d9534f", edgecolor="white", linewidth=1.2)
ax.set_title("Mean Feature Values by Class", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(features_to_compare)
ax.set_ylabel("Mean Value")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart4_mean_features_by_class.png")
plt.show()

# ── Chart 5: fConc Boxplot by Class ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
sns.boxplot(data=df, x="class", y="fConc", palette={"g": "#5cb85c", "h": "#d9534f"}, ax=ax)
ax.set_title("fConc Distribution by Class", fontsize=14, fontweight="bold")
ax.set_xlabel("Class  (g = Gamma Signal,  h = Hadron Background)")
ax.set_ylabel("fConc (concentration ratio)")
plt.tight_layout()
plt.savefig("chart5_fconc_boxplot.png")
plt.show()

# ── Chart 6: fAlpha vs fConc Scatter (coloured by class) ──────────────────────
fig, ax = plt.subplots(figsize=(9, 6))
for cls, label, color in [("h", "Hadron (Background)", "#d9534f"),
                           ("g", "Gamma (Signal)", "#5cb85c")]:
    grp = df[df["class"] == cls]
    ax.scatter(grp["fAlpha"], grp["fConc"], alpha=0.3, s=10, c=color, label=label)
ax.set_title("fAlpha vs. fConc (Coloured by Class)", fontsize=14, fontweight="bold")
ax.set_xlabel("fAlpha (degrees)")
ax.set_ylabel("fConc (concentration ratio)")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart6_falpha_fconc_scatter.png")
plt.show()

# ── Chart 7: Correlation Heatmap ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
num_cols = FEATURE_COLS + ["label"]
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", linewidths=0.5, ax=ax,
    vmin=-1, vmax=1, annot_kws={"size": 9}
)
ax.set_title("Correlation Matrix -- Numerical Features", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("chart7_correlation_heatmap.png")
plt.show()

# ── Chart 8: fSize Distribution by Class ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
for cls, label, color in [("g", "Gamma (Signal)", "#5cb85c"),
                           ("h", "Hadron (Background)", "#d9534f")]:
    df[df["class"] == cls]["fSize"].plot.hist(
        bins=40, alpha=0.65, color=color, edgecolor="white",
        linewidth=0.6, label=label, ax=ax
    )
ax.axvline(df[df["class"]=="g"]["fSize"].median(), color="#2d7a2d",
           linestyle="--", linewidth=1.5, label=f"Signal Median: {df[df['class']=='g']['fSize'].median():.2f}")
ax.axvline(df[df["class"]=="h"]["fSize"].median(), color="#a31515",
           linestyle="--", linewidth=1.5, label=f"Background Median: {df[df['class']=='h']['fSize'].median():.2f}")
ax.set_title("fSize Distribution by Class", fontsize=14, fontweight="bold")
ax.set_xlabel("fSize (log scale)")
ax.set_ylabel("Count")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("chart8_fsize_distribution.png")
plt.show()

print("\nDone -- 8 charts saved to the working directory.")