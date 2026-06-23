# Step 5 - Loss Ratio & Profitability Analysis

## Slide 1 - Framework Step 5

**Judul slide**  
Step 5 - Loss Ratio & Profitability Analysis

**Menjawab pertanyaan**  
"Segmen mana yang paling menguntungkan dan paling merugikan?"

**Yang dihitung**
- Gross Loss Ratio
- Net Loss Ratio

**Formula**
- Gross Loss Ratio = Gross Incurred Claim / GWP
- Net Loss Ratio = Net Incurred Claim / Net Premium

**Penjelasan formula berdasarkan data**
- Gross Incurred Claim = `GRS_ST_IDR + GRS_OS_IDR`
- Net Incurred Claim = `(GRS_ST_IDR + GRS_OS_IDR) - (RI_ST_IDR + RI_OS_IDR)`
- Net Premium = `GWP_IDR - RWP_IDR`

**Yang dianalisis**
- Ranking loss ratio per segmen
- Perbandingan Gross vs Net Loss Ratio
- Analisis profitabilitas:
- dengan large claim
- tanpa large claim
- Analisis trend loss ratio per tahun underwriting

**Interpretasi**
- Loss Ratio > 100% -> loss making
- Reasuransi membantu menurunkan beban klaim secara nominal
- Net LR tidak selalu lebih rendah dari Gross LR karena net premium lebih kecil setelah reasuransi

**Tujuan**
- Mengukur profitabilitas portofolio
- Mengetahui segmen yang memberikan kerugian terbesar

**Catatan untuk visual slide**
- Slide ini bisa dibuat seperti slide framework/metodologi
- Tidak wajib memakai chart besar
- Jika ingin menambahkan visual kecil, gunakan chart berikut sebagai preview analisis:
- Gross vs Net Loss Ratio by COB  
  [chart_01_cell7_out1.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_01_cell7_out1.png)

---

## Slide 2 - Hasil Analisis dan Jawaban Step 5

**Judul slide**  
Hasil Step 5 - Segmen Paling Menguntungkan dan Paling Merugikan

**Ringkasan hasil portofolio**
- Net Premium portofolio = `IDR 1.964T`
- Net Claim portofolio = `IDR 1.150T`
- Net Underwriting Result = `IDR 358.7B`
- Gross Loss Ratio portofolio = `49.34%`
- Net Loss Ratio portofolio = `58.54%`

**Ranking segmen paling menguntungkan**
- `COB` terbaik: `COB 3` dengan `Net LR 6.03%`
- `Branch` terbaik: `BRANCH H` dengan `Net LR 12.02%`
- `Channel` terbaik: `CHANNEL D` dengan `Net LR 17.60%`
- `Product` terbaik dalam ranking utama: `PRODUCT1006` dengan `Net LR 2.62%`

**Ranking segmen paling merugikan**
- `COB` terburuk: `COB 4` dengan `Net LR 106.55%`
- `Branch` terburuk: `BRANCH K` dengan `Net LR 103.87%`
- `Channel` terburuk: `CHANNEL B` dengan `Net LR 116.16%`
- `Product` terburuk dalam ranking utama: `PRODUCT0221` dengan `Net LR 120.59%`

**Perbandingan Gross vs Net Loss Ratio**
- Pada beberapa segmen, Net LR lebih tinggi daripada Gross LR
- Hal ini tidak otomatis berarti reasuransi buruk, karena reasuransi juga menurunkan net premium
- Untuk melihat manfaat reasuransi, lebih tepat melihat `reinsurance recovery` dan `claim relief`

**Analisis profitabilitas dengan large claim vs tanpa large claim**
- Dalam sensitivity analysis tanpa dampak large claim, Net LR portofolio turun dari `58.54%` menjadi `5.07%`
- Segmen yang paling sensitif terhadap large claim adalah `COB 4`, `COB 6`, dan `COB 7`
- Ini menunjukkan bahwa downside portofolio sangat dipengaruhi oleh shock claim besar

**Analisis trend loss ratio per underwriting year**
- `2021`: Net LR `68.77%`
- `2022`: Net LR `32.78%`
- `2023`: Net LR `38.24%`
- Artinya, cohort 2021 adalah yang paling lemah, lalu membaik di 2022, tetapi naik kembali di 2023

**Kesimpulan utama**
- Portofolio secara total masih profitable, tetapi ada beberapa segmen yang sudah loss-making
- Segmen yang paling perlu perhatian adalah `COB 4`, `BRANCH K`, `CHANNEL B`, dan `PRODUCT0221`
- Large claim menjadi pendorong utama downside sehingga penguatan underwriting, pricing, dan claim management perlu difokuskan pada segmen-segmen tersebut

**Chart yang disarankan untuk slide ini**
- Gross vs Net Loss Ratio by COB  
  [chart_01_cell7_out1.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_01_cell7_out1.png)
- Reinsurance Claim Relief by COB  
  [chart_02_cell7_out2.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_02_cell7_out2.png)
- Sensitivity to Large Claims - Reduction in Net LR by COB  
  [chart_03_cell8_out2.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_03_cell8_out2.png)
- Loss Ratio Trend by Underwriting Year  
  [chart_04_cell9_out1.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_04_cell9_out1.png)

**Chart opsional jika masih ada ruang**
- Net Loss Ratio Trend by Underwriting Year and COB  
  [chart_05_cell9_out3.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_05_cell9_out3.png)

---

## Bank Chart

- Gross vs Net Loss Ratio by COB: [chart_01_cell7_out1.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_01_cell7_out1.png)
- Reinsurance Claim Relief by COB: [chart_02_cell7_out2.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_02_cell7_out2.png)
- Sensitivity to Large Claims - Reduction in Net LR by COB: [chart_03_cell8_out2.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_03_cell8_out2.png)
- Loss Ratio Trend by Underwriting Year: [chart_04_cell9_out1.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_04_cell9_out1.png)
- Net Loss Ratio Trend by Underwriting Year and COB: [chart_05_cell9_out3.png](D:/UNAIR/SEMESTER%206/SDC/case-study-sdc/charts_for_ppt/chart_05_cell9_out3.png)
