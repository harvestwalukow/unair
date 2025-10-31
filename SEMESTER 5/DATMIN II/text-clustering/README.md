# Text Clustering Analysis - adaKami Reviews

Analisis clustering pada data review aplikasi adaKami menggunakan TF-IDF dan K-Means.

## Fitur Analisis

1. **Preprocessing**

   - Text cleaning (lowercase, remove URLs, special characters, numbers)
   - Indonesian stopwords removal
   - Tokenization

2. **WordCloud**

   - Visualisasi kata-kata yang paling sering muncul
   - Bar chart untuk top 20 kata

3. **Clustering dengan Sentence-Transformers**
   - Sentence-Transformers embeddings (all-mpnet-base-v2)
   - 768-dimensional semantic embeddings
   - K-Means clustering
   - Elbow method untuk menentukan optimal k
4. **Visualisasi**

   - Static 2D visualization dengan PCA
   - Interactive 2D visualization dengan Plotly
   - Interactive 3D visualization dengan Plotly
   - Cluster statistics (rating, review count, review length)

5. **Silhouette Score**
   - Overall silhouette score
   - Per-cluster silhouette scores
   - Silhouette plot visualization

## Requirements

Install semua dependencies yang diperlukan:

```bash
pip install -r requirements.txt
```

## Cara Menggunakan

1. Pastikan file `adaKami-reviews.csv` ada di folder yang sama

2. Jalankan Jupyter Notebook:

```bash
jupyter notebook text_clustering_analysis.ipynb
```

3. Jalankan semua cells secara berurutan (Cell > Run All)

## Output Files

Setelah analisis selesai, akan menghasilkan file-file berikut:

### Visualisasi (PNG)

- `wordcloud.png` - WordCloud dari semua review
- `top_words.png` - Bar chart 20 kata teratas
- `elbow_silhouette.png` - Elbow method dan silhouette scores
- `cluster_statistics.png` - Statistik per cluster
- `clustering_pca_2d.png` - Visualisasi clustering 2D
- `silhouette_plot.png` - Silhouette plot per cluster

### Interactive Visualizations (HTML)

- `clustering_interactive_2d.html` - Interactive 2D clustering plot
- `clustering_interactive_3d.html` - Interactive 3D clustering plot

### Data Export (CSV)

- `clustering_results.csv` - Hasil clustering lengkap dengan scores
- `cluster_keywords.csv` - Top keywords untuk setiap cluster

## Struktur Notebook

1. **Import Libraries dan Load Data** - Setup dan loading dataset
2. **Text Preprocessing** - Cleaning dan preprocessing text
3. **WordCloud Visualization** - Visualisasi kata-kata
4. **Sentence-Transformers Embeddings** - Generate semantic embeddings
5. **Finding Optimal Number of Clusters** - Elbow method
6. **K-Means Clustering** - Clustering dengan optimal k
7. **Cluster Analysis & Top Terms** - Analisis hasil clustering
8. **Dimensionality Reduction & Visualization** - PCA dan visualisasi
9. **Silhouette Score Analysis** - Evaluasi kualitas clustering
10. **Summary and Export Results** - Summary dan export hasil

## Interpretasi Hasil

### Silhouette Score

- **> 0.7**: Excellent clustering quality
- **0.5 - 0.7**: Good clustering quality
- **0.3 - 0.5**: Moderate clustering quality
- **< 0.3**: Poor clustering quality

### Cluster Analysis

Setiap cluster akan menunjukkan:

- Top keywords yang merepresentasikan cluster
- Jumlah reviews dalam cluster
- Average rating
- Sample reviews

## Keuntungan Sentence-Transformers

Menggunakan **Sentence-Transformers** (all-mpnet-base-v2) dibanding TF-IDF:

1. **Semantic Understanding** - Menangkap makna kontekstual, bukan hanya frekuensi kata
2. **Multilingual Support** - Bekerja baik untuk Bahasa Indonesia tanpa preprocessing ekstensif
3. **Similar Meaning Detection** - Review dengan kata berbeda tapi makna sama akan dikelompokkan
4. **Dense Representations** - 768-dimensional dense vectors vs sparse TF-IDF vectors
5. **Better Clustering** - Biasanya menghasilkan silhouette score lebih tinggi

## Tips

- **Model download**: Pada run pertama, model all-mpnet-base-v2 (~420MB) akan didownload otomatis
- **Processing time**: Embedding generation memakan waktu beberapa menit tergantung ukuran dataset dan hardware
- **GPU acceleration**: Jika tersedia GPU, akan otomatis digunakan untuk mempercepat embedding generation
- Visualisasi interactive HTML dapat dibuka di browser untuk eksplorasi lebih detail
- Anda dapat mengubah `n_clusters` secara manual jika ingin mencoba jumlah cluster berbeda

## Author

Data Mining II Analysis - UNAIR
