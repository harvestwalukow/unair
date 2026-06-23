# Panduan SPSS - Regresi Logistik Ordinal

Panduan ini memakai pengkodean yang sama dengan notebook Python.

## 1. Masukkan data

1. Buka SPSS, lalu pilih **File > Open > Data**.
2. Cara termudah adalah membuka `data_regresi_logistik_ordinal.csv` yang
   dihasilkan notebook.
3. Pastikan urutan variabel:
   `no`, `kepuasan`, `provider`, `sinyal`, `tarif_sms`, `tarif_data`, `usia`.
4. Pada **Variable View**, isi:
   - `kepuasan`: Measure = Ordinal.
   - `provider`, `sinyal`, `tarif_sms`, `tarif_data`: Measure = Nominal.
   - `usia`: Measure = Scale.
5. Tambahkan Value Labels sesuai soal.

## 2. Jalankan ordinal regression

1. Pilih **Analyze > Regression > Ordinal**.
2. Masukkan `kepuasan` ke **Dependent**.
3. Masukkan `provider`, `sinyal`, `tarif_sms`, dan `tarif_data` ke **Factor(s)**.
4. Masukkan `usia` ke **Covariate(s)**.
5. Klik **Output**, lalu centang:
   - Model fitting information
   - Goodness-of-fit
   - Pseudo R-square
   - Parameter estimates
   - Test of parallel lines
   - Cell information, bila tersedia
6. Klik **Location** dan pilih main effects untuk seluruh prediktor.
7. Pada pengaturan kategori faktor, gunakan kategori referensi **Last** agar
   sama dengan Python: Axis, sinyal Lemah, tarif SMS Murah, tarif data Murah.
8. Pastikan **Link function = Logit**, lalu klik **OK**.

## 3. Syntax SPSS

Nama subperintah dapat sedikit berbeda antarversi SPSS. Syntax PLUM yang umum:

```spss
PLUM kepuasan BY provider sinyal tarif_sms tarif_data
  WITH usia
  /CRITERIA = CIN(95) DELTA(0) MXITER(100) MXSTEP(5)
              LCHECK(0) PCONVERGE(1.0E-6) SINGULAR(1.0E-8)
  /LINK = LOGIT
  /PRINT = FIT PARAMETER SUMMARY TPARALLEL
  /DESIGN = provider sinyal tarif_sms tarif_data usia.
```

Untuk memastikan referensi faktor benar, periksa kategori yang parameternya
ditulis `0a` pada tabel **Parameter Estimates**. Kategori tersebut harus kategori
terakhir yang dipakai notebook.

## 4. Cara membaca output

### Model Fitting Information

Bandingkan **Intercept Only** dan **Final**. Nilai Sig. pada chi-square < 0,05
berarti seluruh prediktor secara simultan memperbaiki model.

### Goodness-of-Fit

Pada Pearson dan Deviance, Sig. > 0,05 berarti tidak ada bukti ketidakcocokan
model. Karena hanya ada 66 observasi dan banyak pola kovariat, hasil ini perlu
dibaca hati-hati bila banyak expected count kecil.

### Pseudo R-Square

Laporkan Cox and Snell, Nagelkerke, dan McFadden. Angka tersebut bukan proporsi
keragaman yang identik dengan R-square regresi linear.

### Parameter Estimates

- Baris **Threshold** adalah batas antara kategori kepuasan.
- Baris **Location** adalah koefisien prediktor.
- Sig. < 0,05 menunjukkan parameter berbeda dari nol.
- OR dihitung dengan `EXP(B)`, tetapi cek arah parameterisasi.

Model Python memakai:

`logit[P(Y <= j)] = threshold_j - x beta`

SPSS sering menampilkan location dengan tanda berlawanan. Jika tanda SPSS
berlawanan dari Python, untuk OR menuju **kepuasan lebih tinggi** gunakan
`EXP(-B_SPSS)`. Nilai p, prediksi, dan kesimpulan model tetap seharusnya sama.

### Test of Parallel Lines

Hipotesis nol menyatakan koefisien sama pada semua batas kategori. Sig. > 0,05
berarti asumsi proportional odds/parallel lines tidak ditolak. Sig. < 0,05
menunjukkan asumsi tersebut bermasalah.

## 5. Uji parsial per faktor

Tabel Parameter Estimates menguji setiap dummy secara terpisah. Untuk menguji
satu faktor secara keseluruhan, jalankan kembali model setelah menghapus satu
prediktor, lalu hitung:

`LR = (-2LL model reduced) - (-2LL model full)`

Derajat bebas adalah selisih jumlah parameter:

- provider: 4 df
- sinyal: 2 df
- tarif SMS: 2 df
- tarif data: 2 df
- usia: 1 df

Bandingkan LR dengan chi-square atau gunakan p-value. Notebook sudah menghitung
uji drop-term ini secara otomatis.

## 6. Ketepatan klasifikasi di SPSS

PLUM tidak selalu menampilkan classification table secara langsung. Simpan
probabilitas prediksi bila versi SPSS menyediakan tombol **Save**, lalu:

1. Tentukan kelas prediksi dari probabilitas terbesar.
2. Pilih **Analyze > Descriptive Statistics > Crosstabs**.
3. Row = `kepuasan`; Column = kelas prediksi.
4. Akurasi = jumlah diagonal / 66 x 100%.

Gunakan tabel klasifikasi Python sebagai hasil utama bila opsi Save tidak ada.

## 7. Struktur laporan

1. Definisi variabel dan pengkodean.
2. Model ordinal logit dan kategori referensi.
3. Model fitting/uji simultan.
4. Uji parsial per prediktor.
5. Persamaan model dan interpretasi koefisien.
6. Odds ratio dan interval kepercayaan.
7. Goodness-of-fit dan test of parallel lines.
8. Pseudo R-square.
9. Ketepatan klasifikasi.
10. Tabel perbandingan Python dan SPSS serta kesimpulan.
