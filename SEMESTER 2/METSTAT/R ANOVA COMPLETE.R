##------------------------------------PRAKTIKUM TM 2------------------------------------
#SOAL 1 (RAL ONE-WAY)
read.csv("D:\\UNAIR\\SEMESTER 2\\METSTAT\\Data Praktikum M2-20240316\\M2-Data Praktikum 1.txt")
soal_prak1=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\Data Praktikum M2-20240316\\M2-Data Praktikum 1.txt", header=TRUE)

y_prak1=soal_prak1$Asam_Askorbat
perlakuan_prak1=soal_prak1$Varietas

summary(soal_prak1)

ANOVA_prak1 <- aov(y_prak1  ~ perlakuan_prak1, data = soal_prak1)
summary(ANOVA_prak1)

#SOAL 2 (RAL TWO-WAY)
soal_prak2=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\Data Praktikum M2-20240316\\M2-Data Praktikum 2.txt", header=TRUE)

y_prak2=soal_prak2$Pertumbuhan_Tanaman
perlakuanA_prak2=soal_prak2$Penyiraman
perlakuanB_prak2=soal_prak2$Penyinaran_Matahari

summary(soal_prak2)

#tanpa interaksi
ANOVA_prak2 <- aov(y_prak2 ~ perlakuanA_prak2+perlakuanB_prak2, data = soal_prak2)
summary(ANOVA_prak2)

#dengan interaksi
ANOVA_prak2_interaction <- aov(y_prak2 ~ perlakuanA_prak2*perlakuanB_prak2, data = soal_prak2)
summary(ANOVA_prak2_interaction)

#SOAL 3 (RAKL)
soal_prak3=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\Data Praktikum M2-20240316\\M2-Data Praktikum 3.txt", header=TRUE)

y_prak3=soal_prak3$Hardness
perlakuan_prak3=soal_prak3$Tip
blok_prak3=soal_prak3$Block

summary(soal_prak3)

ANOVA_prak3 = aov(y_prak3 ~ perlakuan_prak3+blok_prak3, data = soal_prak3)
summary(ANOVA_prak3)

##------------------------------------TUGAS TM 2------------------------------------
#SOAL 1 (RAL ONE-WAY)
read.csv("D:\\UNAIR\\SEMESTER 2\\METSTAT\\soal1.txt")

Soal1=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\soal1.txt", header=TRUE, colClasses = c("numeric", "factor"))
y1=Soal1$Hasil
perlakuan=Soal1$Perlakuan
summary(Soal1)

ANOVA1 <- aov(y1 ~ perlakuan, data = Soal1)
summary(ANOVA1)

#SOAL 2 (RAL TWO-WAY)
Soal2=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\soal2.txt", header=TRUE, colClasses = c("numeric", "factor", "factor"))
y2=Soal2$Gaji
Perlakuan_A=Soal2$Lokasi
Perlakuan_B=Soal2$Tipe
summary(Soal2)

#ANOVA
#-----------tanpa interaksi-----------
ANOVA2 <- aov(y2 ~ Perlakuan_A + Perlakuan_B, data = Soal2)
summary(ANOVA2)

#-----------dengan interaksi-----------
INTERACTION <- aov(y2 ~ Perlakuan_A * Perlakuan_B, data = Soal2)
summary(INTERACTION)


##------------------------------------PRAKTIKUM TM 3------------------------------------
#NOMOR 1 (LSD/RBSL)
setwd("D:/UNAIR/SEMESTER 2/METSTAT/")

soal_prak1_2=read.table("m3 factorial design rakl 1.txt", header = TRUE, colClasses = c("factor","numeric","factor","factor"))
soal_prak1_2
summary(soal_prak1_2)

perlakuan_prak1_2=soal_prak1_2$Perlakuan
y_prak1_2=soal_prak1_2$Pertumbuhan_Tanaman_Jagung
baris_prak1_2=soal_prak1_2$Baris
kolom_prak1_2=soal_prak1_2$Kolom

ANOVA_prak1_2 = aov(y_prak1_2 ~ perlakuan_prak1_2+baris_prak1_2+kolom_prak1_2, data = soal_prak1_2)
summary(ANOVA_prak1_2)

#NOMOR 2 (FACTORIAL RAL)
soal_prak2_2=read.table("m3 factorial design rakl 2.txt", header = TRUE, colClasses = c("numeric","factor","factor"))

y_prak2_2=soal_prak2_2$Daya_Tahan_Battery
jb=soal_prak2_2$Jenis_Bahan
temp=soal_prak2_2$Temperatur

ANOVA_prak2_2= aov(y_prak2_2 ~ jb+temp+jb*temp, data=soal_prak2_2)
summary(ANOVA_prak2_2)

#NOMOR 3 (FACTORIAL RAKL)
Data3 <- read.table("m3 factorial design rakl 3.txt", header = TRUE, colClasses = c("numeric","factor","factor","factor"))
Data3
summary(Data3)

#Subset Data
y3=Data3$Kekuatan_Signal
jf=Data3$Jenis_Filter
opt=Data3$Operator
lok=Data3$Lokasi

#ANOVA Faktorial_RAKL
#Interaksi 3 faktor
ANOVA3 <- aov(y3 ~ jf+opt+lok+jf*opt+jf*lok+opt*lok+jf*opt*lok, data = Data3)
summary(ANOVA3)