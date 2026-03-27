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

# Comprehensive role to SOC code mapping
# Each entry maps a plain-language role name to SOC code prefixes found in DOL LCA data
ROLE_SOC_MAP = {
    # Technology
    "Software Engineer":          ["15-1252", "15-1253", "15-1254", "15-1256"],
    "Data Scientist":             ["15-2051", "15-1221", "15-2041"],
    "Data Engineer":              ["15-1242", "15-1243", "15-1244"],
    "Data Analyst":               ["15-2031", "15-2041", "13-2011"],
    "Machine Learning Engineer":  ["15-2051", "15-1221", "15-1252"],
    "AI / ML Researcher":         ["15-2051", "15-1221", "15-2041"],
    "DevOps / Cloud Engineer":    ["15-1244", "15-1241", "15-1231"],
    "Site Reliability Engineer":  ["15-1244", "15-1241", "15-1231"],
    "Cybersecurity Analyst":      ["15-1212", "15-1299", "15-1211"],
    "Network Engineer":           ["15-1241", "15-1231", "15-1244"],
    "Systems Architect":          ["15-1243", "15-1299", "15-1241"],
    "Database Administrator":     ["15-1242", "15-1244"],
    "QA / Test Engineer":         ["15-1253", "15-1256", "15-1299"],
    "Full Stack Developer":       ["15-1252", "15-1253", "15-1254"],
    "Frontend Developer":         ["15-1254", "15-1252", "15-1255"],
    "Embedded Systems Engineer":  ["17-2061", "17-2112", "15-1299"],
    "Blockchain Engineer":        ["15-1252", "15-1299"],
    # Product and Design
    "Product Manager":            ["15-1299", "11-3021", "11-2021"],
    "UX Designer":                ["27-1021", "15-1255", "27-1024"],
    "UI Designer":                ["27-1021", "15-1255", "27-1024"],
    "Product Designer":           ["27-1021", "15-1255", "27-1024"],
    # Business and Operations
    "Business Analyst":           ["15-2031", "13-1111", "13-1161"],
    "Operations Analyst":         ["15-2031", "13-1111", "11-1021"],
    "Project Manager":            ["11-3021", "13-1082", "15-1299"],
    "Program Manager":            ["11-3021", "13-1082"],
    "Management Consultant":      ["13-1111", "13-1199", "11-9199"],
    "Strategy Analyst":           ["13-1111", "11-9199"],
    "Supply Chain Manager":       ["13-1081", "11-3071", "13-1199"],
    "Logistics Analyst":          ["13-1081", "11-3071"],
    "Human Resources Manager":    ["11-3121", "13-1071", "13-1151"],
    "Recruiter / Talent Acq":     ["13-1071", "13-1151"],
    # Finance and Accounting
    "Financial Analyst":          ["13-2051", "13-2061", "13-2041"],
    "Investment Analyst":         ["13-2051", "13-2099", "23-2011"],
    "Quantitative Analyst":       ["13-2051", "15-2041", "15-2031"],
    "Actuary":                    ["15-2011"],
    "Accountant / Auditor":       ["13-2011", "13-2031"],
    "Tax Analyst":                ["13-2082", "13-2011"],
    # Engineering (non-software)
    "Mechanical Engineer":        ["17-2141", "17-2199", "17-2131"],
    "Electrical Engineer":        ["17-2071", "17-2072", "17-2061"],
    "Civil Engineer":             ["17-2051", "17-2061", "17-2081"],
    "Chemical Engineer":          ["17-2041"],
    "Biomedical Engineer":        ["17-2031", "17-2199"],
    "Industrial Engineer":        ["17-2112", "17-2199"],
    "Aerospace Engineer":         ["17-2011", "17-2021"],
    "Environmental Engineer":     ["17-2081", "19-2041"],
    "Structural Engineer":        ["17-2051", "17-2061"],
    # Science and Research
    "Biochemist / Biologist":     ["19-1021", "19-1029", "19-1099"],
    "Chemist":                    ["19-2031", "19-2041"],
    "Statistician":               ["15-2041", "15-2031"],
    "Economist":                  ["19-3011"],
    "Clinical Research Associate":["19-1042", "29-9099"],
    # Healthcare
    "Pharmacist":                 ["29-1051"],
    "Physical Therapist":         ["29-1123"],
    "Physician / Doctor":         ["29-1060", "29-1069", "29-1220"],
    "Registered Nurse":           ["29-1141"],
    "Healthcare Administrator":   ["11-9111", "13-1121"],
    # Architecture and Urban Planning
    "Architect":                  ["17-1011", "17-1012"],
    "Urban / City Planner":       ["19-3051"],
    # Marketing and Communications
    "Marketing Analyst":          ["13-1161", "13-1199", "11-2021"],
    "Marketing Manager":          ["11-2021", "13-1161"],
    "SEO / Digital Marketing":    ["13-1161", "15-1255"],
    # Legal
    "Attorney / Lawyer":          ["23-1011"],
    "Paralegal":                  ["23-2011"],
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
            lambda x: any(x.startswith(p) for p in target_soc_prefixes)
        )
    ]["count"].sum()
    if total == 0:
        return 0.0
    return round(float(matching / total) * 100, 1)

def get_score(company_search, role):
    search_key = make_join_key(company_search)
    matches = signals[signals["join_key"].str.startswith(search_key, na=False)]

    if len(matches) == 0:
        return {"found": False, "message": f"No data found for '{company_search}'. Try a shorter search term."}

    # Aggregate all matching entities
    total_approvals_all = matches["total_approvals"].fillna(0).sum()
    total_denials_all = matches["total_denials"].fillna(0).sum()
    most_recent_year_all = matches["most_recent_year"].max()
    total_lca_all = matches["total_lca_filings"].fillna(0).sum()

    row = matches.loc[matches["total_approvals"].fillna(0).idxmax()]
    join_key = row["join_key"]

    total_approvals_combined = int(total_approvals_all)
    approval_rate_combined = (
        round(float(total_approvals_all / (total_approvals_all + total_denials_all)) * 100, 1)
        if (total_approvals_all + total_denials_all) > 0 else 50.0
    )
    level_i_total = matches["wage_level_I"].fillna(0).sum()
    level_ii_total = matches["wage_level_II"].fillna(0).sum()
    entry_level_combined = (
        round(float((level_i_total + level_ii_total) / total_lca_all) * 100, 1)
        if total_lca_all > 0 else 50.0
    )

    display_name = row.get("clean_name", search_key)
    if pd.isna(display_name):
        display_name = row.get("dol_clean_name", search_key)
    # Do not append entity count — it confuses users
    # The aggregation is an internal detail, not a user-facing feature

    recency = row.get("recency_score", 50)
    trend = row.get("trend_score", 50)
    recency = 50.0 if pd.isna(recency) else float(recency)
    trend = 50.0 if pd.isna(trend) else float(trend)
    lottery = row.get("lottery_odds_score", 25)
    lottery = 25.0 if pd.isna(lottery) else float(lottery)
    role_match = calculate_role_match(join_key, role)

    if total_approvals_combined >= 500:
        volume_score = 90.0
    elif total_approvals_combined >= 100:
        volume_score = 75.0
    elif total_approvals_combined >= 20:
        volume_score = 60.0
    elif total_approvals_combined >= 5:
        volume_score = 40.0
    else:
        volume_score = 20.0

    # Recalibrated weights:
    # For high-volume employers (500+ approvals), role_match is penalized
    # less because large companies file across many role types by necessity.
    # Approval rate and volume carry more weight as primary trust signals.
    role_match_weight = 0.15 if total_approvals_combined >= 500 else 0.20
    recency_weight = 0.25
    trend_weight = 0.12
    volume_weight = 0.18
    approval_weight = 0.15
    entry_weight = 0.10
    lottery_weight = 0.05

    # Normalize approval rate to 0-100 scale (it already is)
    # Boost: companies with >95% approval and >500 approvals get a base bonus
    approval_bonus = 3.0 if (approval_rate_combined >= 95 and total_approvals_combined >= 500) else 0.0

    final_score = (
        recency * recency_weight +
        role_match * role_match_weight +
        trend * trend_weight +
        volume_score * volume_weight +
        approval_rate_combined * approval_weight +
        entry_level_combined * entry_weight +
        lottery * lottery_weight +
        approval_bonus
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
    lottery_text = lottery_text_map.get(str(wage_level), "unknown under the current lottery system")

    most_recent = most_recent_year_all
    most_recent = "Unknown" if pd.isna(most_recent) else int(most_recent)

    return {
        "found": True,
        "company_name": str(display_name),
        "role": role,
        "final_score": float(final_score),
        "confidence": int(confidence),
        "signals": {
            "recency": float(recency),
            "approval_rate": float(approval_rate_combined),
            "trend": float(trend),
            "role_match": float(role_match),
            "entry_level": float(entry_level_combined),
            "volume": float(volume_score),
        },
        "wage_level": str(wage_level),
        "lottery_text": lottery_text,
        "total_approvals": total_approvals_combined,
        "most_recent_year": most_recent,
    }