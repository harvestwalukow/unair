setwd("D:/Statistika/Komputasi Statistika/txt")

#No 1. (RAL)

#memanggil data
Data1 = read.table("Data Praktikum 8.1.txt", header = TRUE, colClasses = c("numeric", "factor"))
y1 = Data1$Asam_Askorbat
perlakuan = Data1$Varietas

summary(Data1)

#ANOVA
ANOVA1 <- aov(y1 ~ perlakuan, data = Data1)
summary(ANOVA1)
#H0: Tidak Ada perbedaan rata-rata asam askorbat
#H1: ada perbedaan rata-rata asam askorbat
#kesimpulan: Tolak H0 karena p-value < alpha, sehingga ada perbedaan rata-rata asam askorbat

#No. 2 (RAKL)
#H0: Tidak Terdapat pengaruh penyinaran dan penyiraman
#H1: Terdapat pengaruh penyinaran dan penyiraman
#Memanggil Data
Data2 = read.table("Data Praktikum 8.2.txt", header = TRUE, colClasses = c("numeric", "factor", "factor"))
Data2
y2 = Data2$Pertumbuhan_Tanaman
Perlakuan_A = Data2$Penyiraman
Perlakuan_B = Data2$Penyinaran_Matahari

summary(Data2)

#ANOVA
#-----Tanpa Interaksi-----
ANOVA2 <- aov(y2 ~ Perlakuan_A + Perlakuan_B, data = Data2)
summary(ANOVA2)
#Perlakuan A: Gagal tolak H0 (p value (0.655) > alpha(0.05))
#Perlakuan B: Tolak H0 (Pvalue (5.26e-08) < alpha (0.05))

#-----dengan interaksi-----
INTERACTION <- aov(y2 ~ Perlakuan_A * Perlakuan_B, data = Data2)
summary(INTERACTION)
#P value > alpha (0.659 > 0.05), sehingga gagal tolak H0, jadi tidak terdapat pengaruh penyinaran dan penyiraman


#No 3 (RBAL) Rancangan Bujur Sangkar Latin

#Memanggil Data
#H0: Tidak ada pengaruh 
#H1: Ada pengaruh
Data3 = read.table("Data Praktikum 8.3.txt", header = TRUE, colClasses = c("numeric", "factor", "factor"))
y3 = Data3$Hardness
Treatments = Data3$Tip
Block = Data3$Block

summary(Data3)

#ANOVA
ANOVA3 <- aov(y3 ~ Treatments + Block, data = Data3)
summary(ANOVA3)

#kesimpulan treatments: Tolak H0 (p value < alpha)
#kesimpulan block: Tolak H0 (p value < alpha)

#No 4
#LSD/RBSL (rancangan bujur sangkar latin)
#memanggil data
#H0: Tidak terdapat pengaruh
#H1: Terdapat Pengaruh
Data4 = read.table("Data Praktikum 8.4.txt", header = TRUE, colClasses = c("factor", "numeric", "factor", "factor"))

Data4
summary(Data4)

#subset Data
Perlakuan= Data4$Perlakuan
Perlakuan
y1= Data4$Pertumbuhan_Tanaman_Jagung
y1
Baris= Data4$Baris
Baris
Kolom= Data4$Kolom
Kolom

#ANOVA RBSL
ANOVA4 <- aov(y1 ~ Perlakuan+Baris+Kolom, data = Data4)
summary(ANOVA4)
#Kesimpulan
#perlakuan: tolak H0
#baris: gagal tolak H0
#kolom: tolak H0

#No 5 (Rancangan Faktorial)
#H0: Tidak terdapat pengaruh
#H1: Terdapat Pengaruh
#Import Data
Data5 = read.table("Data Praktikum 8.5.txt", header = TRUE, colClasses = c("numeric", "factor", "factor"))

Data5
summary(Data5)
#Subset Data
y2=Data5$Daya_Tahan_Battery
y2
jb=Data5$Jenis_Bahan
jb
temp=Data5$Temperatur
temp

#ANOVA Faktorial_RAL
ANOVA2 <- aov(y2 ~ jb+temp+jb*temp, data = Data5)
summary(ANOVA2)
#---------------------------------
ANOVA2_v2 <- aov(y2 ~ jb*temp, data = Data5)
summary(ANOVA2_v2)
