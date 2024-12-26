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
        df = pd.read_csv('day.csv')
        df_hour = pd.read_csv('hour.csv')
        df['dteday'] = pd.to_datetime(df['dteday'])
        df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
        return df, df_hour
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

data, data_hour = load_data()
if data.empty or data_hour.empty:
    st.stop()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", options=["2011", "2012"])
selected_season = st.sidebar.multiselect("Pilih Musim", options=[1, 2, 3, 4], default=[1, 2, 3, 4], format_func=lambda x: {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}[x])
selected_weather = st.sidebar.multiselect("Pilih Cuaca", options=[1, 2, 3, 4], default=[1, 2, 3, 4], format_func=lambda x: {1: "Clear", 2: "Mist", 3: "Light Snow/Rain", 4: "Heavy Rain/Snow"}[x])

filtered_data = data[(data['yr'] == int(selected_year) - 2011) & (data['season'].isin(selected_season)) & (data['weathersit'].isin(selected_weather))]
data_hour_filtered = data_hour[(data_hour['yr'] == int(selected_year) - 2011) & (data_hour['season'].isin(selected_season)) & (data_hour['weathersit'].isin(selected_weather))]

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
st.write("Grafik ini menunjukkan bagaimana pengguna casual dan registered menggunakan sepeda pada setiap hari dalam seminggu.")

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
st.write("Grafik ini memberikan wawasan tentang perbedaan penyewaan sepeda berdasarkan musim dan hari kerja/non-kerja.")

# --- TREND ANALYSIS ---
st.header("Tren Penyewaan Bulanan")
st.write("Analisis ini menunjukkan tren jumlah penyewaan rata-rata berdasarkan bulan.")
st.write("Grafik ini membantu mengidentifikasi tren musiman dari jumlah penyewaan sepeda berdasarkan rata-rata per bulan.")

monthly_trend = filtered_data.groupby(filtered_data['dteday'].dt.to_period('M'))['cnt'].mean().reset_index()
monthly_trend['dteday'] = monthly_trend['dteday'].dt.to_timestamp()

fig3 = px.line(
    monthly_trend, x='dteday', y='cnt',
    labels={'dteday': 'Bulan', 'cnt': 'Rata-rata Penyewaan'},
    title="Tren Penyewaan Bulanan"
)
st.plotly_chart(fig3)
st.write("Grafik ini menampilkan tren penyewaan sepeda bulanan untuk memahami pola musiman.")

# --- PERTANYAAN BISNIS 1: Pola Penggunaan Berdasarkan Jam ---
st.header("Pola Penggunaan Sepeda Berdasarkan Jam")
st.write("Analisis pola penggunaan sepeda dalam satu hari dibagi menjadi morning, afternoon, evening, dan night.")

def categorize_hour(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

# Tambahkan kategori waktu pada data hourly
data_hour_filtered['Time_Period'] = data_hour_filtered['hr'].apply(categorize_hour)
time_period_usage = data_hour_filtered.groupby('Time_Period')['cnt'].mean().reset_index()

fig4 = px.bar(
    time_period_usage, x='Time_Period', y='cnt', color='Time_Period',
    labels={'cnt': 'Rata-rata Penyewaan', 'Time_Period': 'Waktu'},
    title="Rata-rata Penyewaan Sepeda Berdasarkan Waktu"
)
st.plotly_chart(fig4)
st.write("Grafik ini menunjukkan rata-rata penggunaan sepeda dalam berbagai periode waktu dalam sehari.")

# --- PERTANYAAN BISNIS 2: Pengaruh Faktor Cuaca ---
st.header("Pengaruh Faktor Cuaca terhadap Penyewaan Sepeda")
st.write("Analisis ini menunjukkan hubungan antara faktor cuaca seperti suhu, kelembapan, dan kecepatan angin dengan jumlah penyewaan sepeda.")

# Visualisasi pengaruh suhu
fig5 = px.scatter(
    filtered_data, x='temp', y='cnt', color='cnt',
    labels={'temp': 'Suhu (Normalized)', 'cnt': 'Jumlah Penyewaan'},
    title="Hubungan Suhu dan Jumlah Penyewaan"
)
st.plotly_chart(fig5)
st.write("Grafik ini menunjukkan bagaimana suhu memengaruhi jumlah penyewaan sepeda.")

# Visualisasi pengaruh kelembapan
fig6 = px.scatter(
    filtered_data, x='hum', y='cnt', color='cnt',
    labels={'hum': 'Kelembapan (Normalized)', 'cnt': 'Jumlah Penyewaan'},
    title="Hubungan Kelembapan dan Jumlah Penyewaan"
)
st.plotly_chart(fig6)
st.write("Grafik ini menunjukkan bagaimana kelembapan memengaruhi jumlah penyewaan sepeda.")

# --- PENUTUP ---
st.write("Dashboard dibuat oleh Muhammad Edya Rosadi | Dataset: Bike Sharing")
