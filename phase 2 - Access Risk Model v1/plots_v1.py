"""
AccessLens v2 - Report-Ready Visualizations
=============================================
Reads batch simulation results from outputs/batch_results_v1.csv
and generates 4 publication-grade, deterministic plots describing
baseline risk and counterfactual impact.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Force UTF-8 stdout
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_OUTPUTS_DIR = os.path.join(_SCRIPT_DIR, "..", "outputs")
CSV_PATH     = os.path.join(_OUTPUTS_DIR, "batch_results_v1.csv")
FIGURES_DIR  = os.path.join(_OUTPUTS_DIR, "figures")

# Ensure figures output directory exists
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_heatmap_baseline_risk(df: pd.DataFrame) -> str:
    """
    PLOT 1: Heatmap — Baseline Access Risk
    Rows: persona_id, Columns: scheme_id
    Values: baseline_score
    """
    # Pivot the data
    try:
        pivot_df = df.pivot(index="persona_id", columns="scheme_id", values="baseline_score")
    except ValueError:
        # If there are duplicates (e.g., ran a full cross-join and appended), take the mean
        pivot_df = df.groupby(["persona_id", "scheme_id"])["baseline_score"].mean().unstack()

    plt.figure(figsize=(10, 8))
    
    # We use a sequential colormap suitable for black & white printing (e.g., Grays or Blues)
    # cmap="Greys" works well for print-readiness.
    sns.heatmap(
        pivot_df, 
        cmap="Greys", 
        annot=True, 
        fmt=".2f", 
        cbar_kws={'label': 'Baseline Access Risk Score'}
    )
    
    plt.title("Baseline Access Risk: Persona vs. Scheme", pad=15)
    plt.xlabel("Scheme ID")
    plt.ylabel("Persona ID")
    plt.tight_layout()
    
    filepath = os.path.join(FIGURES_DIR, "heatmap_baseline_risk.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    
    return filepath


def plot_avg_risk_by_persona(df: pd.DataFrame) -> str:
    """
    PLOT 2: Bar Chart — Average Baseline Risk by Persona
    X-axis: persona_id, Y-axis: mean baseline_score
    """
    agg = df.groupby("persona_id")["baseline_score"].mean().reset_index()
    # Sort for cleaner presentation
    agg = agg.sort_values("baseline_score", ascending=False)
    
    plt.figure(figsize=(10, 6))
    
    # Use standard grey for print readability
    bars = plt.bar(agg["persona_id"], agg["baseline_score"], color="#555555")
    
    plt.title("Average Baseline Risk by Persona", pad=15)
    plt.xlabel("Persona ID")
    plt.ylabel("Mean Baseline Score")
    plt.ylim(0, 1.0)  # scale is always [0, 1]
    
    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    
    filepath = os.path.join(FIGURES_DIR, "avg_risk_by_persona.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    
    return filepath


def plot_avg_risk_by_scheme(df: pd.DataFrame) -> str:
    """
    PLOT 3: Bar Chart — Average Baseline Risk by Scheme
    X-axis: scheme_id, Y-axis: mean baseline_score
    """
    agg = df.groupby("scheme_id")["baseline_score"].mean().reset_index()
    agg = agg.sort_values("baseline_score", ascending=False)
    
    plt.figure(figsize=(10, 6))
    
    bars = plt.bar(agg["scheme_id"], agg["baseline_score"], color="#777777")
    
    plt.title("Average Baseline Risk by Scheme", pad=15)
    plt.xlabel("Scheme ID")
    plt.ylabel("Mean Baseline Score")
    plt.ylim(0, 1.0)
    
    # Rotate x labels if there are many schemes
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    
    filepath = os.path.join(FIGURES_DIR, "avg_risk_by_scheme.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    
    return filepath


def plot_counterfactual_effectiveness(df: pd.DataFrame) -> str:
    """
    PLOT 4: Bar Chart — Counterfactual Effectiveness
    X-axis: counterfactual type (CF1–CF4), Y-axis: average absolute delta
    """
    cf_cols = {
        "CF1: Awareness": "delta_cf_awareness",
        "CF2: Documentation": "delta_cf_documentation",
        "CF3: Assisted Access": "delta_cf_assisted_removal",
        "CF4: Digital": "delta_cf_digital_enablement"
    }
    
    impacts = {}
    for label, col in cf_cols.items():
        if col in df.columns:
            impacts[label] = df[col].abs().mean()
            
    # Convert to dataframe for plotting
    impact_df = pd.DataFrame(list(impacts.items()), columns=["CF Type", "Avg |Delta|"])
    impact_df = impact_df.sort_values("Avg |Delta|", ascending=False)
    
    plt.figure(figsize=(8, 6))
    
    bars = plt.bar(impact_df["CF Type"], impact_df["Avg |Delta|"], color="#444444")
    
    plt.title("Counterfactual Effectiveness\n(Average Absolute Change in Risk Score)", pad=15)
    plt.xlabel("Policy Lever (Intervention)")
    plt.ylabel("Mean Absolute Δ Score")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f"{yval:.4f}", ha='center', va='bottom', fontsize=10)
        
    plt.tight_layout()
    
    filepath = os.path.join(FIGURES_DIR, "counterfactual_effectiveness.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    
    return filepath


def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find '{CSV_PATH}'.")
        print("Please ensure you have run batch_simulation_v1.py first.")
        sys.exit(1)
        
    # --- 1. Load Data ---
    df = pd.read_csv(CSV_PATH)
    
    num_rows = len(df)
    unique_schemes = df["scheme_id"].nunique()
    unique_personas = df["persona_id"].nunique()
    
    # Check missing values
    missing_mask = df.isnull().any(axis=1)
    num_missing = missing_mask.sum()
    if num_missing > 0:
        # We fill NA with 0.0 just in case, though the model shouldn't output them.
        df = df.fillna(0.0)
    
    # --- 2. Generate Plots ---
    paths = []
    paths.append(plot_heatmap_baseline_risk(df))
    paths.append(plot_avg_risk_by_persona(df))
    paths.append(plot_avg_risk_by_scheme(df))
    paths.append(plot_counterfactual_effectiveness(df))
    
    # --- 3. Print Logs ---
    SEP = "=" * 70
    print(SEP)
    print("  REPORT-READY VISUALIZATIONS — GENERATION COMPLETE")
    print(SEP)
    for p in paths:
        print(f"  Generated: {os.path.basename(p)}")
        print(f"  -> {p}")
        
    # --- 4. Print Checker ---
    print("\n" + SEP)
    print("  CHECKER — PLOT VALIDATION SECTION")
    print(SEP)
    print(f"  [1] DATA READ: {num_rows} rows loaded from CSV.")
    print(f"  [2] UNIQUE ENTITIES: {unique_schemes} schemes, {unique_personas} personas.")
    
    missing_msg = "YES — no missing values found." if num_missing == 0 else f"NO — {num_missing} missing values imputed with 0.0."
    print(f"  [3] DATA COMPLETENESS: Ensure no missing values plotted? {missing_msg}")
    
    all_saved = all(os.path.exists(p) for p in paths)
    print(f"  [4] FILE SYSTEM CHECK: All 4 plots saved successfully? {'YES — PASS' if all_saved else 'NO — FAIL'}")
    print(SEP)


if __name__ == "__main__":
    # Ensure seaborn style is consistent and print-friendly
    sns.set_theme(style="whitegrid", rc={"axes.edgecolor": "0.15", "xtick.bottom": True, "ytick.left": True})
    main()
