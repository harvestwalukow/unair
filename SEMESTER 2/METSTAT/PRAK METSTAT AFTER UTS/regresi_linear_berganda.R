# nomor 1
data1 <- data.frame(penjualan <- c(72,76,78,70,68,80,82,65,62,90),
                    jumlah_iklan <- c(12,11,15,10,11,16,14,8,8,18),
                    jumlah_endorse <- c(5,8,6,5,3,9,12,14,3,10))

model1 <- lm(penjualan ~ jumlah_iklan + jumlah_endorse,data1)
summary(model1)


# nomor 2
library(readr)
concrete <- read_csv("D:/UNAIR/SEMESTER 2/METSTAT/PRAK METSTAT AFTER UTS/concrete.csv")
head(concrete)

model2 <- lm(strength ~ cement + slag + ash + water + superplastic + coarseagg + fineagg + age, data = concrete)
summary(model2)

# nomor 3
library(tidyverse)
library(datarium)
data("marketing", package = "datarium")
head(marketing, 4)

Y = marketing$sales
X1 = marketing$youtube
X2 = marketing$newspaper
X3 = marketing$facebook

#Building Model
model3 <- lm(Y ~ X1 + X2 + X3, data = marketing)
summary(model3)

#Delete variabel newspaper
model3b <- lm(Y ~ X1 + X3, data = marketing)
summary(model3b)

# nomor 4
data4 <- data.frame(y <- c(1.45, 1.93, 0.81, 0.61, 1.55, 0.95, 0.45, 1.14, 0.74, 0.98, 1.41, 0.81, 0.89, 0.68, 1.39, 1.53, 0.91, 1.49, 1.38, 1.73, 1.11, 1.68, 0.66, 0.69, 1.98),
                    x1 <- c(0.58, 0.86, 0.29, 0.2, 0.56, 0.28, 0.08, 0.41, 0.22, 0.35, 0.59, 0.22, 0.26, 0.12, 0.65, 0.7, 0.3, 0.7, 0.39, 0.72, 0.45, 0.81, 0.04, 0.2, 0.95),
                    x2 <- c(0.71, 0.13, 0.79, 0.2, 0.56, 0.92, 0.01, 0.6, 0.7, 0.73, 0.13, 0.96, 0.27, 0.21, 0.88, 0.30, 0.15, 0.09, 0.17, 0.25, 0.30, 0.32, 0.82, 0.98, 0.00))

model4 <- lm(y ~ x1 + x2, data = data4)
summary(model4)

                      
             