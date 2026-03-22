import pandas as pd
import numpy as np

print("Loading cleaned data...")
uscis = pd.read_csv("uscis_clean.csv")
dol = pd.read_csv("dol_clean.csv")
uscis.columns = uscis.columns.str.strip()

print(f"USCIS rows: {len(uscis)}")
print(f"DOL rows: {len(dol)}")

# USCIS signals grouped by join_key
uscis_grouped = uscis.groupby("join_key").agg(
    total_approvals=("New Employment Approval", "sum"),
    total_denials=("New Employment Denial", "sum"),
    most_recent_year=("Fiscal Year", "max"),
    years_active=("Fiscal Year", "nunique"),
    clean_name=("clean_name", "first")
).reset_index()

current_year = 2025

# Signal 1: Recency score
uscis_grouped["recency_score"] = (
    (1 - ((current_year - uscis_grouped["most_recent_year"]) * 0.2))
    .clip(0, 1) * 100
).round(1)

# Signal 4: Approval rate
total_petitions = uscis_grouped["total_approvals"] + uscis_grouped["total_denials"]
uscis_grouped["approval_rate"] = (
    (uscis_grouped["total_approvals"] / total_petitions.replace(0, np.nan))
    .fillna(0) * 100
).round(1)

# Signal 3: Trend direction
print("\nCalculating trend signals (this may take a moment)...")

def calculate_trend(group):
    yearly = group.groupby("Fiscal Year")["New Employment Approval"].sum()
    if len(yearly) < 2:
        return 50
    recent = yearly.sort_index().tail(3)
    if len(recent) < 2:
        return 50
    trend = recent.diff().mean()
    if trend > 10:
        return 80
    elif trend > 0:
        return 65
    elif trend == 0:
        return 50
    elif trend > -10:
        return 35
    else:
        return 20

trend_result = uscis.groupby("join_key").apply(
    calculate_trend, include_groups=False
).reset_index()
trend_result.columns = ["join_key", "trend_score"]

uscis_grouped = uscis_grouped.merge(trend_result, on="join_key", how="left")
print(f"USCIS signals calculated for {len(uscis_grouped)} companies")

# DOL signals grouped by join_key
dol_grouped = dol.groupby("join_key").agg(
    total_lca_filings=("CASE_NUMBER", "count"),
    unique_soc_codes=("SOC_CODE", "nunique"),
    dol_clean_name=("clean_name", "first")
).reset_index()

def most_common_wage(group):
    wage_counts = group["PW_WAGE_LEVEL"].value_counts()
    if len(wage_counts) == 0:
        return "Unknown"
    return str(wage_counts.index[0])

most_common = dol.groupby("join_key").apply(
    most_common_wage, include_groups=False
).reset_index()
most_common.columns = ["join_key", "most_common_wage_level"]

dol_grouped = dol_grouped.merge(most_common, on="join_key", how="left")

# Wage level pivot
dol_wage = dol.groupby(["join_key", "PW_WAGE_LEVEL"]).size().reset_index(name="count")
dol_wage_pivot = dol_wage.pivot_table(
    index="join_key",
    columns="PW_WAGE_LEVEL",
    values="count",
    fill_value=0
).reset_index()
dol_wage_pivot.columns.name = None
wage_cols = {col: f"wage_level_{col}" for col in dol_wage_pivot.columns if col != "join_key"}
dol_wage_pivot = dol_wage_pivot.rename(columns=wage_cols)

dol_grouped = dol_grouped.merge(dol_wage_pivot, on="join_key", how="left")

# Entry level friendliness score
level_i = dol_grouped.get("wage_level_I", pd.Series(0, index=dol_grouped.index))
level_ii = dol_grouped.get("wage_level_II", pd.Series(0, index=dol_grouped.index))
total_wage = dol_grouped["total_lca_filings"].replace(0, np.nan)
dol_grouped["entry_level_score"] = (
    ((level_i + level_ii) / total_wage).fillna(0) * 100
).round(1)

# Lottery odds score
lottery_map = {"I": 15, "II": 31, "III": 46, "IV": 61}
dol_grouped["lottery_odds_score"] = (
    dol_grouped["most_common_wage_level"]
    .map(lottery_map)
    .fillna(25)
)

print(f"DOL signals calculated for {len(dol_grouped)} companies")

# Save SOC distribution using join_key
soc_distribution = dol.groupby(["join_key", "SOC_CODE"]).size().reset_index(name="count")
soc_distribution.to_csv("soc_distribution.csv", index=False)
print(f"SOC distribution saved: {len(soc_distribution)} rows")

# Combine all signals on join_key
print("\nCombining all signals...")
signals = uscis_grouped.merge(dol_grouped, on="join_key", how="outer")

# Confidence score
def calculate_confidence(row):
    confidence = 78
    if pd.isna(row.get("total_approvals")) or row.get("total_approvals", 0) < 10:
        confidence -= 20
    if not pd.isna(row.get("most_recent_year")):
        if (current_year - row["most_recent_year"]) > 2:
            confidence -= 15
    if pd.isna(row.get("total_lca_filings")) or row.get("total_lca_filings", 0) == 0:
        confidence -= 15
    return max(confidence, 10)

signals["confidence"] = signals.apply(calculate_confidence, axis=1)

# Save
signals.to_csv("company_signals.csv", index=False)
print(f"\nDone. company_signals.csv saved with {len(signals)} companies")
print(f"Columns: {list(signals.columns)}")

# Test on Amazon
test = signals[signals["join_key"].str.contains("AMAZONCOMSERVICES", na=False)]
if len(test) > 0:
    print("\nSample: AMAZON COM SERVICES signals")
    print(test[["join_key", "recency_score", "approval_rate", "trend_score",
                "entry_level_score", "lottery_odds_score", "confidence"]].to_string())
else:
    print("\nAmazon not found in test. Checking nearby matches:")
    print(signals[signals["join_key"].str.contains("AMAZON", na=False)][
        ["join_key", "recency_score", "approval_rate", "entry_level_score", "confidence"]
    ].head(5).to_string())