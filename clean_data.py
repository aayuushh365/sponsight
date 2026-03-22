import pandas as pd
import re
import os

def clean_name(name):
    if pd.isna(name):
        return ""
    name = str(name).upper().strip()
    name = re.sub(r'[.,]', '', name)
    suffixes = [' LLC', ' INC', ' CORP', ' LTD', ' LP',
                ' PC', ' NA', ' CO', ' US']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    name = re.sub(r'\s+', ' ', name)
    return name

def make_join_key(clean):
    # Remove all spaces for joining
    # This handles cases where one dataset has "AMAZON COM" 
    # and another has "AMAZONCOM"
    return re.sub(r'\s+', '', clean)

# Load and clean USCIS
print("Loading USCIS files...")
uscis_frames = []
for filename in os.listdir("."):
    if "Employer Information" in filename and filename.endswith(".xlsx"):
        print(f"  Reading {filename}")
        df = pd.read_excel(filename)
        df.columns = df.columns.str.strip()
        uscis_frames.append(df)

uscis = pd.concat(uscis_frames, ignore_index=True)
uscis["clean_name"] = uscis["Employer (Petitioner) Name"].apply(clean_name)
uscis["join_key"] = uscis["clean_name"].apply(make_join_key)

print(f"USCIS total rows: {len(uscis)}")

# Load and clean DOL
print("\nLoading DOL file...")
dol = pd.read_excel("LCA_Disclosure_Data_FY2026_Q1.xlsx")
dol = dol[dol["CASE_STATUS"] == "Certified"]
dol = dol[dol["VISA_CLASS"] == "H-1B"]
dol["clean_name"] = dol["EMPLOYER_NAME"].apply(clean_name)
dol["join_key"] = dol["clean_name"].apply(make_join_key)

print(f"DOL total rows after filtering: {len(dol)}")

# Save cleaned files
uscis.to_csv("uscis_clean.csv", index=False)
dol.to_csv("dol_clean.csv", index=False)
print("\nFiles saved: uscis_clean.csv and dol_clean.csv")

# Check overlap using join_key instead of clean_name
uscis_keys = set(uscis["join_key"].unique())
dol_keys = set(dol["join_key"].unique())
overlap = uscis_keys.intersection(dol_keys)
print(f"Companies matching with join_key: {len(overlap)}")

# Verify Amazon fix
amazon_uscis = uscis[uscis["clean_name"].str.contains("AMAZON COM", na=False)]
amazon_dol = dol[dol["clean_name"].str.contains("AMAZONCOM", na=False)]
print("\nAmazon join_key in USCIS:", amazon_uscis["join_key"].unique()[:3])
print("Amazon join_key in DOL:", amazon_dol["join_key"].unique()[:3])