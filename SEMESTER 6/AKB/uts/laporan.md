# DAFTAR ISI

1. BAB 1 PENDAHULUAN
   1.1 Latar Belakang Permasalahan
   1.2 Tujuan Analisis
2. BAB 2 URAIAN
   2.1 Penetapan Key Performance Indicator (KPI)
   2.2 Analisis Voice of Customer dari Teks Review
   2.3 Translasi Insight ke Bahasa Bisnis
   2.4 Predictive Modeling Sederhana
3. BAB 3 KESIMPULAN
   3.1 Ringkasan Hasil Analisis dan Temuan Utama
   3.2 Rekomendasi Keputusan Bisnis Berdasarkan Hasil Analisis dan Model Prediktif
4. DAFTAR PUSTAKA
5. LAMPIRAN / APPENDIX

# BAB 1 PENDAHULUAN

## 1.1 Latar Belakang Permasalahan

Review pelanggan merupakan salah satu sumber data yang sangat penting dalam lingkungan bisnis digital, khususnya pada platform e-commerce. Melalui review, pelanggan tidak hanya memberikan penilaian numerik dalam bentuk rating, tetapi juga menyampaikan pengalaman penggunaan, tingkat kepuasan, keluhan, serta harapan mereka terhadap suatu produk. Bagi perusahaan, informasi tersebut sangat bernilai karena dapat digunakan untuk memahami persepsi pasar, mengidentifikasi masalah utama yang dirasakan konsumen, serta menyusun keputusan bisnis yang lebih berbasis bukti.

Pada kategori *Beauty and Personal Care*, keberadaan review pelanggan menjadi semakin penting karena produk dalam kategori ini berhubungan langsung dengan tubuh, kulit, rambut, kebersihan, dan penampilan. Produk semacam ini umumnya memiliki tingkat sensitivitas yang tinggi terhadap persepsi konsumen. Apabila produk tidak bekerja sesuai harapan, menimbulkan iritasi, memiliki aroma yang tidak disukai, atau diterima dalam kondisi rusak, pelanggan cenderung memberikan review negatif yang cukup detail. Sebaliknya, apabila produk dianggap efektif dan memuaskan, review positif dapat memperkuat kepercayaan calon pembeli lain. Dengan demikian, review pada kategori ini bukan hanya sekadar umpan balik pelanggan, tetapi juga cerminan kualitas produk dan pengalaman pelanggan secara menyeluruh.

Walaupun demikian, jumlah review pada kategori *Beauty and Personal Care* sangat besar sehingga sulit dianalisis secara manual. Apabila perusahaan hanya berfokus pada rata-rata rating, maka terdapat risiko bahwa masalah penting pelanggan tidak terdeteksi karena tertutupi oleh skor agregat yang relatif tinggi. Oleh karena itu, diperlukan pendekatan analisis yang menggabungkan indikator kuantitatif dan analisis teks review agar kondisi kategori dapat dipahami secara lebih komprehensif.

Dalam penelitian ini, analisis dilakukan menggunakan data review kategori `Beauty_and_Personal_Care` dari dataset Amazon Reviews 2023. Karena ukuran populasi sangat besar, penelitian menggunakan **25% sampel data** yang diambil dengan metode **proportionate stratified deterministic sampling** berdasarkan kombinasi **bulan review** dan **rating**. Pendekatan ini dipilih agar distribusi temporal dan distribusi sentimen tetap terjaga, sekaligus membuat sampel dapat direplikasi. Dari total **23.911.390 review** yang tersedia, diperoleh **5.976.417 review** sebagai sampel analisis.

Analisis ini penting karena tidak berhenti pada deskripsi statistik, tetapi juga bertujuan menerjemahkan data review menjadi insight dan rekomendasi keputusan bisnis. Melalui penetapan KPI, identifikasi tema keluhan utama, perbandingan pola review baik dan buruk, serta model prediktif sederhana, perusahaan dapat memperoleh gambaran yang lebih jelas mengenai kondisi kategori produk dan area perbaikan yang paling prioritas.

## 1.2 Tujuan Analisis

Tujuan analisis ini adalah sebagai berikut:

1. Menganalisis review pelanggan pada kategori `Beauty_and_Personal_Care` sebagai dasar untuk memahami kondisi umum kategori produk.
2. Menetapkan KPI utama, KPI turunan, dan guardrail KPI yang relevan untuk menilai kesehatan kategori berdasarkan data review pelanggan.
3. Mengidentifikasi tema-tema utama dalam review pelanggan serta membandingkan pola antara review baik dan review buruk.
4. Menerjemahkan hasil analisis data dan teks review ke dalam insight bisnis yang dapat digunakan sebagai dasar rekomendasi keputusan.
5. Membangun dan mengevaluasi model klasifikasi sederhana untuk membedakan review baik dan review buruk, serta menjelaskan manfaat dan risiko bisnis dari penggunaannya.

# BAB 2 URAIAN

## A. Penetapan Key Performance Indicator (KPI)

### 1. KPI Utama

KPI utama yang dipilih dalam analisis ini adalah **rata-rata rating (average rating)**. Indikator ini dipilih karena mampu memberikan gambaran umum mengenai persepsi pelanggan terhadap kategori produk secara agregat. Dalam konteks bisnis digital, rata-rata rating sering digunakan sebagai indikator awal untuk membaca kesehatan kategori, karena metrik ini ringkas, mudah dipahami, dan mudah dipantau secara berkala.

Berdasarkan hasil analisis pada sampel 25%, rata-rata rating kategori *Beauty and Personal Care* adalah **4,111**. Angka ini menunjukkan bahwa secara umum persepsi pelanggan terhadap kategori tergolong baik. Namun, rata-rata rating tidak dapat dibaca secara terpisah karena nilai agregat yang relatif tinggi tetap dapat menyembunyikan kelompok pelanggan yang mengalami ketidakpuasan serius. Oleh karena itu, KPI utama ini perlu diperkuat dengan KPI turunan agar pembacaan kondisi kategori menjadi lebih lengkap.

Berdasarkan kondisi tersebut, target KPI utama ke depan yang dapat ditetapkan adalah **meningkatkan rata-rata rating kategori menjadi minimal 4,20**. Target ini cukup realistis karena titik awal kategori sudah berada pada level yang baik, sehingga fokus perbaikan diarahkan pada pengurangan sumber keluhan yang paling dominan. Dengan target tersebut, perusahaan tidak hanya mempertahankan persepsi positif yang sudah ada, tetapi juga mendorong perbaikan pengalaman pelanggan secara bertahap.

### 2. KPI Turunan

Untuk mendukung KPI utama, digunakan dua KPI turunan, yaitu **persentase review buruk (1-2 bintang)** dan **rata-rata helpful votes pada review buruk**.

KPI turunan pertama adalah **persentase review buruk (1-2 bintang)**, yang pada hasil analisis tercatat sebesar **17,22%**. Indikator ini penting karena menunjukkan proporsi pelanggan yang menyampaikan ketidakpuasan tinggi. Dalam konteks keputusan bisnis, metrik ini membantu perusahaan melihat sisi negatif yang tidak selalu terlihat dari rata-rata rating. Dengan kata lain, walaupun rata-rata rating cukup tinggi, proporsi review buruk yang masih cukup besar menandakan adanya masalah nyata yang tetap perlu ditangani.

KPI turunan kedua adalah **rata-rata helpful votes pada review buruk**, yaitu sebesar **1,44**. Indikator ini digunakan untuk menilai apakah review negatif dianggap relevan atau berguna oleh pembeli lain. Jika review buruk memperoleh helpful votes yang cukup tinggi, maka keluhan yang disampaikan cenderung bukan sekadar pengalaman individual, melainkan sinyal yang dipandang penting oleh pasar. Karena itu, metrik ini berguna bagi tim bisnis untuk memprioritaskan jenis keluhan yang berpotensi memengaruhi keputusan pembelian pelanggan lain.

Dengan demikian, kedua KPI turunan ini berfungsi untuk memperkaya pembacaan KPI utama. Rata-rata rating menunjukkan kondisi umum kategori, persentase review buruk mengukur tingkat ketidakpuasan berat, dan helpful votes pada review buruk membantu mengidentifikasi kekuatan sinyal dari keluhan pelanggan.

Selain sebagai alat diagnosis, kedua KPI turunan ini juga dapat diterjemahkan menjadi target operasional. Untuk **persentase review buruk (1-2 bintang)**, target yang layak ditetapkan adalah **menurunkannya dari 17,22% menjadi di bawah 15%**. Penurunan ini penting karena akan menunjukkan bahwa perbaikan kualitas produk dan pengalaman pelanggan benar-benar berdampak pada penurunan keluhan berat.

Untuk **rata-rata helpful votes pada review buruk**, target yang lebih tepat bukan sekadar menaikkan atau menurunkan angka secara mekanis, tetapi **menjaga agar helpful votes pada review buruk tidak meningkat tajam** setelah intervensi dilakukan. Secara praktis, perusahaan dapat menetapkan target agar metrik ini **tetap di sekitar atau di bawah 1,44**, karena kenaikan tajam dapat mengindikasikan bahwa keluhan negatif semakin dianggap relevan oleh pembeli lain. Dengan demikian, KPI ini berfungsi sebagai sinyal apakah isu negatif makin meluas atau mulai terkendali.

### 3. Guardrail KPI

Guardrail KPI yang dipilih adalah **verified purchase share**, yaitu persentase review yang berasal dari pembelian terverifikasi. Pada hasil analisis, nilai indikator ini sebesar **91,10%**. Indikator ini dipilih sebagai batas kehati-hatian agar rekomendasi bisnis tetap bertumpu pada review yang relatif lebih kredibel.

Penggunaan *verified purchase share* penting karena tidak semua review memiliki tingkat keandalan yang sama. Review dari pembelian terverifikasi lebih dapat dipercaya karena berasal dari pelanggan yang benar-benar melakukan transaksi. Dengan menggunakan metrik ini sebagai guardrail, hasil analisis menjadi lebih kuat secara metodologis dan tidak terlalu dipengaruhi oleh review yang kurang representatif.

Dalam konteks bisnis, guardrail ini mengingatkan bahwa keputusan tidak seharusnya hanya ditopang oleh banyaknya review atau tingginya rating, tetapi juga oleh kualitas sumber informasi yang digunakan.

Sebagai target guardrail ke depan, perusahaan dapat menetapkan bahwa **verified purchase share harus dipertahankan minimal pada level 90%**. Target ini penting agar evaluasi kinerja kategori dan keputusan bisnis tetap berbasis pada pengalaman pelanggan yang kuat secara kredibilitas. Jika proporsi review terverifikasi turun terlalu jauh, maka hasil pembacaan KPI utama dan KPI turunan juga berisiko menjadi kurang stabil.

## B. Analisis Voice of Customer dari Teks Review

### 1. Pengambilan dan Preprocessing Data Review Text dari Kategori Beauty_and_Personal_Care

Data yang digunakan berasal dari file `Beauty_and_Personal_Care.jsonl` dari dataset Amazon Reviews 2023. Dataset asli memuat beberapa variabel utama, yaitu `rating`, `title`, `text`, `images`, `asin`, `parent_asin`, `user_id`, `timestamp`, `helpful_vote`, dan `verified_purchase`. Dalam analisis ini, variabel yang paling relevan adalah `rating`, `title`, `text`, `helpful_vote`, `verified_purchase`, `timestamp`, `asin`, dan `parent_asin`.

Karena ukuran file sangat besar, proses analisis dilakukan dengan pendekatan streaming. Selanjutnya, dari populasi tersedia diambil **25% sampel** menggunakan *proportionate stratified deterministic sampling* berdasarkan bulan review dan rating. Teknik ini dipilih agar distribusi waktu dan distribusi sentimen pada sampel tetap mencerminkan populasi.

Pada tahap preprocessing, judul review dan isi review digabungkan menjadi satu teks analisis. Teks kemudian dibersihkan melalui pengubahan huruf menjadi huruf kecil, penghapusan karakter non-alfanumerik yang tidak relevan, serta normalisasi spasi. Tahap ini dilakukan agar data teks menjadi lebih konsisten dan siap digunakan untuk analisis tema serta pemodelan klasifikasi.

### 2. Identifikasi Minimal 3 Tema Keluhan Utama

Berdasarkan hasil analisis review dengan rating rendah, terdapat tiga tema keluhan utama yang paling dominan, yaitu:

1. **Product does not work as expected**
2. **Packaging, leakage, or damaged items**
3. **Skin irritation or side effects**

Tema pertama, yaitu *product does not work as expected*, merupakan tema dengan frekuensi tertinggi pada review buruk, yaitu **549.812 review** atau **13,36%** dari seluruh review buruk. Tema ini menunjukkan bahwa banyak pelanggan merasa produk tidak memberikan hasil sesuai harapan, tidak efektif, atau tidak sejalan dengan klaim manfaatnya.

Tema kedua, yaitu *packaging, leakage, or damaged items*, muncul pada **431.553 review** atau **10,49%** dari review buruk. Temuan ini menunjukkan bahwa masalah pelanggan tidak hanya berasal dari formula atau manfaat produk, tetapi juga dari kondisi fisik produk saat diterima.

Tema ketiga, yaitu *skin irritation or side effects*, ditemukan pada **308.726 review** atau **7,50%** dari review buruk. Tema ini menunjukkan adanya reaksi negatif setelah penggunaan produk, seperti iritasi atau efek samping lain. Dalam kategori *Beauty and Personal Care*, tema ini sangat penting karena terkait langsung dengan keamanan dan kenyamanan pelanggan.

### 3. Perbandingan antara Review Rating Tinggi vs Rendah

Perbandingan antara review rating tinggi dan rating rendah menunjukkan perbedaan pola yang cukup jelas. Review dengan rating tinggi (`4-5`) memiliki rata-rata panjang review sebesar **36,99 kata** dan rata-rata helpful votes sebesar **1,11**. Kata-kata yang paling sering muncul pada review tinggi antara lain *great*, *love*, *hair*, *good*, *skin*, *works*, *well*, dan *stars*. Pola ini menunjukkan bahwa review positif cenderung menekankan efektivitas, kepuasan, dan manfaat yang dirasakan pelanggan.

Sebaliknya, review dengan rating rendah (`1-2`) memiliki rata-rata panjang review sebesar **41,31 kata** dan rata-rata helpful votes sebesar **1,44**. Kata-kata yang paling sering muncul pada review rendah antara lain *hair*, *work*, *good*, *money*, *doesn*, *didn*, *skin*, dan *smell*. Dibandingkan review positif, review negatif cenderung lebih panjang, lebih eksplisit dalam menjelaskan masalah, dan sedikit lebih tinggi tingkat relevansinya bagi pembaca lain.

Temuan ini menunjukkan bahwa review buruk cenderung lebih informatif dalam mengungkapkan sumber ketidakpuasan pelanggan. Karena itu, review negatif merupakan sumber data yang sangat penting untuk evaluasi kualitas dan pengambilan keputusan perbaikan.

### 4. Analisis Pola dan Isu Utama yang Dirasakan Pelanggan

Keluhan yang paling sering muncul adalah produk yang tidak bekerja sesuai harapan. Hal ini menandakan bahwa pelanggan dalam kategori *Beauty and Personal Care* sangat menilai hasil nyata dari penggunaan produk. Ketika manfaat yang dijanjikan tidak dirasakan, pelanggan cenderung memberikan rating rendah dan menyampaikan keluhan secara langsung.

Review buruk juga menunjukkan pola tema tertentu, terutama yang berkaitan dengan kerusakan kemasan, kebocoran, dan kondisi barang saat diterima. Dengan kata lain, pengalaman pelanggan tidak hanya ditentukan oleh isi produk, tetapi juga oleh kualitas pengemasan dan distribusi.

Selain itu, tema iritasi atau efek samping menegaskan bahwa pelanggan sangat sensitif terhadap aspek keamanan. Dalam kategori yang bersentuhan langsung dengan tubuh, isu keamanan memiliki implikasi reputasi yang sangat besar. Jika tema ini terus muncul, maka risikonya tidak hanya pada penurunan rating, tetapi juga pada penurunan kepercayaan terhadap merek.

Secara umum, *voice of customer* menunjukkan bahwa masalah utama yang dirasakan pelanggan berpusat pada tiga aspek: efektivitas produk, kualitas fisik produk saat diterima, dan keamanan penggunaan.

## C. Translasi Insight ke Bahasa Bisnis

Berikut adalah hasil translasi insight analisis data dan teks review ke dalam bahasa bisnis:

| Temuan Data | Makna Bisnis | Implikasi Keputusan |
|---|---|---|
| Rata-rata rating kategori mencapai 4,111, tetapi persentase review buruk masih sebesar 17,22%. | Persepsi umum terhadap kategori tergolong baik, namun terdapat kelompok pelanggan yang mengalami ketidakpuasan serius dalam proporsi yang tidak kecil. | Perusahaan perlu memantau rata-rata rating bersama proporsi review buruk agar tidak hanya berfokus pada skor agregat. |
| Tema keluhan utama pada review rendah adalah produk tidak bekerja sesuai harapan. | Masalah utama pelanggan terletak pada efektivitas produk dan kesesuaian antara klaim produk dengan pengalaman nyata. | Perlu dilakukan evaluasi pada kualitas produk, formulasi, dan komunikasi klaim pemasaran agar lebih realistis. |
| Keluhan tentang kemasan bocor, rusak, atau terbuka masih sangat dominan. | Pengalaman negatif pelanggan juga dipengaruhi oleh proses pengemasan dan distribusi, bukan hanya isi produk. | Tim operasional dan quality control perlu memperkuat standar kemasan dan penanganan distribusi. |
| Review buruk memiliki helpful votes rata-rata lebih tinggi dibanding review baik. | Sebagian review negatif dipandang relevan oleh pembeli lain dan berpotensi memengaruhi keputusan pembelian. | Tim bisnis perlu memprioritaskan review negatif yang paling menonjol dan sering dianggap helpful. |
| Model klasifikasi sederhana mencapai accuracy 0,9492 dan ROC-AUC 0,9859. | Otomasi awal cukup efektif untuk membantu membaca volume review yang besar. | Model dapat digunakan sebagai alat *early warning* untuk membantu prioritas penanganan review. |

## D. Predictive Modeling Sederhana

### 1. Pembangunan Model Klasifikasi Sederhana

Dalam penelitian ini dibangun model klasifikasi sederhana menggunakan **Multinomial Naive Bayes** untuk membedakan review baik dan review buruk. Review baik didefinisikan sebagai review dengan rating `4-5`, sedangkan review buruk didefinisikan sebagai review dengan rating `1-2`. Review dengan rating 3 tidak digunakan dalam pemodelan agar batas antara dua kelas lebih jelas.

Pemilihan *Multinomial Naive Bayes* didasarkan pada beberapa pertimbangan. Pertama, model ini sederhana dan efisien untuk data teks dalam skala besar. Kedua, model ini cocok untuk pendekatan fitur berbasis frekuensi kata. Ketiga, model ini cukup mudah dijelaskan dalam konteks analisis bisnis, sehingga hasilnya lebih mudah diterjemahkan menjadi manfaat praktis bagi tim non-teknis.

### 2. Pemilihan Fitur Sederhana

Fitur utama yang digunakan dalam model adalah **teks review**, yang diubah menjadi representasi numerik menggunakan **HashingVectorizer**. Pendekatan ini memungkinkan teks dalam volume besar diubah menjadi fitur yang dapat diproses model tanpa harus menyimpan kamus kata yang sangat besar di memori.

Walaupun model prediktif terutama bertumpu pada teks review, analisis pendukung tetap mempertimbangkan **panjang review** dan **helpful votes** sebagai konteks perilaku pelanggan. Panjang review digunakan untuk melihat perbedaan karakteristik antara review baik dan buruk, sedangkan helpful votes digunakan untuk menilai tingkat relevansi review bagi pengguna lain.

Pemilihan fitur semacam ini selaras dengan kebutuhan tugas, yaitu membangun model yang sederhana, efisien, dan tetap memiliki nilai praktis untuk membantu tim bisnis.

### 3. Evaluasi Hasil Model dan Manfaatnya bagi Tim Bisnis

Berdasarkan hasil evaluasi pada data uji, model menghasilkan metrik sebagai berikut:

- **Accuracy**: 0,9492
- **Precision kelas review baik**: 0,9538
- **Recall kelas review baik**: 0,9853
- **F1-score kelas review baik**: 0,9693
- **Precision kelas review buruk**: 0,9249
- **Recall kelas review buruk**: 0,7907
- **F1-score kelas review buruk**: 0,8525
- **ROC-AUC**: 0,9859

Hasil tersebut menunjukkan bahwa model **cukup membantu** untuk membedakan review baik dan review buruk. Secara khusus, model sangat baik dalam mengenali review baik, sementara kemampuan mengenali review buruk juga tergolong baik meskipun tidak sekuat kelas positif. Dalam konteks operasional, hal ini tetap bermanfaat karena model mampu mempercepat proses identifikasi review yang perlu diperhatikan dari jutaan data yang tersedia.

Bagi tim bisnis, model ini berguna karena dapat berfungsi sebagai alat *triage* awal. Tim *customer service*, *quality assurance*, dan manajemen produk tidak perlu membaca seluruh review secara manual, tetapi dapat lebih dahulu memfokuskan perhatian pada review yang diprediksi berpotensi bermasalah. Dengan demikian, sumber daya dapat digunakan lebih efisien dan respon terhadap isu pelanggan dapat dipercepat.

### 4. Analisis Risiko Bisnis bila Terdapat Mis-klasifikasi Review Buruk sebagai Review Baik

Risiko bisnis utama dalam penggunaan model ini adalah ketika **review buruk diprediksi sebagai review baik**. Pada hasil evaluasi, terdapat **172.675 review buruk** pada data uji yang diprediksi sebagai review baik. Kesalahan semacam ini berbahaya karena dapat membuat keluhan serius tidak segera terdeteksi.

Jika review yang sebenarnya berisi masalah kualitas, kerusakan produk, atau efek samping terlewatkan, maka perusahaan dapat terlambat mengambil tindakan korektif. Dampaknya dapat berupa penurunan kepuasan pelanggan, peningkatan retur atau komplain, memburuknya rating produk, hingga penurunan reputasi merek. Risiko ini sangat penting pada kategori *Beauty and Personal Care* karena banyak produk terkait langsung dengan tubuh dan keamanan penggunaan.

Dengan demikian, model ini sebaiknya diposisikan sebagai **alat bantu prioritisasi**, bukan sebagai pengganti evaluasi manual sepenuhnya. Review yang terindikasi penting atau sensitif tetap perlu ditinjau kembali secara manual, terutama pada area yang berkaitan dengan keamanan pelanggan dan kualitas produk.

# BAB 3 KESIMPULAN

## 3.1 Ringkasan Hasil Analisis dan Temuan Utama

Analisis terhadap 25% sampel data review kategori `Beauty_and_Personal_Care` menunjukkan bahwa secara umum kategori memiliki persepsi pelanggan yang cukup baik, tercermin dari rata-rata rating sebesar **4,111**. Namun, di balik skor tersebut masih terdapat **17,22% review buruk**, yang menunjukkan bahwa masalah pelanggan tetap cukup signifikan dan tidak dapat diabaikan.

Hasil analisis *voice of customer* menunjukkan bahwa tema keluhan utama pelanggan berpusat pada tiga isu, yaitu produk yang tidak bekerja sesuai harapan, masalah pada kemasan atau kerusakan produk saat diterima, serta iritasi atau efek samping setelah penggunaan. Selain itu, review buruk cenderung lebih panjang dan sedikit lebih tinggi helpful votes-nya dibanding review baik, yang menunjukkan bahwa review negatif banyak memuat informasi penting yang relevan bagi pelanggan lain.

Pada sisi pemodelan, model *Multinomial Naive Bayes* menunjukkan performa yang baik dengan accuracy **0,9492** dan ROC-AUC **0,9859**. Model ini cukup efektif sebagai alat bantu pemilahan awal antara review baik dan review buruk, meskipun masih memiliki risiko mis-klasifikasi yang perlu diwaspadai.

## 3.2 Rekomendasi Keputusan Bisnis Berdasarkan Hasil Analisis dan Model Prediktif

Berdasarkan hasil analisis, terdapat beberapa rekomendasi keputusan bisnis yang dapat dipertimbangkan. Pertama, perusahaan perlu memprioritaskan audit kualitas pada produk yang paling sering dikeluhkan karena tidak bekerja sesuai harapan. Kedua, standar quality control pada kemasan dan distribusi perlu diperkuat untuk menurunkan keluhan terkait kebocoran, kerusakan, atau kondisi produk saat diterima pelanggan. Ketiga, perusahaan perlu memantau rata-rata rating bersamaan dengan persentase review buruk agar sistem pemantauan kinerja kategori menjadi lebih sensitif terhadap sinyal masalah.

Selain itu, model klasifikasi sederhana yang dibangun dapat dimanfaatkan sebagai sistem *early warning* untuk membantu tim bisnis memprioritaskan review yang perlu ditindaklanjuti. Meskipun demikian, hasil model tidak sebaiknya digunakan sebagai satu-satunya dasar keputusan. Review yang berkaitan dengan isu kualitas serius, keamanan, atau efek samping tetap perlu diverifikasi secara manual agar risiko bisnis akibat kesalahan klasifikasi dapat ditekan.

# DAFTAR PUSTAKA

1. McAuley Lab. (2024). *Amazon Reviews 2023*. Hugging Face Datasets. [https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)
2. Hou, Y., Li, J., He, Z., et al. (2024). *Bridging Language and Items for Retrieval and Recommendation*. arXiv. [https://arxiv.org/abs/2403.03952](https://arxiv.org/abs/2403.03952)
3. Amazon Reviews'23. (2024). *Dataset Documentation and Data Fields*. [https://amazon-reviews-2023.github.io/main.html](https://amazon-reviews-2023.github.io/main.html)
4. James, G., Witten, D., Hastie, T., & Tibshirani, R. (2021). *An Introduction to Statistical Learning* (2nd ed.). Springer.

# LAMPIRAN / APPENDIX

## 1. Grafik Sederhana, Tabel KPI, Ringkasan Tema Review, dan Hasil Evaluasi Model

Lampiran pendukung analisis tersedia pada folder `outputs`, khususnya:

- `outputs/figures/rating_distribution.png`
- `outputs/figures/monthly_avg_rating.png`
- `outputs/figures/complaint_themes.png`
- `outputs/figures/confusion_matrix.png`
- `outputs/tables/kpi_table.csv`
- `outputs/tables/monthly_rating.csv`
- `outputs/tables/full_data_summary.csv`
- `outputs/tables/voc_themes.csv`
- `outputs/tables/review_segment_comparison.csv`
- `outputs/tables/business_translation.csv`
- `outputs/tables/model_metrics.csv`
- `outputs/tables/classification_report.csv`

## 2. Notebook / Script

Script utama yang digunakan dalam penelitian ini adalah:

- `analyze_amazon_beauty.py`

Script tersebut memuat proses data loading, sampling, preprocessing, analisis KPI, analisis tema review, dan pembangunan model klasifikasi sederhana.

## 3. Bukti-bukti Pendukung Lainnya

Bukti pendukung lain yang dapat digunakan untuk pelaporan antara lain:

- `outputs/text/run_summary.json` sebagai ringkasan angka hasil analisis
- `decision_memo.md` sebagai memo keputusan bisnis singkat
- `appendix_evidence.md` sebagai ringkasan evidence pendukung
