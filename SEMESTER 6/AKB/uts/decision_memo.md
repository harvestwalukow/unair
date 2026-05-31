# Decision Memo

## Analisis Review Pelanggan untuk Mendukung Keputusan Bisnis pada Kategori Beauty and Personal Care

Nama Mahasiswa: [Isi Nama Anda]  
NIM: [Isi NIM Anda]  
Mata Kuliah: Analisis Keputusan Bisnis  
Tahun Akademik: 2025/2026

## Konteks Data

Analisis ini menggunakan **25% sampel data** dari file lokal `Beauty_and_Personal_Care.jsonl` yang berasal dari dataset resmi Amazon Reviews 2023. Pengambilan sampel dilakukan dengan **proportionate stratified deterministic sampling** berdasarkan kombinasi **bulan review** dan **rating**, sehingga distribusi temporal dan distribusi sentimen tetap terjaga serta sampel dapat direplikasi. Total data yang dibaca dari file adalah **23,911,390 review**, sedangkan total review yang masuk ke sampel analisis adalah **5,976,417 review**.

## KPI Keputusan

KPI utama yang dipilih adalah **average rating**. Pada sampel analisis, rata-rata rating tercatat **4.111**.

Dua KPI turunan yang digunakan adalah:

1. **Persentase review buruk (1-2 bintang)** sebesar **17.22%**.
2. **Average helpful votes pada review buruk** sebesar **1.44**.

Guardrail KPI yang digunakan adalah **verified purchase share** sebesar **91.10%** agar rekomendasi tetap bertumpu pada pengalaman pembelian yang lebih kredibel.

Berdasarkan hasil tersebut, target KPI ke depan yang direkomendasikan adalah:

1. menaikkan **average rating** ke minimal **4.20**,
2. menurunkan **persentase review buruk** ke bawah **15%**,
3. menjaga **average helpful votes pada review buruk** tetap di sekitar atau di bawah **1.44**, dan
4. mempertahankan **verified purchase share** minimal **90%**.

## Temuan Utama Voice of Customer

Tiga tema keluhan yang paling dominan pada review 1-2 bintang adalah:

1. **Product does not work as expected**
2. **Packaging, leakage, or damaged items**
3. **Skin irritation or side effects**

Pola review buruk menunjukkan bahwa keluhan pelanggan banyak berkaitan dengan ketidakefektifan produk, kualitas kemasan saat produk diterima, serta reaksi negatif setelah penggunaan.

## Hasil Predictive Modeling

Model klasifikasi sederhana menggunakan **Multinomial Naive Bayes** dengan fitur teks review (`HashingVectorizer`) untuk membedakan review baik (`4-5`) dan review buruk (`1-2`). Hasil pada data uji menunjukkan:

- Accuracy: **0.9492**
- Precision kelas review baik: **0.9538**
- Recall kelas review baik: **0.9853**
- F1-score kelas review baik: **0.9693**
- ROC-AUC: **0.9859**

Model ini cukup membantu untuk triase awal review dalam volume besar, terutama untuk membantu tim bisnis, QA, dan customer service memprioritaskan review yang perlu ditindaklanjuti lebih cepat. Di sisi lain, model lebih kuat dalam mengenali review baik dibanding review buruk, sehingga hasil prediksi tetap perlu dibaca secara hati-hati untuk kebutuhan eskalasi keluhan.

## Risiko Bisnis Mis-klasifikasi

Risiko utama muncul ketika **review buruk diprediksi sebagai review baik**. Pada hasil evaluasi, masih terdapat **172.675** review buruk pada data uji yang diprediksi sebagai review baik. Jika ini terjadi dalam praktik, keluhan serius dapat terlewat, respons bisnis menjadi terlambat, dan masalah kualitas bisa berkembang menjadi penurunan rating, peningkatan retur, dan kerusakan reputasi.

## Rekomendasi Keputusan Bisnis

1. Prioritaskan audit kualitas pada produk dengan keluhan efektivitas paling tinggi.
2. Perkuat quality control kemasan dan proses distribusi untuk menekan keluhan kebocoran atau kerusakan.
3. Gunakan dashboard yang memasangkan average rating dengan persentase review buruk sebagai early warning.
4. Gunakan model klasifikasi sebagai alat prioritas, bukan pengganti evaluasi manual penuh.
