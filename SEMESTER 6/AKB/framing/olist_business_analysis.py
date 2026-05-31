"""
Olist E-Commerce Business Framing & Exploratory Data Analysis
=============================================================
Objective: Determine which business framing (Delivery Delay, Seller/Product Quality,
or Shipping Cost) is best supported by the data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 120

DATA_DIR = r"d:\UNAIR\SEMESTER 6\AKB"
OUTPUT_DIR = DATA_DIR  # save charts alongside data

# =============================================================================
# 1. LOAD ALL DATASETS & INSPECT SCHEMAS
# =============================================================================
print("=" * 70)
print("1. LOADING DATASETS & SCHEMA INSPECTION")
print("=" * 70)

orders      = pd.read_csv(os.path.join(DATA_DIR, "olist_orders_dataset.csv"))
items       = pd.read_csv(os.path.join(DATA_DIR, "olist_order_items_dataset.csv"))
payments    = pd.read_csv(os.path.join(DATA_DIR, "olist_order_payments_dataset.csv"))
reviews     = pd.read_csv(os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv"))
customers   = pd.read_csv(os.path.join(DATA_DIR, "olist_customers_dataset.csv"))
products    = pd.read_csv(os.path.join(DATA_DIR, "olist_products_dataset.csv"))
sellers     = pd.read_csv(os.path.join(DATA_DIR, "olist_sellers_dataset.csv"))
geo         = pd.read_csv(os.path.join(DATA_DIR, "olist_geolocation_dataset.csv"))
cat_trans   = pd.read_csv(os.path.join(DATA_DIR, "product_category_name_translation.csv"))

datasets = {
    "orders": orders, "items": items, "payments": payments,
    "reviews": reviews, "customers": customers, "products": products,
    "sellers": sellers, "geolocation": geo, "category_translation": cat_trans,
}

for name, df in datasets.items():
    print(f"\n--- {name} ({df.shape[0]:,} rows × {df.shape[1]} cols) ---")
    print(f"Columns: {list(df.columns)}")
    print(df.dtypes.to_string())

# =============================================================================
# 2. JOIN TABLES INTO ORDER-LEVEL DATASET
# =============================================================================
print("\n" + "=" * 70)
print("2. JOINING TABLES")
print("=" * 70)

# Convert date columns
date_cols = [
    'order_purchase_timestamp', 'order_approved_at',
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col])

# Aggregate items per order
items_agg = items.groupby('order_id').agg(
    total_items=('order_item_id', 'count'),
    total_price=('price', 'sum'),
    total_freight=('freight_value', 'sum'),
).reset_index()

# Aggregate payments per order
payments_agg = payments.groupby('order_id').agg(
    payment_value=('payment_value', 'sum'),
    payment_installments=('payment_installments', 'max'),
).reset_index()

# Take the FIRST review per order (some orders have duplicates)
reviews_dedup = reviews.sort_values('review_creation_date').drop_duplicates(subset='order_id', keep='last')
reviews_clean = reviews_dedup[['order_id', 'review_score', 'review_comment_message']].copy()

# Main join
df = (
    orders
    .merge(items_agg, on='order_id', how='inner')
    .merge(payments_agg, on='order_id', how='inner')
    .merge(reviews_clean, on='order_id', how='inner')
)

# Also join items to products and sellers for quality analysis
items_detail = (
    items
    .merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
    .merge(cat_trans, on='product_category_name', how='left')
    .merge(sellers[['seller_id', 'seller_city', 'seller_state']], on='seller_id', how='left')
)

# Item-level dataset with reviews
items_reviews = (
    items_detail
    .merge(reviews_clean, on='order_id', how='inner')
)

print(f"Order-level dataset: {df.shape[0]:,} rows × {df.shape[1]} cols")
print(f"Item-level detail dataset: {items_reviews.shape[0]:,} rows")

# =============================================================================
# 3. FEATURE ENGINEERING
# =============================================================================
print("\n" + "=" * 70)
print("3. FEATURE ENGINEERING")
print("=" * 70)

# --- Delivery framing ---
df['delivery_duration'] = (
    df['order_delivered_customer_date'] - df['order_purchase_timestamp']
).dt.total_seconds() / 86400  # days

df['estimated_duration'] = (
    df['order_estimated_delivery_date'] - df['order_purchase_timestamp']
).dt.total_seconds() / 86400

df['delivery_delay'] = df['delivery_duration'] - df['estimated_duration']
df['timeliness_status'] = df['delivery_delay'].apply(
    lambda x: 'Late' if x > 0 else 'On-Time' if pd.notnull(x) else 'Unknown'
)

# --- Quality framing ---
df['review_category'] = pd.cut(
    df['review_score'], bins=[0, 2, 3, 5], labels=['Bad (1-2)', 'Neutral (3)', 'Good (4-5)']
)

# --- Shipping cost framing ---
df['freight_ratio'] = df['total_freight'] / df['total_price']
df['freight_ratio'] = df['freight_ratio'].clip(upper=5)  # cap outliers
df['shipping_category'] = pd.cut(
    df['freight_ratio'],
    bins=[-0.001, 0.15, 0.30, 100],
    labels=['Low (<15%)', 'Medium (15-30%)', 'High (>30%)']
)

# Month column for trends
df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')

# Filter to delivered orders for delivery analysis
delivered = df[df['order_status'] == 'delivered'].dropna(subset=['delivery_duration']).copy()

print(f"Delivered orders for analysis: {delivered.shape[0]:,}")
print(f"Late deliveries: {(delivered['timeliness_status'] == 'Late').sum():,} "
      f"({(delivered['timeliness_status'] == 'Late').mean():.1%})")
print(f"Mean delivery duration: {delivered['delivery_duration'].mean():.1f} days")
print(f"Mean freight ratio: {delivered['freight_ratio'].mean():.2%}")
print(f"\nReview score distribution:")
print(df['review_score'].value_counts().sort_index())

# =============================================================================
# 4. HYPOTHESIS 1 — DELIVERY DELAY ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("4. HYPOTHESIS 1 — DELIVERY DELAY")
print("=" * 70)

# 4a. Review score by timeliness
time_review = delivered.groupby('timeliness_status')['review_score'].agg(['mean', 'median', 'count'])
time_review.columns = ['Mean Score', 'Median Score', 'Order Count']
print("\n--- Table 1: Review Score by Delivery Timeliness ---")
print(time_review.to_string())

# 4b. Late delivery rate by month
monthly_late = (
    delivered.groupby('order_month')
    .agg(
        total_orders=('order_id', 'count'),
        late_orders=('timeliness_status', lambda x: (x == 'Late').sum()),
    )
)
monthly_late['late_rate'] = monthly_late['late_orders'] / monthly_late['total_orders']
print("\n--- Monthly Late Delivery Rate (last 6 months) ---")
print(monthly_late.tail(6).to_string())

# 4c. Distribution of delay days for late orders
late_orders = delivered[delivered['timeliness_status'] == 'Late']
print(f"\nLate delivery delay stats (days):")
print(late_orders['delivery_delay'].describe())

# =============================================================================
# 5. HYPOTHESIS 2 — SELLER / PRODUCT QUALITY
# =============================================================================
print("\n" + "=" * 70)
print("5. HYPOTHESIS 2 — SELLER / PRODUCT QUALITY")
print("=" * 70)

# 5a. Review score distribution
review_dist = df['review_score'].value_counts(normalize=True).sort_index() * 100
print("\n--- Review Score Distribution (%) ---")
print(review_dist.round(1).to_string())

# 5b. Top 10 sellers by number of bad reviews (score <= 2)
bad_reviews = items_reviews[items_reviews['review_score'] <= 2]
seller_bad = (
    bad_reviews
    .groupby('seller_id')
    .agg(bad_review_count=('review_score', 'count'), avg_score=('review_score', 'mean'))
    .sort_values('bad_review_count', ascending=False)
    .head(10)
)
print("\n--- Table 2: Top 10 Sellers with Most Bad Reviews (score 1-2) ---")
print(seller_bad.to_string())

# 5c. Categories with worst average scores
cat_scores = (
    items_reviews
    .groupby('product_category_name_english')
    .agg(avg_score=('review_score', 'mean'), count=('review_score', 'count'))
    .query('count >= 50')
    .sort_values('avg_score')
    .head(10)
)
print("\n--- Bottom 10 Product Categories by Avg Review Score (min 50 reviews) ---")
print(cat_scores.to_string())

# 5d. Concentration — what % of sellers account for 50% of bad reviews?
seller_bad_all = (
    bad_reviews.groupby('seller_id')['review_score'].count()
    .sort_values(ascending=False)
    .reset_index()
)
seller_bad_all.columns = ['seller_id', 'bad_count']
seller_bad_all['cumulative_pct'] = seller_bad_all['bad_count'].cumsum() / seller_bad_all['bad_count'].sum()
sellers_for_50pct = (seller_bad_all['cumulative_pct'] <= 0.50).sum()
total_sellers_with_bad = len(seller_bad_all)
print(f"\n{sellers_for_50pct} sellers ({sellers_for_50pct/total_sellers_with_bad:.1%}) "
      f"account for 50% of all bad reviews")

# =============================================================================
# 6. HYPOTHESIS 3 — SHIPPING COST
# =============================================================================
print("\n" + "=" * 70)
print("6. HYPOTHESIS 3 — SHIPPING COST")
print("=" * 70)

# 6a. Freight ratio stats
print("\n--- Freight Ratio Statistics ---")
print(delivered['freight_ratio'].describe().to_string())

# 6b. Review score by shipping category
ship_review = delivered.groupby('shipping_category')['review_score'].agg(['mean', 'median', 'count'])
ship_review.columns = ['Mean Score', 'Median Score', 'Order Count']
print("\n--- Table 3: Review Score by Shipping Cost Category ---")
print(ship_review.to_string())

# 6c. Avg freight ratio by review score
freight_by_review = delivered.groupby('review_score')['freight_ratio'].mean()
print("\n--- Freight Ratio by Review Score ---")
print(freight_by_review.to_string())

# =============================================================================
# 7. COMPARATIVE SUMMARY — WHICH FRAMING HAS STRONGEST EVIDENCE?
# =============================================================================
print("\n" + "=" * 70)
print("7. COMPARATIVE SUMMARY")
print("=" * 70)

# Correlation of each factor with review score (Spearman — appropriate for ordinal review scores)
from scipy import stats
corr_delivery = delivered[['delivery_duration', 'review_score']].dropna()
rs_delivery, ps_delivery = stats.spearmanr(corr_delivery['delivery_duration'], corr_delivery['review_score'])

corr_freight = delivered[['freight_ratio', 'review_score']].dropna()
rs_freight, ps_freight = stats.spearmanr(corr_freight['freight_ratio'], corr_freight['review_score'])

# Late vs On-time score gap
late_score = delivered[delivered['timeliness_status'] == 'Late']['review_score'].mean()
ontime_score = delivered[delivered['timeliness_status'] == 'On-Time']['review_score'].mean()
score_gap = ontime_score - late_score

# Shipping category score gap
low_ship = delivered[delivered['shipping_category'] == 'Low (<15%)']['review_score'].mean()
high_ship = delivered[delivered['shipping_category'] == 'High (>30%)']['review_score'].mean()
ship_gap = low_ship - high_ship

print(f"\n--- Spearman Rank Correlation (appropriate for ordinal review scores) ---")
print(f"Delivery duration vs review score: rs = {rs_delivery:.3f} (p = {ps_delivery:.2e})")
print(f"Freight ratio vs review score:     rs = {rs_freight:.3f} (p = {ps_freight:.2e})")
print(f"\nOn-Time vs Late review gap:       {score_gap:.2f} points")
print(f"Low vs High shipping review gap:  {ship_gap:.2f} points")
print(f"\nLate delivery rate: {(delivered['timeliness_status'] == 'Late').mean():.1%}")
print(f"Bad review rate (score 1-2): {(df['review_score'] <= 2).mean():.1%}")

# =============================================================================
# 8. GENERATE VISUALIZATIONS
# =============================================================================
print("\n" + "=" * 70)
print("8. GENERATING VISUALIZATIONS")
print("=" * 70)

# --- Figure 1: BASELINE — Delivery Duration vs Review Score (Boxplot) ---
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60']
bp = delivered.boxplot(
    column='delivery_duration', by='review_score', ax=ax,
    patch_artist=True, showfliers=False,
    boxprops=dict(linewidth=1.5),
    medianprops=dict(color='black', linewidth=2)
)
for patch, color in zip(ax.patches if hasattr(ax, 'patches') else [], colors):
    patch.set_facecolor(color)
ax.set_xlabel('Review Score', fontsize=12)
ax.set_ylabel('Delivery Duration (days)', fontsize=12)
ax.set_title('Baseline: Delivery Duration by Review Score', fontsize=14, fontweight='bold')
fig.suptitle('')
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig1_baseline_delivery_vs_review.png"), bbox_inches='tight')
print("Saved: fig1_baseline_delivery_vs_review.png")
plt.close()

# --- Figure 2: On-Time vs Late — Review Score Comparison ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: bar chart
time_means = delivered.groupby('timeliness_status')['review_score'].mean()
bars = axes[0].bar(time_means.index, time_means.values, color=['#27ae60', '#e74c3c'], edgecolor='white', width=0.5)
for bar, val in zip(bars, time_means.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.2f}', ha='center', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Mean Review Score', fontsize=12)
axes[0].set_title('Mean Review Score:\nOn-Time vs Late', fontsize=13, fontweight='bold')
axes[0].set_ylim(0, 5.5)

# Right: monthly late rate trend
monthly = monthly_late.copy()
monthly.index = monthly.index.astype(str)
axes[1].plot(range(len(monthly)), monthly['late_rate'] * 100, marker='o', color='#e74c3c', linewidth=2)
axes[1].fill_between(range(len(monthly)), monthly['late_rate'] * 100, alpha=0.15, color='#e74c3c')
axes[1].set_xticks(range(0, len(monthly), 3))
axes[1].set_xticklabels(monthly.index[::3], rotation=45, ha='right', fontsize=8)
axes[1].set_ylabel('Late Delivery Rate (%)', fontsize=12)
axes[1].set_title('Monthly Late Delivery Rate Trend', fontsize=13, fontweight='bold')
axes[1].yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig2_delivery_comparison.png"), bbox_inches='tight')
print("Saved: fig2_delivery_comparison.png")
plt.close()

# --- Figure 3: Review Score Distribution ---
fig, ax = plt.subplots(figsize=(8, 5))
score_counts = df['review_score'].value_counts().sort_index()
colors_review = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60']
bars = ax.bar(score_counts.index, score_counts.values, color=colors_review, edgecolor='white', width=0.6)
for bar, val in zip(bars, score_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f'{val:,}', ha='center', fontsize=10)
ax.set_xlabel('Review Score', fontsize=12)
ax.set_ylabel('Number of Orders', fontsize=12)
ax.set_title('Distribution of Review Scores', fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig3_review_distribution.png"), bbox_inches='tight')
print("Saved: fig3_review_distribution.png")
plt.close()

# --- Figure 4: Freight Ratio Distribution + Ship Category vs Score ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(delivered['freight_ratio'].dropna(), bins=50, color='#3498db', edgecolor='white', alpha=0.85)
axes[0].axvline(delivered['freight_ratio'].median(), color='#e74c3c', linestyle='--', linewidth=2, label=f"Median: {delivered['freight_ratio'].median():.2f}")
axes[0].set_xlabel('Freight Ratio (freight / price)', fontsize=12)
axes[0].set_ylabel('Frequency', fontsize=12)
axes[0].set_title('Freight Ratio Distribution', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].set_xlim(0, 1.5)

ship_cat_means = delivered.groupby('shipping_category')['review_score'].mean()
bars = axes[1].bar(ship_cat_means.index, ship_cat_means.values, color=['#27ae60', '#f1c40f', '#e74c3c'], edgecolor='white', width=0.5)
for bar, val in zip(bars, ship_cat_means.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.2f}', ha='center', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Mean Review Score', fontsize=12)
axes[1].set_title('Mean Review Score by\nShipping Cost Category', fontsize=13, fontweight='bold')
axes[1].set_ylim(0, 5.5)

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig4_shipping_analysis.png"), bbox_inches='tight')
print("Saved: fig4_shipping_analysis.png")
plt.close()

print("\n✅ All visualizations saved successfully.")
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
