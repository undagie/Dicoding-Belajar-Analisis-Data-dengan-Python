import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Bike Sharing Analysis",
    page_icon="🚲",
    layout="wide"
)

# --- JUDUL ---
st.title("Bike Sharing Data Analysis Dashboard")
st.write("Analisis tren penyewaan sepeda berdasarkan faktor musiman, pengguna, dan jumlah penyewaan.")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dashboard/main_data.csv')
        df['dteday'] = pd.to_datetime(df['dteday'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data()
if data.empty:
    st.stop()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", options=["2011", "2012"])
selected_season = st.sidebar.multiselect("Pilih Musim", options=[1, 2, 3, 4], default=[1, 2, 3, 4], format_func=lambda x: {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}[x])

filtered_data = data[(data['yr'] == int(selected_year) - 2011) & (data['season'].isin(selected_season))]

# --- RFM-LIKE ANALYSIS ---
st.header("Segmentasi Pengguna: Registered vs Casual")
st.write("Analisis ini membandingkan rata-rata jumlah penyewaan pengguna **registered** dan **casual** berdasarkan frekuensi dan monetisasi.")
st.write("Grafik ini menunjukkan perbandingan rata-rata penyewaan pengguna terdaftar (registered) dan tidak terdaftar (casual) untuk setiap hari dalam seminggu.")

weekly_user_stats = filtered_data.groupby('weekday').agg({
    'casual': 'mean',
    'registered': 'mean',
    'cnt': 'sum'
}).reset_index()
weekly_user_stats['weekday'] = weekly_user_stats['weekday'].map({0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'})

# Visualisasi dengan Plotly
fig1 = px.bar(
    weekly_user_stats.melt(id_vars='weekday', value_vars=['casual', 'registered'], var_name='User Type', value_name='Average Usage'),
    x='weekday', y='Average Usage', color='User Type', barmode='group',
    title="Rata-rata Penyewaan Pengguna per Hari"
)
st.plotly_chart(fig1)

# --- ANALISIS POLA MUSIMAN ---
st.header("Pola Musiman Penyewaan Sepeda")
st.write("Analisis ini menunjukkan tren jumlah penyewaan sepeda berdasarkan musim dan jenis hari (kerja/libur).")
st.write("Grafik ini membantu mengidentifikasi pola penyewaan berdasarkan musim (Spring, Summer, Fall, Winter) dan apakah hari tersebut adalah hari kerja atau bukan.")

season_usage = filtered_data.groupby(['season', 'workingday'])['cnt'].mean().reset_index()
season_usage['season'] = season_usage['season'].map({1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"})
season_usage['workingday'] = season_usage['workingday'].map({0: "Non-Working Day", 1: "Working Day"})

fig2 = px.bar(
    season_usage, x='season', y='cnt', color='workingday',
    labels={'workingday': 'Hari Kerja', 'cnt': 'Rata-rata Penyewaan'},
    title="Rata-rata Penyewaan Sepeda per Musim dan Hari"
)
st.plotly_chart(fig2)

# --- MANUAL CLUSTERING ---
st.header("Manual Clustering: Penggunaan Sepeda")
st.write("Pengelompokan jumlah penyewaan sepeda ke dalam kategori **Low Usage**, **Medium Usage**, dan **High Usage**.")
st.write("Grafik ini mengelompokkan jumlah penyewaan sepeda ke dalam tiga kategori berdasarkan banyaknya penyewaan, sehingga mempermudah analisis pola penggunaan.")

# Fungsi Manual Clustering
def cluster_usage(cnt):
    if cnt < 2000:
        return 'Low Usage'
    elif 2000 <= cnt < 4000:
        return 'Medium Usage'
    else:
        return 'High Usage'

filtered_data['Usage_Cluster'] = filtered_data['cnt'].apply(cluster_usage)
cluster_counts = filtered_data['Usage_Cluster'].value_counts().reset_index()
cluster_counts.columns = ['Cluster', 'Count']

fig3 = px.bar(
    cluster_counts, x='Cluster', y='Count', color='Cluster',
    title="Distribusi Clustering Penyewaan Sepeda"
)
st.plotly_chart(fig3)

# --- BINNING JUMLAH PENYEWAAN ---
st.header("Binning Jumlah Penyewaan Sepeda")
st.write("Data penyewaan dibagi ke dalam interval untuk melihat distribusi penggunaan sepeda.")
st.write("Grafik ini menunjukkan distribusi jumlah penyewaan sepeda dengan membagi data ke dalam interval seperti Very Low, Low, Medium, dan High.")

# Binning yang lebih berarti berdasarkan data aktual
max_cnt = filtered_data['cnt'].max()
bins = [0, 1000, 3000, 5000, max_cnt]
labels = ['Very Low', 'Low', 'Medium', 'High']
filtered_data['Binned_Usage'] = pd.cut(filtered_data['cnt'], bins=bins, labels=labels)
binned_counts = filtered_data['Binned_Usage'].value_counts().reset_index()
binned_counts.columns = ['Interval', 'Count']

fig4 = px.bar(
    binned_counts, x='Interval', y='Count', color='Interval',
    title="Distribusi Binning Penyewaan Sepeda"
)
st.plotly_chart(fig4)

# --- TREND ANALYSIS ---
st.header("Tren Penyewaan Bulanan")
st.write("Analisis ini menunjukkan tren jumlah penyewaan rata-rata berdasarkan bulan.")
st.write("Grafik ini membantu mengidentifikasi tren musiman dari jumlah penyewaan sepeda berdasarkan rata-rata per bulan.")

monthly_trend = filtered_data.groupby(filtered_data['dteday'].dt.to_period('M'))['cnt'].mean().reset_index()
monthly_trend['dteday'] = monthly_trend['dteday'].dt.to_timestamp()

fig5 = px.line(
    monthly_trend, x='dteday', y='cnt',
    labels={'dteday': 'Bulan', 'cnt': 'Rata-rata Penyewaan'},
    title="Tren Penyewaan Bulanan"
)
st.plotly_chart(fig5)

# --- FOOTER ---
st.write("Dashboard dibuat oleh Muhammad Edya Rosadi | Dataset: Bike Sharing")
