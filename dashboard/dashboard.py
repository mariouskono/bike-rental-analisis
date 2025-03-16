import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Informasi Proyek
st.sidebar.header("Proyek Analisis Data")
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

# Konversi nilai kategori
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

day_df["musim"] = day_df["season"].replace({
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Fall'
})

# Filter Interaktif di Sidebar
st.sidebar.header("Filter Data")
min_date = day_df['tanggal'].min().date()
max_date = day_df['tanggal'].max().date()

start_date = st.sidebar.date_input(
    "Pilih Tanggal Awal",
    min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "Pilih Tanggal Akhir",
    max_date,
    min_value=min_date,
    max_value=max_date
)

selected_musim = st.sidebar.multiselect(
    'Pilih Musim',
    options=day_df['musim'].unique(),
    default=day_df['musim'].unique()
)

selected_cuaca = st.sidebar.multiselect(
    'Pilih Kondisi Cuaca',
    options=day_df['kondisi_cuaca'].unique(),
    default=day_df['kondisi_cuaca'].unique()
)

# Filter data berdasarkan input pengguna
filtered_df = day_df[
    (day_df['tanggal'].dt.date >= start_date) &
    (day_df['tanggal'].dt.date <= end_date) &
    (day_df['musim'].isin(selected_musim)) &
    (day_df['kondisi_cuaca'].isin(selected_cuaca))
]

# Judul Dashboard
st.title("Dashboard Analisis Data Bike Sharing")

# Visualisasi 1: Total Peminjam per Hari Kerja
st.subheader("Total Peminjam Sepeda Berdasarkan Hari Kerja")
if not filtered_df.empty:
    fig_hari_kerja, ax_hari_kerja = plt.subplots(figsize=(10, 5))
    sns.barplot(x="hari_kerja", y="total_peminjam", data=filtered_df, estimator=sum, ax=ax_hari_kerja)
    st.pyplot(fig_hari_kerja)
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

# Visualisasi 2: Total Peminjam per Kondisi Cuaca
st.subheader("Total Peminjam Sepeda Berdasarkan Kondisi Cuaca")
if not filtered_df.empty:
    fig_kondisi_cuaca, ax_kondisi_cuaca = plt.subplots(figsize=(10, 5))
    sns.barplot(x="kondisi_cuaca", y="total_peminjam", data=filtered_df, estimator=sum, ax=ax_kondisi_cuaca)
    st.pyplot(fig_kondisi_cuaca)
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

# Analisis Clustering
st.subheader("Analisis Clustering Penggunaan Sepeda")
st.markdown("""
### Pengelompokan Berdasarkan Kondisi Lingkungan dan Waktu
Metode: Binning parameter cuaca + K-Means Clustering
""")

if not filtered_df.empty:
    try:
        # Binning parameter numerik
        filtered_df['suhu_kategori'] = pd.cut(filtered_df['suhu'], bins=3, 
                                            labels=['Rendah', 'Sedang', 'Tinggi'])
        filtered_df['kelembaban_kategori'] = pd.cut(filtered_df['kelembaban'], bins=3,
                                                  labels=['Rendah', 'Sedang', 'Tinggi'])
        filtered_df['kecepatan_angin_kategori'] = pd.cut(filtered_df['kecepatan_angin'], bins=3,
                                                       labels=['Rendah', 'Sedang', 'Tinggi'])

        # Persiapan data untuk clustering
        cluster_data = pd.get_dummies(filtered_df[[
            'suhu_kategori', 'kelembaban_kategori', 'kecepatan_angin_kategori',
            'musim', 'bulan'
        ]])

        # Clustering dengan K-Means
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(cluster_data)
        filtered_df['cluster'] = clusters

        # Visualisasi cluster
        fig_cluster, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='cluster', y='total_peminjam', data=filtered_df)
        plt.title('Distribusi Jumlah Peminjam per Cluster')
        st.pyplot(fig_cluster)

        # Analisis cluster
        st.subheader("Karakteristik Cluster")
        cluster_summary = filtered_df.groupby('cluster').agg({
            'suhu': 'mean',
            'kelembaban': 'mean',
            'kecepatan_angin': 'mean',
            'musim': lambda x: x.mode()[0],
            'bulan': lambda x: x.mode()[0],
            'total_peminjam': 'mean'
        }).reset_index()
        st.dataframe(cluster_summary)

        # Interpretasi
        st.subheader("Interpretasi Cluster")
        st.markdown("""
        - **Cluster 0**: Kondisi dengan parameter lingkungan sedang dan penggunaan sepeda menengah
        - **Cluster 1**: Kondisi optimal dengan penggunaan sepeda tertinggi
        - **Cluster 2**: Kondisi kurang optimal dengan penggunaan sepeda terendah
        """)
        
    except Exception as e:
        st.error(f"Error dalam pemrosesan clustering: {str(e)}")
else:
    st.warning("Tidak ada data yang sesuai untuk analisis clustering.")

# Kesimpulan Umum
st.subheader("Kesimpulan Umum")
st.write("- Hari kerja pertengahan minggu (Rabu-Jumat) menunjukkan penggunaan sepeda tertinggi")
st.write("- Kondisi cuaca cerah meningkatkan minat penggunaan sepeda hingga 2x lipat")
st.write("- Cluster analisis menunjukkan kombinasi suhu sedang + kelembaban rendah menghasilkan penggunaan maksimal")
