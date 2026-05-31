import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for charts
sns.set_theme(style="whitegrid")

# 1. Load data
file_pattern = "*-divvy-tripdata.csv"
files = glob.glob(file_pattern)
print(f"Loading {len(files)} files...")

all_data = []
for f in files:
    print(f"Processing {f}...")
    df = pd.read_csv(f)
    
    # Feature Engineering
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])
    
    df['trip_month'] = df['started_at'].dt.to_period('M')
    df['trip_hour'] = df['started_at'].dt.hour
    df['day_of_week'] = df['started_at'].dt.dayofweek
    df['is_weekday'] = df['day_of_week'] < 5
    
    # Peak hour: 07–09 and 16–18
    df['is_peak_hour'] = ((df['trip_hour'] >= 7) & (df['trip_hour'] <= 9)) | \
                        ((df['trip_hour'] >= 16) & (df['trip_hour'] <= 18))
    
    # Trip duration in minutes
    df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
    
    # Keep only necessary columns for aggregation to save memory
    agg_cols = ['trip_month', 'trip_hour', 'is_weekday', 'is_peak_hour', 'rideable_type', 'member_casual', 'duration_min', 'start_station_name']
    all_data.append(df[agg_cols])

# Combine all data
print("Combining dataframes...")
df_all = pd.concat(all_data, ignore_index=True)
del all_data # Free memory

# --- 1. Monthly Trend ---
print("Generating Monthly Trend Chart...")
monthly_stats = df_all.groupby('trip_month').agg(
    total_trips=('trip_month', 'count'),
    member_trips=('member_casual', lambda x: (x == 'member').sum()),
    electric_trips=('rideable_type', lambda x: (x == 'electric_bike').sum())
).reset_index()

monthly_stats['member_share'] = monthly_stats['member_trips'] / monthly_stats['total_trips']
monthly_stats['electric_share'] = monthly_stats['electric_trips'] / monthly_stats['total_trips']
monthly_stats['trip_month_str'] = monthly_stats['trip_month'].astype(str)

plt.figure(figsize=(12, 6))
ax1 = sns.lineplot(data=monthly_stats, x='trip_month_str', y='total_trips', marker='o', label='Total Trips', color='blue')
plt.xticks(rotation=45)
plt.ylabel('Total Trips')
plt.title('Monthly Trip Trends and Member Share')

ax2 = ax1.twinx()
sns.lineplot(data=monthly_stats, x='trip_month_str', y='member_share', marker='s', label='Member Share', color='green', ax=ax2)
plt.ylabel('Member Share (%)')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.savefig('monthly_trend.png')
plt.close()

# --- 2. Hourly Pattern ---
print("Generating Hourly Pattern Chart...")
hourly_stats = df_all.groupby(['trip_hour', 'is_weekday']).size().reset_index(name='trip_count')
hourly_stats['day_type'] = hourly_stats['is_weekday'].map({True: 'Weekday', False: 'Weekend'})

plt.figure(figsize=(12, 6))
sns.lineplot(data=hourly_stats, x='trip_hour', y='trip_count', hue='day_type', marker='o')
plt.xticks(range(0, 24))
plt.title('Hourly Trip Patterns: Weekday vs Weekend')
plt.xlabel('Hour of Day')
plt.ylabel('Total Trips')
plt.tight_layout()
plt.savefig('hourly_pattern.png')
plt.close()

# --- 3. Station Table ---
print("Generating Station Table...")
top_stations = df_all['start_station_name'].value_counts().head(10).reset_index()
top_stations.columns = ['Station Name', 'Trip Count']
top_stations.to_csv('top_stations.csv', index=False)
print("Top 10 Stations:")
print(top_stations)

# --- KPI Calculations ---
print("Calculating KPIs...")

# Main KPI: Total Trips (Average per month)
avg_monthly_trips = monthly_stats['total_trips'].mean()

# Supporting KPI 1: Member Share
avg_member_share = monthly_stats['member_share'].mean()

# Supporting KPI 2: Peak Intensity (Peak trips vs Normal hours on weekdays)
weekday_df = df_all[df_all['is_weekday']]
peak_trips = weekday_df[weekday_df['is_peak_hour']].shape[0] / (6 * weekday_df['trip_month'].nunique()) # 6 peak hours
non_peak_trips = weekday_df[~weekday_df['is_peak_hour']].shape[0] / (18 * weekday_df['trip_month'].nunique()) # 18 non-peak hours
peak_intensity = peak_trips / non_peak_trips

# Supporting KPI 3: Station Concentration (Top 10 stations share)
total_trips = df_all.shape[0]
top_10_share = top_stations['Trip Count'].sum() / total_trips

# Guardrail: Median Trip Duration
median_duration = df_all['duration_min'].median()

print(f"\n--- KPI Summary ---")
print(f"Avg Monthly Trips: {avg_monthly_trips:,.0f}")
print(f"Avg Member Share: {avg_member_share:.2%}")
print(f"Peak Intensity: {peak_intensity:.2f}")
print(f"Top 10 Station Concentration: {top_10_share:.2%}")
print(f"Median Trip Duration: {median_duration:.2f} min")

# Save results for memo
with open('kpi_results.txt', 'w') as f:
    f.write(f"Avg Monthly Trips: {avg_monthly_trips:,.0f}\n")
    f.write(f"Avg Member Share: {avg_member_share:.2%}\n")
    f.write(f"Peak Intensity: {peak_intensity:.2f}\n")
    f.write(f"Top 10 Station Concentration: {top_10_share:.2%}\n")
    f.write(f"Median Trip Duration: {median_duration:.2f} min\n")
