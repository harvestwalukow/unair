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
    df = pd.read_csv(f)
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['trip_month'] = df['started_at'].dt.to_period('M')
    df['trip_hour'] = df['started_at'].dt.hour
    df['day_of_week'] = df['started_at'].dt.dayofweek
    df['is_weekday'] = df['day_of_week'] < 5
    df['is_peak_hour'] = ((df['trip_hour'] >= 7) & (df['trip_hour'] <= 9)) | \
                        ((df['trip_hour'] >= 16) & (df['trip_hour'] <= 18))
    df['duration_min'] = (pd.to_datetime(df['ended_at']) - df['started_at']).dt.total_seconds() / 60
    
    agg_cols = ['trip_month', 'trip_hour', 'is_weekday', 'is_peak_hour', 'rideable_type', 'member_casual', 'duration_min', 'start_station_name']
    all_data.append(df[agg_cols])

df_all = pd.concat(all_data, ignore_index=True)

# --- 1. Tren Bulanan ---
monthly_stats = df_all.groupby('trip_month').agg(
    total_trips=('trip_month', 'count'),
    member_trips=('member_casual', lambda x: (x == 'member').sum())
).reset_index()

monthly_stats['member_share'] = (monthly_stats['member_trips'] / monthly_stats['total_trips']) * 100
monthly_stats['trip_month_str'] = monthly_stats['trip_month'].astype(str)

plt.figure(figsize=(12, 6))
ax1 = sns.lineplot(data=monthly_stats, x='trip_month_str', y='total_trips', marker='o', label='Total Perjalanan', color='blue')
plt.xticks(rotation=45)
plt.ylabel('Total Perjalanan')
plt.title('Tren Perjalanan Bulanan dan Proporsi Member')

ax2 = ax1.twinx()
sns.lineplot(data=monthly_stats, x='trip_month_str', y='member_share', marker='s', label='Proporsi Member (%)', color='green', ax=ax2)
plt.ylabel('Proporsi Member (%)')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.savefig('monthly_trend_id.png')
plt.close()

# --- 2. Pola Jam Sibuk ---
hourly_stats = df_all.groupby(['trip_hour', 'is_weekday']).size().reset_index(name='trip_count')
hourly_stats['day_type'] = hourly_stats['is_weekday'].map({True: 'Hari Kerja (Weekday)', False: 'Akhir Pekan (Weekend)'})

plt.figure(figsize=(12, 6))
sns.lineplot(data=hourly_stats, x='trip_hour', y='trip_count', hue='day_type', marker='o')
plt.xticks(range(0, 24))
plt.title('Pola Perjalanan Per Jam: Hari Kerja vs Akhir Pekan')
plt.xlabel('Jam')
plt.ylabel('Total Perjalanan')
plt.legend(title='Tipe Hari')
plt.tight_layout()
plt.savefig('hourly_pattern_id.png')
plt.close()
