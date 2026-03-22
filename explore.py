import pandas as pd
import re

# ── Load both datasets ──────────────────────────────────────────────

# Load USCIS file and strip whitespace from column names
uscis = pd.read_excel("Employer Information.xlsx")
uscis.columns = uscis.columns.str.strip()

# Load DOL file
dol = pd.read_excel("LCA_Disclosure_Data_FY2026_Q1.xlsx")

print("USCIS loaded:", len(uscis), "rows")
print("DOL loaded:", len(dol), "rows")

# ── Define the cleaning function ────────────────────────────────────
# This function takes any company name string and returns
# a standardized version that will match across both datasets

def clean_name(name):
    if pd.isna(name):
        return ""
    name = str(name)
    name = name.upper()              # make everything uppercase
    name = name.strip()              # remove leading/trailing spaces
    name = re.sub(r'[.,]', '', name) # remove periods and commas
    # remove common legal suffixes that vary between datasets
    suffixes = [' LLC', ' INC', ' CORP', ' LTD', ' LP', 
                ' PC', ' NA', ' CO', ' US']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    name = re.sub(r'\s+', ' ', name) # collapse multiple spaces to one
    return name

# ── Apply the cleaning function ─────────────────────────────────────

uscis["clean_name"] = uscis["Employer (Petitioner) Name"].apply(clean_name)
dol["clean_name"] = dol["EMPLOYER_NAME"].apply(clean_name)

# ── Test the results on Amazon ──────────────────────────────────────

print("\nCleaned Amazon names in USCIS:")
amazon_uscis = uscis[uscis["clean_name"].str.contains("AMAZON", na=False)]
print(amazon_uscis["clean_name"].unique())

print("\nCleaned Amazon names in DOL:")
amazon_dol = dol[dol["clean_name"].str.contains("AMAZON", na=False)]
print(amazon_dol["clean_name"].unique())

# ── Check how many names now match between the two datasets ─────────

uscis_names = set(uscis["clean_name"].unique())
dol_names = set(dol["clean_name"].unique())
overlap = uscis_names.intersection(dol_names)

print("\nUnique names in USCIS:", len(uscis_names))
print("Unique names in DOL:", len(dol_names))
print("Names that match between both datasets:", len(overlap))
# Find names that appear in USCIS but NOT in DOL
only_in_uscis = uscis_names - dol_names
# Show ones containing AMAZON to check
amazon_only_uscis = [n for n in only_in_uscis if "AMAZON" in n]
print("\nAmazon names in USCIS that did NOT match DOL:")
print(sorted(amazon_only_uscis))

amazon_only_dol = [n for n in (dol_names - uscis_names) if "AMAZON" in n]
print("\nAmazon names in DOL that did NOT match USCIS:")
print(sorted(amazon_only_dol))