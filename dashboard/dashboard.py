import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Informasi Proyek
st.sidebar.header("Proyek Analisis Data")
st.sidebar.markdown("""
- **Nama:** Bertnardo Mario Uskono
- **Email:** bertnardouskono@gmail.com
- **ID Dicoding:** MC190D5Y1643
""")

# Load data
data_path = "./data/day.csv"
try:
    day_df = pd.read_csv(data_path)
    # Konversi dan validasi kolom tanggal
    day_df = day_df.rename(columns={'dteday': 'tanggal_raw'})
    day_df['tanggal'] = pd.to_datetime(day_df['tanggal_raw'], errors='coerce')
    day_df = day_df.dropna(subset=['tanggal']).drop(columns=['tanggal_raw'])
except Exception as e:
    st.error(f"Gagal memuat data: {str(e)}")
    st.stop()

# Konversi kolom dan kategori
try:
    # Rename kolom
    column_mapping = {
        'yr': 'tahun',
        'mnth': 'bulan',
        'weekday': 'hari_kerja',
        'weathersit': 'kondisi_cuaca',
        'temp': 'suhu',
        'atemp': 'suhu_terasa',
        'hum': 'kelembaban',
        'windspeed': 'kecepatan_angin',
        'cnt': 'total_peminjam',
        'season': 'musim'
    }
    day_df = day_df.rename(columns=column_mapping)
    
    # Konversi kategori
    day_df['hari_kerja'] = day_df['hari_kerja'].replace({
        0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu',
        4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
    })
    
    day_df['kondisi_cuaca'] = day_df['kondisi_cuaca'].replace({
        1: 'Cerah', 2: 'Berkabut', 3: 'Hujan Ringan', 4: 'Hujan Lebat'
    })
    
    day_df['musim'] = day_df['musim'].replace({
        1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'
    })
except KeyError as e:
    st.error(f"Kolom tidak ditemukan: {str(e)}")
    st.stop()

# Filter Interaktif
st.sidebar.header("Filter Data")
try:
    min_date = day_df['tanggal'].min().date()
    max_date = day_df['tanggal'].max().date()
except AttributeError:
    st.sidebar.error("Format tanggal tidak valid!")
    st.stop()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_musim = st.sidebar.multiselect(
    'Musim',
    options=day_df['musim'].unique(),
    default=day_df['musim'].unique()
)

selected_cuaca = st.sidebar.multiselect(
    'Kondisi Cuaca',
    options=day_df['kondisi_cuaca'].unique(),
    default=day_df['kondisi_cuaca'].unique()
)

# Aplikasi filter
try:
    start_date, end_date = date_range
    filtered_df = day_df[
        (day_df['tanggal'].dt.date >= start_date) &
        (day_df['tanggal'].dt.date <= end_date) &
        (day_df['musim'].isin(selected_musim)) &
        (day_df['kondisi_cuaca'].isin(selected_cuaca))
    ]
except Exception as e:
    st.error(f"Error dalam filtering data: {str(e)}")
    st.stop()

# Visualisasi
st.title("Dashboard Analisis Bike Sharing")

if not filtered_df.empty:
    # Visualisasi 1: Total Peminjam per Hari
    st.subheader("Trend Harian Peminjaman Sepeda")
    fig1, ax1 = plt.subplots(figsize=(12,6))
    sns.lineplot(
        data=filtered_df,
        x='tanggal',
        y='total_peminjam',
        hue='musim',
        ax=ax1
    )
    plt.xticks(rotation=45)
    st.pyplot(fig1)
    
    # Visualisasi 2: Distribusi Cuaca
    st.subheader("Distribusi Kondisi Cuaca")
    fig2, ax2 = plt.subplots(figsize=(8,4))
    filtered_df['kondisi_cuaca'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2)
    st.pyplot(fig2)
    
    # Analisis Clustering
    st.subheader("Analisis Cluster Peminjaman")
    
    try:
        # Binning parameter
        bins_config = {
            'suhu': ['Rendah', 'Sedang', 'Tinggi'],
            'kelembaban': ['Kering', 'Normal', 'Lembab'],
            'kecepatan_angin': ['Tenang', 'Berangin', 'Kencang']
        }
        
        for col, labels in bins_config.items():
            filtered_df[f'{col}_category'] = pd.cut(
                filtered_df[col],
                bins=3,
                labels=labels
            )
        
        # Persiapan data clustering
        cluster_features = pd.get_dummies(filtered_df[[
            'suhu_category',
            'kelembaban_category',
            'kecepatan_angin_category',
            'musim',
            'hari_kerja'
        ]])
        
        # Clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        filtered_df['cluster'] = kmeans.fit_predict(cluster_features)
        
        # Visualisasi cluster
        st.subheader("Distribusi Cluster")
        fig3, ax3 = plt.subplots(figsize=(10,6))
        sns.scatterplot(
            data=filtered_df,
            x='suhu',
            y='total_peminjam',
            hue='cluster',
            palette='viridis',
            size='kecepatan_angin',
            ax=ax3
        )
        st.pyplot(fig3)
        
        # Analisis cluster
        st.subheader("Karakteristik Cluster")
        cluster_stats = filtered_df.groupby('cluster').agg({
            'suhu': 'mean',
            'kelembaban': 'mean',
            'kecepatan_angin': 'mean',
            'total_peminjam': 'mean',
            'musim': lambda x: x.mode()[0],
            'hari_kerja': lambda x: x.mode()[0]
        }).rename(columns={
            'suhu': 'Suhu Rata-rata',
            'kelembaban': 'Kelembaban Rata-rata',
            'kecepatan_angin': 'Kecepatan Angin Rata-rata',
            'total_peminjam': 'Rata-rata Peminjaman'
        })
        st.dataframe(cluster_stats.style.format("{:.2f}"))
        
    except Exception as e:
        st.error(f"Error dalam analisis cluster: {str(e)}")
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

# Tampilkan data mentah
st.subheader("Data Mentah")
st.dataframe(filtered_df, height=300)

# Footer
st.markdown("---")
st.markdown("**Catatan:** Dashboard ini dibuat untuk memenuhi proyek analisis data Dicoding")
