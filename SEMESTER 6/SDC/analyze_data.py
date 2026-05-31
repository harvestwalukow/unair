import pandas as pd
import numpy as np

file_path = "Study Case for Univ Airlangga 2026 _Actuarial AXA.xlsx"

# Read Raw Data
df = pd.read_excel(file_path, sheet_name='Raw Data')

# Calculate Total Claims (Settled + Outstanding)
df['TOTAL_CLAIM_GROSS'] = df['GROSS ST'] + df['GROSS OS']

# Aggregate by CLASS OF BUSINESS
cob_agg = df.groupby('CLASS OF BUSINESS').agg({
    'GWP': 'sum',
    'SUM INSURED': 'sum',
    'TOTAL_CLAIM_GROSS': 'sum',
    'POLICY NO': 'count'
}).reset_index()
cob_agg['LOSS_RATIO'] = cob_agg['TOTAL_CLAIM_GROSS'] / cob_agg['GWP']
cob_agg = cob_agg.sort_values('LOSS_RATIO', ascending=False)

# Aggregate by CHANNEL
ch_agg = df.groupby('CHANNEL').agg({
    'GWP': 'sum',
    'SUM INSURED': 'sum',
    'TOTAL_CLAIM_GROSS': 'sum',
    'POLICY NO': 'count'
}).reset_index()
ch_agg['LOSS_RATIO'] = ch_agg['TOTAL_CLAIM_GROSS'] / ch_agg['GWP']
ch_agg = ch_agg.sort_values('LOSS_RATIO', ascending=False)

# Aggregate by COB and CHANNEL (Top 10 by Loss Ratio)
cob_ch_agg = df.groupby(['CLASS OF BUSINESS', 'CHANNEL']).agg({
    'GWP': 'sum',
    'SUM INSURED': 'sum',
    'TOTAL_CLAIM_GROSS': 'sum',
    'POLICY NO': 'count'
}).reset_index()
cob_ch_agg['LOSS_RATIO'] = cob_ch_agg['TOTAL_CLAIM_GROSS'] / cob_ch_agg['GWP']
cob_ch_agg = cob_ch_agg[cob_ch_agg['GWP'] > 0] # Filter out 0 GWP to avoid infinity
cob_ch_agg = cob_ch_agg.sort_values('LOSS_RATIO', ascending=False).head(10)

with open("analysis_results.txt", "w", encoding="utf-8") as f:
    f.write("=== OVERALL PORTFOLIO ===\n")
    f.write(f"Total Policies: {df.shape[0]}\n")
    f.write(f"Total GWP: {df['GWP'].sum():,.2f}\n")
    f.write(f"Total Sum Insured: {df['SUM INSURED'].sum():,.2f}\n")
    f.write(f"Total Claims Gross: {df['TOTAL_CLAIM_GROSS'].sum():,.2f}\n")
    overall_lr = df['TOTAL_CLAIM_GROSS'].sum() / df['GWP'].sum() if df['GWP'].sum() > 0 else 0
    f.write(f"Overall Loss Ratio: {overall_lr:.2%}\n\n")

    f.write("=== BY CLASS OF BUSINESS ===\n")
    f.write(cob_agg.to_string())
    f.write("\n\n")

    f.write("=== BY CHANNEL ===\n")
    f.write(ch_agg.to_string())
    f.write("\n\n")

    f.write("=== TOP 10 RISK SEGMENTS (COB + CHANNEL) by Loss Ratio ===\n")
    f.write(cob_ch_agg.to_string())
    f.write("\n")

print("Analysis done.")
