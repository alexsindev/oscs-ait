import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from src.models import SolveParams
from src import greedy, simulated_annealing
from src.generator import generate_dataset, generate_bangkok_real, generate_hard_dataset, save_dataset, load_dataset
from src.experiments import (
    run_algorithm_comparison, run_scalability, run_param_sweep, run_convergence
)

CHART_DIR = "assets/charts"
DATA_DIR = "assets/dataset"
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
PALETTE = sns.color_palette("tab10")

DEFAULT_PARAMS = SolveParams(num_days=2, daily_time_budget=720, total_budget=500.0,
                              start_time=540, hotel_lat=13.7563, hotel_lng=100.5018)
DATASET_ORDER = ["small", "medium", "bangkok_real", "large", "hard"]
DATASET_N = {"small": 15, "medium": 75, "bangkok_real": 150, "large": 300, "hard": 100}


# ── Data generation ────────────────────────────────────────────────────────────

def generate_all_datasets():
    print("Generating datasets...")
    configs = [
        ("small", 15, generate_dataset),
        ("medium", 75, generate_dataset),
        ("large", 300, generate_dataset),
    ]
    for name, n, fn in configs:
        path = f"{DATA_DIR}/{name}.json"
        attrs = fn(n, seed=42, name=name)
        save_dataset(attrs, path)
        print(f"  {name}: {len(attrs)} attractions → {path}")

    path = f"{DATA_DIR}/bangkok_real.json"
    attrs = generate_bangkok_real(150, seed=42)
    save_dataset(attrs, path)
    print(f"  bangkok_real: {len(attrs)} attractions → {path}")

    path = f"{DATA_DIR}/hard.json"
    attrs = generate_hard_dataset(100, seed=42)
    save_dataset(attrs, path)
    print(f"  hard (tight windows): {len(attrs)} attractions → {path}")


def load_all_datasets():
    return {name: load_dataset(f"{DATA_DIR}/{name}.json") for name in DATASET_ORDER}


HARD_PARAMS = SolveParams(num_days=2, daily_time_budget=480, total_budget=300.0,
                           start_time=480, hotel_lat=13.7563, hotel_lng=100.5018)


# ── Chart helpers ──────────────────────────────────────────────────────────────

def savefig(name):
    path = f"{CHART_DIR}/{name}"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {path}")


# ── Exp 1: Algorithm Comparison ────────────────────────────────────────────────

def exp1_comparison(datasets):
    print("\nExp 1: Algorithm comparison...")
    base_datasets = {k: v for k, v in datasets.items() if k != "hard"}
    results = run_algorithm_comparison(base_datasets, DEFAULT_PARAMS, greedy.solve, simulated_annealing.solve)

    rows = []
    for name in DATASET_ORDER:
        params_used = HARD_PARAMS if name == "hard" else DEFAULT_PARAMS
        if name == "hard":
            r_hard = run_algorithm_comparison({"hard": datasets["hard"]}, HARD_PARAMS,
                                               greedy.solve, simulated_annealing.solve)
            r = r_hard["hard"]
        else:
            r = results[name]
        rows.append({
            "Dataset": name,
            "n": DATASET_N[name],
            "Greedy": r["greedy"].satisfaction,
            "SA Mean": r["sa"].mean,
            "SA Std": r["sa"].std,
            "Improvement %": r["improvement_pct"],
            "Greedy ms": r["greedy"].computation_ms,
            "SA ms": r["sa"].mean_ms,
        })

    df = pd.DataFrame(rows)
    df.to_csv(f"{CHART_DIR}/comparison_table.csv", index=False)
    print(df.to_string(index=False))

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(DATASET_ORDER))
    w = 0.35
    bars_g = ax.bar(x - w / 2, df["Greedy"], w, label="Greedy", color=PALETTE[0])
    bars_s = ax.bar(x + w / 2, df["SA Mean"], w, label="SA (mean)", color=PALETTE[1],
                    yerr=df["SA Std"], capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n(n={DATASET_N[n]})" for n in DATASET_ORDER])
    ax.set_ylabel("Total Satisfaction Score")
    ax.set_title("Greedy vs. Simulated Annealing — Satisfaction")
    ax.legend()
    savefig("satisfaction_comparison.png")

    imp_vals = df["Improvement %"].round(2).tolist()
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [PALETTE[2] if v >= 0 else PALETTE[3] for v in imp_vals]
    ax.bar(DATASET_ORDER, imp_vals, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("SA Improvement over Greedy (%)")
    ax.set_title("SA Improvement % by Dataset")
    ymax = max(abs(v) for v in imp_vals) if imp_vals else 1
    ax.set_ylim(-ymax * 1.5 - 0.5, ymax * 1.5 + 0.5)
    for i, v in enumerate(imp_vals):
        offset = ymax * 0.1 + 0.1
        ax.text(i, v + (offset if v >= 0 else -offset), f"{v:.1f}%", ha="center", fontsize=9)
    savefig("improvement_pct.png")

    return results


# ── Exp 2: Scalability ─────────────────────────────────────────────────────────

def exp2_scalability(datasets):
    print("\nExp 2: Scalability...")
    scale_names = [n for n in DATASET_ORDER if n != "hard"]
    scale_datasets = {k: datasets[k] for k in scale_names}
    rows = run_scalability(scale_datasets, DEFAULT_PARAMS, greedy.solve, simulated_annealing.solve)

    ns = [DATASET_N[name] for name in scale_names]
    g_ms = [rows[name]["greedy_ms"] for name in scale_names]
    s_ms = [rows[name]["sa_mean_ms"] for name in scale_names]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(ns, g_ms, "o-", color=PALETTE[0], label="Greedy", linewidth=2)
    ax.loglog(ns, s_ms, "s-", color=PALETTE[1], label="SA (mean)", linewidth=2)
    for n, g in zip(ns, g_ms):
        ax.annotate(f"n={n}", (n, g), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_xlabel("Number of Attractions (n)")
    ax.set_ylabel("Runtime (ms)")
    ax.set_title("Scalability: Runtime vs Dataset Size (log-log)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    savefig("runtime_scaling.png")


# ── Exp 3–5: Parameter Sensitivity ────────────────────────────────────────────

def exp_sensitivity(datasets):
    medium = datasets["medium"]
    print("\nExp 3: Sensitivity — num_days...")

    def _plot_sensitivity(sweep, param_label, x_vals, x_label, filename, x_fmt=None):
        g_vals = [sweep[v]["greedy"].satisfaction for v in x_vals]
        s_means = [sweep[v]["sa"].mean for v in x_vals]
        s_stds = [sweep[v]["sa"].std for v in x_vals]
        x_labels = [x_fmt(v) if x_fmt else str(v) for v in x_vals]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x_labels, g_vals, "o-", color=PALETTE[0], label="Greedy", linewidth=2)
        ax.errorbar(x_labels, s_means, yerr=s_stds, fmt="s-",
                    color=PALETTE[1], label="SA (mean ± std)", linewidth=2, capsize=4)
        ax.set_xlabel(x_label)
        ax.set_ylabel("Total Satisfaction Score")
        ax.set_title(f"Sensitivity: Satisfaction vs {x_label}")
        ax.legend()
        savefig(filename)

    days_vals = [1, 2, 3, 5]
    sweep_days = run_param_sweep(medium, "num_days", days_vals, DEFAULT_PARAMS,
                                  greedy.solve, simulated_annealing.solve)
    _plot_sensitivity(sweep_days, "num_days", days_vals, "Number of Days", "sensitivity_days.png")

    print("  Sensitivity — daily_time_budget...")
    budget_vals = [360, 600, 720]
    sweep_daily = run_param_sweep(medium, "daily_time_budget", budget_vals, DEFAULT_PARAMS,
                                   greedy.solve, simulated_annealing.solve)
    _plot_sensitivity(sweep_daily, "daily_time_budget", budget_vals,
                      "Daily Time Budget (min)", "sensitivity_daily_budget.png",
                      x_fmt=lambda v: f"{v//60}h")

    print("  Sensitivity — total_budget...")
    money_vals = [100, 200, 500, 1000]
    sweep_money = run_param_sweep(medium, "total_budget", money_vals, DEFAULT_PARAMS,
                                   greedy.solve, simulated_annealing.solve)
    _plot_sensitivity(sweep_money, "total_budget", money_vals,
                      "Total Budget (USD)", "sensitivity_total_budget.png",
                      x_fmt=lambda v: f"${v}")


# ── Exp 6: SA Convergence ──────────────────────────────────────────────────────

def exp6_convergence(datasets):
    print("\nExp 6: SA convergence...")
    medium = datasets["medium"]
    curves = run_convergence(medium, DEFAULT_PARAMS, simulated_annealing.solve, n_seeds=5)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    for i, c in enumerate(curves):
        pts = c["convergence"]
        if not pts:
            continue
        iters = [p.iteration for p in pts]
        sats = [p.satisfaction for p in pts]
        ax1.plot(iters, sats, alpha=0.85, linewidth=1.5,
                 color=PALETTE[i], label=f"seed={c['seed']}")
        if i == 0:
            temps = [p.temperature for p in pts]
            ax2.plot(iters, temps, "k--", linewidth=1, alpha=0.4, label="Temperature")

    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Best Satisfaction")
    ax2.set_ylabel("Temperature", color="grey")
    ax2.tick_params(axis="y", labelcolor="grey")
    ax1.set_title("SA Convergence — Medium Dataset (5 seeds)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=8)
    savefig("convergence.png")


# ── Exp 7: SA Seed Distribution ───────────────────────────────────────────────

def exp7_distribution(datasets):
    print("\nExp 7: SA satisfaction distribution across seeds...")
    from src.experiments import run_multiple

    data = []
    for name in DATASET_ORDER:
        stats = run_multiple(datasets[name], DEFAULT_PARAMS, simulated_annealing.solve)
        for v in (stats.raw or []):
            data.append({"Dataset": f"{name}\n(n={DATASET_N[name]})", "Satisfaction": v})

    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=df, x="Dataset", y="Satisfaction", hue="Dataset",
                ax=ax, palette="tab10", width=0.5, legend=False)
    ax.set_title("SA Satisfaction Distribution (10 seeds per dataset)")
    ax.set_xlabel("")
    savefig("sa_distribution.png")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    generate_all_datasets()
    datasets = load_all_datasets()

    exp1_comparison(datasets)
    exp2_scalability(datasets)
    exp_sensitivity(datasets)
    exp6_convergence(datasets)
    exp7_distribution(datasets)

    print("\nAll experiments complete.")
    print(f"Charts → {CHART_DIR}/")
    print(f"Datasets → {DATA_DIR}/")
