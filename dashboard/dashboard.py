import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Judul Utama Dashboard
st.title("Bike Sharing Dataset")

# Informasi Proyek di Sidebar
st.sidebar.header("Proyek Analisis Data : Bike Sharing Dataset")
st.sidebar.markdown("""
- **Nama:** Bertnardo Mario Uskono
- **Email:** bertnardouskono@gmail.com
- **ID Dicoding:** MC190D5Y1643
""")

# Tombol untuk Analisis Notebook di Sidebar
st.sidebar.header("Opsi Analisis Tambahan")
show_notebook = st.sidebar.checkbox("Tampilkan Analisis Notebook")

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
    
    # Pastikan kolom numerik bertipe float
    numeric_cols = ['suhu', 'suhu_terasa', 'kelembaban', 'kecepatan_angin', 'total_peminjam']
    day_df[numeric_cols] = day_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    day_df = day_df.dropna(subset=numeric_cols)
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
        # Binning parameter numerik
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
        # Statistik numerik
        cluster_stats = filtered_df.groupby('cluster').agg({
            'suhu': 'mean',
            'kelembaban': 'mean',
            'kecepatan_angin': 'mean',
            'total_peminjam': 'mean'
        }).rename(columns={
            'suhu': 'Suhu Rata-rata',
            'kelembaban': 'Kelembaban Rata-rata',
            'kecepatan_angin': 'Kecepatan Angin Rata-rata',
            'total_peminjam': 'Rata-rata Peminjaman'
        })
        st.dataframe(
            cluster_stats.style.format({
                'Suhu Rata-rata': '{:.2f}',
                'Kelembaban Rata-rata': '{:.2f}',
                'Kecepatan Angin Rata-rata': '{:.2f}',
                'Rata-rata Peminjaman': '{:.2f}'
            })
        )
        
        # Statistik kategori
        cluster_categories = filtered_df.groupby('cluster').agg({
            'musim': lambda x: x.mode()[0],
            'hari_kerja': lambda x: x.mode()[0]
        }).rename(columns={
            'musim': 'Musim Terbanyak',
            'hari_kerja': 'Hari Terbanyak'
        })
        st.write("Kategori Dominan per Cluster:")
        st.dataframe(cluster_categories)
        
    except Exception as e:
        st.error(f"Error dalam analisis cluster: {str(e)}")
else:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")

# Tampilkan Analisis Notebook jika dipilih
if show_notebook:
    st.title("Analisis Tambahan dari Notebook")
    
    # Pertanyaan 1: Total Peminjam Berdasarkan Hari Kerja
    st.subheader("Total Peminjam Sepeda Berdasarkan Hari Kerja")
    fig4, ax4 = plt.subplots(figsize=(10,5))
    sns.barplot(x="hari_kerja", y="total_peminjam", data=day_df, estimator=sum, ax=ax4)
    plt.xticks(rotation=45)
    st.pyplot(fig4)
    
    # Pertanyaan 2: Total Peminjam Berdasarkan Cuaca
    st.subheader("Total Peminjam Sepeda Berdasarkan Kondisi Cuaca")
    fig5, ax5 = plt.subplots(figsize=(10,5))
    sns.barplot(x="kondisi_cuaca", y="total_peminjam", data=day_df, estimator=sum, ax=ax5)
    st.pyplot(fig5)
    
    # Analisis Korelasi
    st.subheader("Correlation Matrix")
    corr_matrix = day_df.corr(numeric_only=True)
    fig6, ax6 = plt.subplots(figsize=(12,8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax6)
    st.pyplot(fig6)
    
    # Kesimpulan Korelasi
    st.subheader("Kesimpulan Korelasi Matriks")
    st.markdown("""
    - **Suhu (temp & atemp):** Korelasi positif kuat dengan peminjaman, menunjukkan semakin hangat cuaca, semakin tinggi peminjaman.
    - **Tahun (yr):** Tren peningkatan peminjaman setiap tahun.
    - **Kelembaban (hum):** Korelasi negatif, kelembaban tinggi mengurangi peminjaman.
    """)
    
    # Kesimpulan Umum
    st.subheader("Kesimpulan Umum")
    st.markdown("""
    - **Hari dengan Peminjaman Tertinggi:** Jumat.
    - **Cuaca Optimal:** Cerah mendominasi peminjaman tertinggi.
    """)

# Tampilkan data mentah
st.subheader("Data Mentah")
st.dataframe(filtered_df, height=300)

# Footer
st.markdown("---")
st.markdown("**Catatan:** Dashboard ini dibuat untuk memenuhi proyek analisis data Dicoding")
