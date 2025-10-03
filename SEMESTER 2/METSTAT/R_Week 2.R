#SOAL 1
read.csv("D:\\UNAIR\\SEMESTER 2\\METSTAT\\soal1.txt")

Soal1=read.table("D:\\UNAIR\\SEMESTER 2\\METSTAT\\soal1.txt", header=TRUE, colClasses = c("numeric", "factor"))
y1=Soal1$Hasil
perlakuan=Soal1$Perlakuan
summary(Soal1)

ANOVA1 <- aov(y1 ~ perlakuan, data = Soal1)
summary(ANOVA1)

#SOAL 2
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
