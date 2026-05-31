"""
Analisis: Delivery Delay vs Repeat Order
=========================================
Pertanyaan: Apakah pelanggan yang mengalami keterlambatan pengiriman
cenderung TIDAK melakukan repeat order?

Ini menghubungkan delivery delay dengan "slowing transaction growth".
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os, warnings
from scipy import stats

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 120

DATA_DIR = r"d:\UNAIR\SEMESTER 6\AKB"

# --- Load ---
orders    = pd.read_csv(os.path.join(DATA_DIR, "olist_orders_dataset.csv"))
items     = pd.read_csv(os.path.join(DATA_DIR, "olist_order_items_dataset.csv"))
customers = pd.read_csv(os.path.join(DATA_DIR, "olist_customers_dataset.csv"))
reviews   = pd.read_csv(os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv"))

for col in ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
    orders[col] = pd.to_datetime(orders[col])

# --- Join orders with customers to get customer_unique_id ---
df = orders.merge(customers[['customer_id', 'customer_unique_id']], on='customer_id', how='inner')

# Filter delivered orders only
df = df[df['order_status'] == 'delivered'].copy()

# Calculate delivery metrics
df['delivery_duration'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
df['delivery_delay'] = df['delivery_duration'] - (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
df['is_late'] = df['delivery_delay'] > 0

# Add review scores
reviews_d = reviews.sort_values('review_creation_date').drop_duplicates(subset='order_id', keep='last')[['order_id', 'review_score']]
df = df.merge(reviews_d, on='order_id', how='left')

# Sort by customer and purchase date
df = df.sort_values(['customer_unique_id', 'order_purchase_timestamp'])

print("=" * 70)
print("ANALISIS: DELIVERY DELAY vs REPEAT ORDER")
print("=" * 70)
print(f"Total delivered orders: {len(df):,}")
print(f"Total unique customers: {df['customer_unique_id'].nunique():,}")

# =================================================================
# 1. IDENTIFIKASI REPEAT vs ONE-TIME CUSTOMERS
# =================================================================
print("\n" + "=" * 70)
print("1. IDENTIFIKASI REPEAT vs ONE-TIME CUSTOMERS")
print("=" * 70)

customer_orders = df.groupby('customer_unique_id').agg(
    order_count=('order_id', 'nunique'),
    first_order=('order_purchase_timestamp', 'min'),
    last_order=('order_purchase_timestamp', 'max'),
).reset_index()

customer_orders['is_repeat'] = customer_orders['order_count'] > 1

repeat_count = customer_orders['is_repeat'].sum()
total_customers = len(customer_orders)
print(f"\nOne-time customers: {total_customers - repeat_count:,} ({(total_customers - repeat_count)/total_customers:.1%})")
print(f"Repeat customers:   {repeat_count:,} ({repeat_count/total_customers:.1%})")

# =================================================================
# 2. PENGALAMAN PERTAMA & REPEAT BEHAVIOR
# =================================================================
print("\n" + "=" * 70)
print("2. APAKAH DELAY DI ORDER PERTAMA MEMPENGARUHI REPEAT?")
print("=" * 70)

# Get FIRST order per customer
first_orders = df.drop_duplicates(subset='customer_unique_id', keep='first').copy()
first_orders = first_orders.merge(
    customer_orders[['customer_unique_id', 'is_repeat', 'order_count']],
    on='customer_unique_id', how='left'
)

# Filter to orders with delivery data
first_orders = first_orders.dropna(subset=['delivery_delay'])

# Repeat rate by first-order delivery experience
first_orders['first_order_status'] = first_orders['is_late'].map({True: 'Late', False: 'On-Time'})

repeat_by_experience = first_orders.groupby('first_order_status').agg(
    total_customers=('customer_unique_id', 'count'),
    repeat_customers=('is_repeat', 'sum'),
).reset_index()
repeat_by_experience['repeat_rate'] = repeat_by_experience['repeat_customers'] / repeat_by_experience['total_customers']

print("\n--- Repeat Rate berdasarkan Pengalaman Order Pertama ---")
print(repeat_by_experience.to_string(index=False))

# Chi-square test
ct = pd.crosstab(first_orders['first_order_status'], first_orders['is_repeat'])
chi2, p_chi, _, _ = stats.chi2_contingency(ct)
n_total = ct.sum().sum()
cramers_v = np.sqrt(chi2 / (n_total * (min(ct.shape) - 1)))

print(f"\nChi-square = {chi2:.2f}, p = {p_chi:.4e}")
print(f"Cramer's V = {cramers_v:.4f}")

# =================================================================
# 3. REPEAT RATE BY REVIEW SCORE (FIRST ORDER)
# =================================================================
print("\n" + "=" * 70)
print("3. REPEAT RATE BY REVIEW SCORE (ORDER PERTAMA)")
print("=" * 70)

repeat_by_score = first_orders.groupby('review_score').agg(
    total=('customer_unique_id', 'count'),
    repeaters=('is_repeat', 'sum'),
).reset_index()
repeat_by_score['repeat_rate'] = repeat_by_score['repeaters'] / repeat_by_score['total']

print(repeat_by_score.to_string(index=False))

# =================================================================
# 4. REPEAT RATE BY DELAY SEVERITY
# =================================================================
print("\n" + "=" * 70)
print("4. REPEAT RATE BY DELAY SEVERITY")
print("=" * 70)

first_orders['delay_category'] = pd.cut(
    first_orders['delivery_delay'],
    bins=[-999, -7, 0, 7, 14, 999],
    labels=['7+ hari lebih awal', '1-7 hari lebih awal', '0-7 hari terlambat', '7-14 hari terlambat', '14+ hari terlambat']
)

repeat_by_delay = first_orders.groupby('delay_category', observed=True).agg(
    total=('customer_unique_id', 'count'),
    repeaters=('is_repeat', 'sum'),
).reset_index()
repeat_by_delay['repeat_rate'] = repeat_by_delay['repeaters'] / repeat_by_delay['total']

print(repeat_by_delay.to_string(index=False))

# =================================================================
# 5. CUSTOMER LIFETIME — ORDERS AFTER LATE DELIVERY
# =================================================================
print("\n" + "=" * 70)
print("5. RATA-RATA JUMLAH ORDER PER CUSTOMER")
print("=" * 70)

avg_orders_ontime = first_orders[first_orders['first_order_status'] == 'On-Time']['order_count'].mean()
avg_orders_late = first_orders[first_orders['first_order_status'] == 'Late']['order_count'].mean()

print(f"Avg orders (first order On-Time): {avg_orders_ontime:.3f}")
print(f"Avg orders (first order Late):    {avg_orders_late:.3f}")

# Mann-Whitney U test
u_stat, p_mw = stats.mannwhitneyu(
    first_orders[first_orders['first_order_status'] == 'On-Time']['order_count'],
    first_orders[first_orders['first_order_status'] == 'Late']['order_count'],
    alternative='two-sided'
)
print(f"Mann-Whitney U p-value: {p_mw:.4e}")

# =================================================================
# 6. ESTIMATED REVENUE IMPACT
# =================================================================
print("\n" + "=" * 70)
print("6. ESTIMASI DAMPAK REVENUE")
print("=" * 70)

items_agg = items.groupby('order_id').agg(total_price=('price', 'sum')).reset_index()
first_w_price = first_orders.merge(items_agg, on='order_id', how='left')

avg_order_value = first_w_price['total_price'].mean()
late_first_orders = len(first_orders[first_orders['first_order_status'] == 'Late'])

ontime_repeat_rate = repeat_by_experience[repeat_by_experience['first_order_status'] == 'On-Time']['repeat_rate'].values[0]
late_repeat_rate = repeat_by_experience[repeat_by_experience['first_order_status'] == 'Late']['repeat_rate'].values[0]

lost_repeaters = late_first_orders * (ontime_repeat_rate - late_repeat_rate)
lost_revenue = lost_repeaters * avg_order_value

print(f"Avg order value: R$ {avg_order_value:,.2f}")
print(f"Customers with late first order: {late_first_orders:,}")
print(f"Repeat rate gap: {ontime_repeat_rate:.2%} - {late_repeat_rate:.2%} = {ontime_repeat_rate - late_repeat_rate:.2%}")
print(f"Estimated lost repeat customers: {lost_repeaters:,.0f}")
print(f"Estimated lost revenue: R$ {lost_revenue:,.2f}")

# =================================================================
# 7. VISUALIZATIONS
# =================================================================
print("\n" + "=" * 70)
print("7. GENERATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# --- Chart A: Repeat Rate — On-Time vs Late ---
colors_bar = ['#27ae60', '#e74c3c']
bars_a = axes[0].bar(
    repeat_by_experience['first_order_status'],
    repeat_by_experience['repeat_rate'] * 100,
    color=colors_bar, edgecolor='white', width=0.5
)
for bar, val in zip(bars_a, repeat_by_experience['repeat_rate'] * 100):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.2f}%', ha='center', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Repeat Purchase Rate (%)', fontsize=11)
axes[0].set_title('Repeat Rate:\nOn-Time vs Late (First Order)', fontsize=12, fontweight='bold')
axes[0].set_ylim(0, max(repeat_by_experience['repeat_rate'] * 100) * 1.4)

# --- Chart B: Repeat Rate by Delay Severity ---
colors_delay = ['#27ae60', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
bars_b = axes[1].barh(
    repeat_by_delay['delay_category'],
    repeat_by_delay['repeat_rate'] * 100,
    color=colors_delay, edgecolor='white', height=0.6
)
for bar, val in zip(bars_b, repeat_by_delay['repeat_rate'] * 100):
    axes[1].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}%', va='center', fontsize=10, fontweight='bold')
axes[1].set_xlabel('Repeat Rate (%)', fontsize=11)
axes[1].set_title('Repeat Rate by\nDelay Severity', fontsize=12, fontweight='bold')
axes[1].invert_yaxis()

# --- Chart C: Repeat Rate by Review Score ---
colors_score = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60']
bars_c = axes[2].bar(
    repeat_by_score['review_score'],
    repeat_by_score['repeat_rate'] * 100,
    color=colors_score, edgecolor='white', width=0.6
)
for bar, val in zip(bars_c, repeat_by_score['repeat_rate'] * 100):
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                 f'{val:.2f}%', ha='center', fontsize=10, fontweight='bold')
axes[2].set_xlabel('Review Score (First Order)', fontsize=11)
axes[2].set_ylabel('Repeat Rate (%)', fontsize=11)
axes[2].set_title('Repeat Rate by\nFirst Order Review Score', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(DATA_DIR, "fig5_delay_vs_repeat_order.png"), bbox_inches='tight')
print("Saved: fig5_delay_vs_repeat_order.png")
plt.close()

print("\nAnalysis complete.")
