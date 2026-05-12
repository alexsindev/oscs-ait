"""
Titanic Dataset - Exploratory Data Analysis
============================================
Dataset Source: Kaggle / Seaborn built-in
Run: python titanic_eda.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io, sys

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150})

# ── 1. Load Dataset ───────────────────────────────────────────────────────────
# Option A: from seaborn (requires internet on first run)
df = sns.load_dataset("titanic")

# Option B: from a local CSV (uncomment if you have the file)
# df = pd.read_csv("titanic.csv")

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
print(null_df[null_df["null_count"] > 0])

# ── 4. Descriptive Statistics ─────────────────────────────────────────────────
print("\n── Descriptive Stats (Numerical) ──")
print(df.describe().to_string())

print("\n── Descriptive Stats (Categorical) ──")
print(df.describe(include="object").to_string())

# ── 5. Survival Breakdown ─────────────────────────────────────────────────────
print("\n── Overall Survival Rate ──")
print(df["survived"].value_counts())
print(f"Survival Rate: {df['survived'].mean():.4f}  ({df['survived'].mean()*100:.2f}%)")

print("\n── Survival by Sex ──")
print(df.groupby("sex")["survived"].mean())

print("\n── Survival by Pclass ──")
print(df.groupby("pclass")["survived"].mean())

print("\n── Survival by Embarked ──")
print(df.groupby("embarked")["survived"].mean())

# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Chart 1: Survival Count ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
counts = df["survived"].value_counts().sort_index()
bars = ax.bar(
    ["Did Not Survive (0)", "Survived (1)"],
    counts.values,
    color=["#d9534f", "#5cb85c"],
    edgecolor="white", linewidth=1.5, width=0.5
)
for bar, val in zip(bars, counts.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 5,
        str(val), ha="center", va="bottom", fontweight="bold", fontsize=12
    )
ax.set_title("Survival Count", fontsize=14, fontweight="bold")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig("chart1_survival_count.png")
plt.show()

# ── Chart 2: Age Distribution ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
df["age"].dropna().hist(bins=35, color="steelblue", edgecolor="white", linewidth=0.8, ax=ax)
ax.axvline(df["age"].median(), color="red",    linestyle="--", linewidth=1.8,
           label=f"Median: {df['age'].median():.1f}")
ax.axvline(df["age"].mean(),   color="orange", linestyle="--", linewidth=1.8,
           label=f"Mean:   {df['age'].mean():.1f}")
ax.set_title("Age Distribution of Passengers", fontsize=14, fontweight="bold")
ax.set_xlabel("Age")
ax.set_ylabel("Count")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart2_age_distribution.png")
plt.show()

# ── Chart 3: Survival Rate by Sex ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
sex_surv = df.groupby("sex")["survived"].mean()
bars = ax.bar(
    sex_surv.index, sex_surv.values,
    color=["#5bc0de", "#f0ad4e"],
    edgecolor="white", linewidth=1.5, width=0.45
)
for bar, val in zip(bars, sex_surv.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.015,
        f"{val:.1%}", ha="center", va="bottom", fontweight="bold", fontsize=12
    )
ax.set_title("Survival Rate by Sex", fontsize=14, fontweight="bold")
ax.set_ylabel("Survival Rate")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig("chart3_survival_by_sex.png")
plt.show()

# ── Chart 4: Survival Rate by Passenger Class ────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
pc_surv = df.groupby("pclass")["survived"].mean()
bars = ax.bar(
    pc_surv.index.astype(str), pc_surv.values,
    color=["#337ab7", "#5cb85c", "#d9534f"],
    edgecolor="white", linewidth=1.5, width=0.45
)
for bar, val in zip(bars, pc_surv.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.015,
        f"{val:.1%}", ha="center", va="bottom", fontweight="bold", fontsize=12
    )
ax.set_title("Survival Rate by Passenger Class", fontsize=14, fontweight="bold")
ax.set_xlabel("Passenger Class")
ax.set_ylabel("Survival Rate")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig("chart4_survival_by_pclass.png")
plt.show()

# ── Chart 5: Fare Distribution by Class (Boxplot) ────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="pclass", y="fare", palette="Set2", ax=ax)
ax.set_title("Fare Distribution by Passenger Class", fontsize=14, fontweight="bold")
ax.set_xlabel("Passenger Class")
ax.set_ylabel("Fare (£)")
plt.tight_layout()
plt.savefig("chart5_fare_boxplot.png")
plt.show()

# ── Chart 6: Age vs Fare Scatter (coloured by Survival) ───────────────────────
fig, ax = plt.subplots(figsize=(9, 6))
for surv, label, color in [(0, "Did Not Survive", "#d9534f"), (1, "Survived", "#5cb85c")]:
    grp = df[df["survived"] == surv].dropna(subset=["age", "fare"])
    ax.scatter(grp["age"], grp["fare"], alpha=0.45, s=22, c=color, label=label)
ax.set_title("Age vs. Fare (Coloured by Survival)", fontsize=14, fontweight="bold")
ax.set_xlabel("Age")
ax.set_ylabel("Fare (£)")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("chart6_age_fare_scatter.png")
plt.show()

# ── Chart 7: Correlation Heatmap ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
num_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", linewidths=0.5, ax=ax,
    vmin=-1, vmax=1, annot_kws={"size": 11}
)
ax.set_title("Correlation Matrix — Numerical Features", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("chart7_correlation_heatmap.png")
plt.show()

# ── Chart 8: Survival Rate by Port of Embarkation ────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
emb_surv = df.groupby("embarked")["survived"].mean().dropna()
colors_emb = sns.color_palette("Set2", len(emb_surv))
bars = ax.bar(
    emb_surv.index, emb_surv.values,
    color=colors_emb, edgecolor="white", linewidth=1.5, width=0.4
)
for bar, val in zip(bars, emb_surv.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.015,
        f"{val:.1%}", ha="center", va="bottom", fontweight="bold", fontsize=12
    )
ax.set_title("Survival Rate by Port of Embarkation", fontsize=14, fontweight="bold")
ax.set_xlabel("Port  (C = Cherbourg,  Q = Queenstown,  S = Southampton)")
ax.set_ylabel("Survival Rate")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig("chart8_survival_by_embarked.png")
plt.show()

print("\n✅ Done — 8 charts saved to the working directory.")
