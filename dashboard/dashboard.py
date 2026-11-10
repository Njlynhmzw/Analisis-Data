from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style='whitegrid')
BASE = Path(__file__).parent
SEASON_ORDER = ['Spring', 'Summer', 'Fall', 'Winter']
WEATHER_ORDER = ['Clear', 'Mist/Cloudy', 'Light Snow/Rain']
DAY_COLORS = {'Hari Kerja': '#1F77B4', 'Libur/Akhir Pekan': '#FF7F0E'}

st.set_page_config(page_title='Bike Sharing Dashboard', page_icon='🚲', layout='wide')


@st.cache_data
def load_data():
    day = pd.read_csv(BASE / 'day_clean.csv', parse_dates=['dteday'])
    hour = pd.read_csv(BASE / 'main_data.csv', parse_dates=['dteday'])
    return day, hour


day_df, hour_df = load_data()

# ---------- Sidebar ----------
st.sidebar.title('🚲 Filter')
min_d, max_d = day_df['dteday'].min().date(), day_df['dteday'].max().date()
date_range = st.sidebar.date_input('Rentang tanggal', value=(min_d, max_d), min_value=min_d, max_value=max_d)
seasons = st.sidebar.multiselect('Musim', SEASON_ORDER, default=SEASON_ORDER)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    st.sidebar.info('Pilih tanggal akhir untuk melengkapi rentang.')
    st.stop()

d = day_df[day_df['dteday'].between(start, end) & day_df['season_label'].isin(seasons)]
h = hour_df[hour_df['dteday'].between(start, end) & hour_df['season_label'].isin(seasons)]
if d.empty or h.empty:
    st.warning('Tidak ada data untuk filter yang dipilih.')
    st.stop()

# ---------- Header & KPI ----------
st.title('Bike Sharing Dashboard')
st.caption('Capital Bikeshare, Washington D.C. (2011-2012). Data bersih hasil analisis pada notebook.')

c1, c2, c3, c4 = st.columns(4)
c1.metric('Total penyewaan', f"{d['cnt'].sum():,.0f}")
c2.metric('Rata-rata per hari', f"{d['cnt'].mean():,.0f}")
c3.metric('Rata-rata per jam', f"{h['cnt'].mean():,.1f}")
c4.metric('Porsi pengguna registered', f"{d['registered'].sum() / d['cnt'].sum() * 100:.1f}%")

# ---------- Pertanyaan 1 ----------
st.subheader('Pertanyaan 1: Jam puncak penyewaan, hari kerja vs libur')
pattern = h.groupby(['hr', 'day_type'])['cnt'].mean().unstack()
fig, ax = plt.subplots(figsize=(11, 4.8))
for col in pattern.columns:
    s = pattern[col]
    ax.plot(s.index, s.values, marker='o', linewidth=2.2, label=col, color=DAY_COLORS[col])
    pk = s.idxmax()
    ax.annotate(f'Puncak {pk:02d}.00 ({s.max():.0f})', xy=(pk, s.max()), xytext=(pk, s.max() + 0.12 * pattern.max().max()),
                ha='center', color=DAY_COLORS[col], fontweight='bold', arrowprops=dict(arrowstyle='->', color=DAY_COLORS[col]))
ax.set_xticks(range(24))
ax.set_xlabel('Jam (0-23)'); ax.set_ylabel('Rata-rata penyewaan per jam')
ax.set_ylim(0, pattern.max().max() * 1.35)
ax.legend(frameon=False); sns.despine()
st.pyplot(fig)

peaks = {c: (pattern[c].idxmax(), pattern[c].max()) for c in pattern.columns}
txt = ' | '.join(f'**{c}**: puncak pukul {k:02d}.00 ({v:.0f} sepeda/jam)' for c, (k, v) in peaks.items())
st.markdown(txt)
st.info('Hari kerja memiliki dua puncak komuter (pagi dan sore); hari libur satu puncak landai di siang hari. '
        'Jadwalkan redistribusi sepeda sebelum jam sibuk.')

# ---------- Pertanyaan 2 ----------
st.subheader('Pertanyaan 2: Pengaruh cuaca dan musim terhadap penyewaan harian')
col_a, col_b = st.columns(2)

with col_a:
    w = d.groupby('weather_label')['cnt'].mean().reindex(WEATHER_ORDER).dropna()
    fig, ax = plt.subplots(figsize=(6, 4.6))
    cols = ['#2CA02C' if x == 'Clear' else '#B0B0B0' for x in w.index]
    bars = ax.bar(w.index, w.values, color=cols)
    base = w.get('Clear', np.nan)
    for r, (name, v) in zip(bars, w.items()):
        lbl = f'{v:,.0f}' if name == 'Clear' or np.isnan(base) else f'{v:,.0f}\n({(v / base - 1) * 100:+.0f}%)'
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + w.max() * 0.015, lbl, ha='center')
    ax.set_ylim(0, w.max() * 1.18); ax.set_ylabel('Rata-rata penyewaan harian'); ax.set_xlabel('')
    ax.set_title('Rata-rata harian per kondisi cuaca (% vs Clear)', loc='left', fontsize=11)
    sns.despine(); st.pyplot(fig)

with col_b:
    s = d.groupby('season_label')['cnt'].mean().reindex(SEASON_ORDER).dropna()
    fig, ax = plt.subplots(figsize=(6, 4.6))
    cols = ['#1F77B4' if v == s.max() else ('#D62728' if v == s.min() else '#B0B0B0') for v in s.values]
    bars = ax.bar(s.index, s.values, color=cols)
    for r, v in zip(bars, s.values):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + s.max() * 0.015, f'{v:,.0f}', ha='center')
    ax.set_ylim(0, s.max() * 1.18); ax.set_ylabel(''); ax.set_xlabel('')
    ax.set_title('Rata-rata harian per musim', loc='left', fontsize=11)
    sns.despine(); st.pyplot(fig)

st.info('Hujan/salju ringan menurunkan penyewaan tajam dibanding cuaca cerah; Fall musim tertinggi dan Spring terendah '
        '(pada seluruh rentang data). Sesuaikan armada dan promosi dengan prakiraan cuaca dan musim.')

# ---------- Analisis lanjutan ----------
st.subheader('Analisis Lanjutan: Binning Suhu dan Pengelompokan Waktu')
col_c, col_d = st.columns(2)

with col_c:
    dd = d.copy()
    dd['temp_group'] = pd.cut(dd['temp_c'], bins=[-np.inf, 10, 20, 30, np.inf],
                              labels=['Dingin (<10°C)', 'Sejuk (10-20°C)', 'Hangat (20-30°C)', 'Panas (>30°C)'])
    t = dd.groupby('temp_group', observed=True)['cnt'].mean()
    fig, ax = plt.subplots(figsize=(6, 4.6))
    cols = ['#1F77B4' if v == t.max() else '#B0B0B0' for v in t.values]
    ax.bar(t.index.astype(str), t.values, color=cols)
    ax.set_ylabel('Rata-rata penyewaan harian'); ax.set_title('Penyewaan menurut kelompok suhu', loc='left', fontsize=11)
    ax.tick_params(axis='x', rotation=20); sns.despine(); st.pyplot(fig)

with col_d:
    hh = h.copy()
    hh['time_group'] = pd.cut(hh['hr'], bins=[-1, 5, 9, 15, 19, 23],
                              labels=['Dini Hari (00-05)', 'Pagi Sibuk (06-09)', 'Siang (10-15)', 'Sore Sibuk (16-19)', 'Malam (20-23)'])
    ts = hh.groupby(['time_group', 'day_type'], observed=True)['cnt'].mean().unstack()
    fig, ax = plt.subplots(figsize=(6, 4.6))
    ts.plot(kind='bar', ax=ax, color=[DAY_COLORS[c] for c in ts.columns], width=0.8)
    ax.set_xlabel(''); ax.set_ylabel('Rata-rata per jam'); ax.legend(title='', frameon=False)
    ax.set_title('Penyewaan menurut kelompok waktu', loc='left', fontsize=11)
    ax.tick_params(axis='x', rotation=25); sns.despine(); st.pyplot(fig)

st.caption('Sumber data: Fanaee-T & Gama (2013), Capital Bikeshare Bike Sharing Dataset.')
