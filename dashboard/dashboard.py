import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Judul Utama Dashboard
st.title("Bike Sharing Dataset")

# Informasi Proyek di Sidebar
st.sidebar.header("Proyek Analisis Data : Bike Sharing Dataset")
st.sidebar.markdown("""
- **Nama:** Bertnardo Mario Uskono
- **Email:** bertnardouskono@gmail.com
- **ID Dicoding:** MC190D5Y1643
""")

# Load data
data_path = "./data/day.csv"
day_df = pd.read_csv(data_path)

# Cleaning data
day_df["tanggal"] = pd.to_datetime(day_df["dteday"])
day_df.rename(columns={
    'dteday': 'tanggal',
    'yr': 'tahun',
    'mnth': 'bulan',
    'weekday': 'hari_kerja',
    'weathersit': 'kondisi_cuaca',
    'temp': 'suhu',
    'atemp': 'suhu_terasa',
    'hum': 'kelembaban',
    'windspeed': 'kecepatan_angin',
    'cnt': 'total_peminjam'
}, inplace=True)

day_df["hari_kerja"] = day_df["hari_kerja"].replace({
    0: 'Minggu',
    1: 'Senin',
    2: 'Selasa',
    3: 'Rabu',
    4: 'Kamis',
    5: 'Jumat',
    6: 'Sabtu'
})

day_df["kondisi_cuaca"] = day_df["kondisi_cuaca"].replace({
    1: 'Cerah',
    2: 'Berkabut',
    3: 'Hujan Ringan',
    4: 'Hujan Lebat'
})

# Judul Dashboard
st.header("Dashboard Analisis Data Bike Sharing")

# Pertanyaan 1: Total Peminjam Sepeda Berdasarkan Hari Kerja
st.subheader("Total Peminjam Sepeda Berdasarkan Hari Kerja")
fig_hari_kerja, ax_hari_kerja = plt.subplots(figsize=(10, 5))
sns.barplot(x="hari_kerja", y="total_peminjam", data=day_df, estimator=sum, ax=ax_hari_kerja)
st.pyplot(fig_hari_kerja)

# Pertanyaan 2: Total Peminjam Sepeda Berdasarkan Kondisi Cuaca
st.subheader("Total Peminjam Sepeda Berdasarkan Kondisi Cuaca")
fig_kondisi_cuaca, ax_kondisi_cuaca = plt.subplots(figsize=(10, 5))
sns.barplot(x="kondisi_cuaca", y="total_peminjam", data=day_df, estimator=sum, ax=ax_kondisi_cuaca)
st.pyplot(fig_kondisi_cuaca)

# Analisis Lanjutan (Opsional): Correlation Matrix
st.subheader("Correlation Matrix")
correlation_matrix = day_df.corr(numeric_only=True)
fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax_corr)
st.pyplot(fig_corr)

# Kesimpulan Korelasi Matriks
st.subheader("Kesimpulan Korelasi Matriks")
st.write("""
- Suhu (temp dan atemp) memiliki korelasi positif yang kuat dengan jumlah peminjam (total_peminjam). Ini menunjukkan bahwa semakin tinggi suhu, semakin banyak orang yang meminjam sepeda.
- Tahun (tahun) juga memiliki korelasi positif dengan jumlah peminjam, menunjukkan tren peningkatan penggunaan sepeda dari tahun ke tahun.
- Kelembaban (kelembaban) memiliki korelasi negatif dengan jumlah peminjam, menunjukkan bahwa kelembaban yang lebih tinggi cenderung mengurangi jumlah peminjam.
""")

# Kesimpulan Umum
st.subheader("Kesimpulan Umum")
st.write("- Hari Jumat memiliki jumlah peminjam sepeda tertinggi dalam seminggu.")
st.write("- Kondisi cuaca cerah sangat mendukung aktivitas peminjaman sepeda, dengan jumlah peminjam tertinggi dibandingkan kondisi cuaca lainnya.")
