# Decision Memo

## Analisis Review Pelanggan untuk Mendukung Keputusan Bisnis pada Kategori Beauty and Personal Care

Nama Mahasiswa: [Isi Nama Anda]  
NIM: [Isi NIM Anda]  
Mata Kuliah: Analisis Keputusan Bisnis  
Tahun Akademik: 2025/2026

## Konteks Data

Analisis ini menggunakan sampel 24,964 review dari kategori `Beauty_and_Personal_Care` pada dataset Amazon Reviews 2023. Karena file kategori asli berukuran sangat besar, analisis dilakukan pada streaming sample yang diambil langsung dari sumber resmi dataset. Sampel ini cukup untuk menggambarkan pola utama review pelanggan, namun hasilnya tetap perlu dibaca sebagai indikasi berbasis sampel, bukan sensus penuh.

## KPI Keputusan

KPI utama yang dipilih adalah **average rating** karena metrik ini paling ringkas untuk menggambarkan kesehatan persepsi kategori secara umum. Pada sampel, rata-rata rating tercatat **4.200**.

Dua KPI turunan yang digunakan adalah:

1. **Persentase review buruk (1-2 bintang)** sebesar **11.22%**, untuk menangkap konsentrasi keluhan berat.
2. **Average helpful votes pada review buruk** sebesar **1.50**, untuk melihat apakah keluhan negatif cukup relevan dan dianggap berguna oleh pembeli lain.

Guardrail KPI yang digunakan adalah **verified purchase share** sebesar **59.66%**. Guardrail ini penting agar rekomendasi lebih bertumpu pada pengalaman pembelian yang lebih kredibel.

## Temuan Utama Voice of Customer

Tiga tema keluhan yang paling dominan pada review 1-2 bintang adalah:

1. **Product does not work as expected**
2. **Packaging, leakage, or damaged items**
3. **Skin irritation or side effects**

Pola review buruk menunjukkan bahwa keluhan pelanggan banyak berkaitan dengan kegagalan fungsi produk, mutu pengemasan, serta reaksi pengguna terhadap formula, bau, atau efek samping. Dibanding review tinggi, review rendah juga cenderung lebih problem-focused dan lebih eksplisit menyebut konsekuensi negatif setelah penggunaan.

## Hasil Predictive Modeling

Model klasifikasi sederhana menggunakan Logistic Regression dengan fitur teks review (`TF-IDF`), panjang review, dan helpful votes untuk membedakan review baik (`4-5`) dan review buruk (`1-2`). Hasil pada data uji menunjukkan:

- Accuracy: **0.9353**
- Precision kelas review baik: **0.9869**
- Recall kelas review baik: **0.9386**
- F1-score kelas review baik: **0.9621**
- ROC-AUC: **0.9781**

Secara praktis, model cukup membantu untuk triase awal review. Tim bisnis dapat memanfaatkannya untuk menandai review yang perlu segera dievaluasi tanpa harus membaca seluruh review secara manual.

## Risiko Bisnis Mis-klasifikasi

Risiko paling penting adalah ketika **review buruk diprediksi sebagai review baik**. Kondisi ini dapat membuat keluhan serius tidak cepat terdeteksi, sehingga memperlambat respons terhadap masalah kualitas, memperburuk rating produk, menaikkan tingkat retur, dan berpotensi merusak reputasi merek. Karena itu, model ini sebaiknya diposisikan sebagai alat prioritisasi, bukan pengganti evaluasi manual.

## Rekomendasi Keputusan Bisnis

1. Fokuskan audit kualitas pada produk yang paling sering memicu tema keluhan efektivitas produk dan packaging issue.
2. Bentuk dashboard mingguan yang memasangkan average rating dengan persentase review 1-2 bintang sebagai early warning.
3. Gunakan model klasifikasi untuk memprioritaskan review yang perlu ditindaklanjuti oleh tim quality assurance dan customer service.
4. Terapkan guardrail minimum jumlah review sebelum mengambil keputusan besar di level produk individual.
