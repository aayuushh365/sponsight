import pandas as pd
import numpy as np
import re

signals = pd.read_csv("company_signals.csv")
soc_dist = pd.read_csv("soc_distribution.csv")

def make_join_key(name):
    if pd.isna(name):
        return ""
    name = str(name).upper().strip()
    name = re.sub(r'[.,]', '', name)
    suffixes = [' LLC', ' INC', ' CORP', ' LTD', ' LP',
                ' PC', ' NA', ' CO', ' US']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    name = re.sub(r'\s+', '', name)
    return name

ROLE_SOC_MAP = {
    "Software Engineer": ["15-1252", "15-1253", "15-1254"],
    "Data Scientist": ["15-2051", "15-1221"],
    "Data Engineer": ["15-1242", "15-1243"],
    "Product Manager": ["15-1299", "11-3021"],
    "Business Analyst": ["15-2031", "13-1111"],
    "Financial Analyst": ["13-2051", "13-2061"],
    "Mechanical Engineer": ["17-2141", "17-2199"],
    "Electrical Engineer": ["17-2071", "17-2072"],
    "Civil Engineer": ["17-2051", "17-2061"],
    "UX Designer": ["27-1021", "15-1255"],
    "Marketing Analyst": ["13-1161", "13-1199"],
    "Supply Chain Manager": ["13-1081", "11-3071"],
}

def calculate_role_match(join_key, role):
    target_soc_prefixes = ROLE_SOC_MAP.get(role, [])
    if not target_soc_prefixes:
        return 50.0

    company_soc = soc_dist[soc_dist["join_key"] == join_key]
    if len(company_soc) == 0:
        return 0.0

    total = company_soc["count"].sum()
    matching = company_soc[
        company_soc["SOC_CODE"].astype(str).apply(
            lambda x: any(x.startswith(prefix) for prefix in target_soc_prefixes)
        )
    ]["count"].sum()

    if total == 0:
        return 0.0
    return round(float(matching / total) * 100, 1)

def get_score(company_search, role):
    search_key = make_join_key(company_search)

    matches = signals[
        signals["join_key"].str.contains(search_key, na=False)
    ]

    if len(matches) == 0:
        return {
            "found": False,
            "message": f"No data found for '{company_search}'. Try a shorter search term."
        }

    # Option B: aggregate all matching entities into one combined picture
    total_approvals_all = matches["total_approvals"].fillna(0).sum()
    total_denials_all = matches["total_denials"].fillna(0).sum()
    most_recent_year_all = matches["most_recent_year"].max()
    total_lca_all = matches["total_lca_filings"].fillna(0).sum()

    # Use the row with most approvals for name display and single-value signals
    row = matches.loc[matches["total_approvals"].fillna(0).idxmax()]
    join_key = row["join_key"]

    # Override totals with aggregated values
    total_approvals_combined = int(total_approvals_all)
    approval_rate_combined = (
        round(float(total_approvals_all / (total_approvals_all + total_denials_all)) * 100, 1)
        if (total_approvals_all + total_denials_all) > 0 else 50.0
    )

    # Aggregate wage levels across all entities for entry level score
    level_i_total = matches["wage_level_I"].fillna(0).sum()
    level_ii_total = matches["wage_level_II"].fillna(0).sum()
    entry_level_combined = (
        round(float((level_i_total + level_ii_total) / total_lca_all) * 100, 1)
        if total_lca_all > 0 else 50.0
    )

    # Display name shows all entities found
    entity_count = len(matches)
    display_name = row.get("clean_name", search_key)
    if pd.isna(display_name):
        display_name = row.get("dol_clean_name", search_key)
    if entity_count > 1:
        display_name = f"{display_name} (and {entity_count - 1} related entities)"

    display_name = row.get("clean_name", join_key)
    if pd.isna(display_name):
        display_name = row.get("dol_clean_name", join_key)

    recency = row.get("recency_score", 50)
    approval = row.get("approval_rate", 50)
    trend = row.get("trend_score", 50)
    entry_level = row.get("entry_level_score", 50)
    lottery = row.get("lottery_odds_score", 25)
    role_match = calculate_role_match(join_key, role)

    recency = 50.0 if pd.isna(recency) else float(recency)
    approval = approval_rate_combined
    trend = 50.0 if pd.isna(trend) else float(trend)
    entry_level = entry_level_combined
    lottery = 25.0 if pd.isna(lottery) else float(lottery)

    total_approvals = total_approvals_combined

    if total_approvals >= 500:
        volume_score = 90.0
    elif total_approvals >= 100:
        volume_score = 75.0
    elif total_approvals >= 20:
        volume_score = 60.0
    elif total_approvals >= 5:
        volume_score = 40.0
    else:
        volume_score = 20.0

    final_score = (
        recency * 0.25 +
        role_match * 0.20 +
        trend * 0.15 +
        volume_score * 0.15 +
        approval * 0.10 +
        entry_level * 0.10 +
        lottery * 0.05
    )
    final_score = round(min(max(final_score, 0), 100), 1)

    confidence = row.get("confidence", 43)
    confidence = 43 if pd.isna(confidence) else int(confidence)

    wage_level = row.get("most_common_wage_level", "Unknown")
    if pd.isna(wage_level):
        wage_level = "Unknown"

    lottery_text_map = {
        "I": "roughly 15% under the 2026 wage-weighted lottery",
        "II": "roughly 31% under the 2026 wage-weighted lottery",
        "III": "roughly 46% under the 2026 wage-weighted lottery",
        "IV": "roughly 61% under the 2026 wage-weighted lottery",
    }
    lottery_text = lottery_text_map.get(
        str(wage_level),
        "unknown under the current lottery system"
    )

    most_recent = row.get("most_recent_year", 0)
    most_recent = "Unknown" if pd.isna(most_recent) else int(most_recent)

    return {
        "found": True,
        "company_name": str(display_name),
        "role": role,
        "final_score": float(final_score),
        "confidence": int(confidence),
        "signals": {
            "recency": float(recency),
            "approval_rate": float(approval),
            "trend": float(trend),
            "role_match": float(role_match),
            "entry_level": float(entry_level),
            "volume": float(volume_score),
        },
        "wage_level": str(wage_level),
        "lottery_text": lottery_text,
        "total_approvals": int(total_approvals),
        "most_recent_year": most_recent,
    }

if __name__ == "__main__":
    result = get_score("AMAZON COM", "Software Engineer")
    print("\nTest: Amazon COM Services - Software Engineer")
    for key, value in result.items():
        print(f"  {key}: {value}")

    result2 = get_score("GOOGLE", "Product Manager")
    print("\nTest: Google - Product Manager")
    for key, value in result2.items():
        print(f"  {key}: {value}")

    result3 = get_score("MICROSOFT", "Data Scientist")
    print("\nTest: Microsoft - Data Scientist")
    for key, value in result3.items():
        print(f"  {key}: {value}")