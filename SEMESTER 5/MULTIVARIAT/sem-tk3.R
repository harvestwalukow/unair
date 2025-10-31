# load library
library(lavaan)
library(semPlot)

# baca dataset
data <- read.csv("SPHERE dataset cleaned.csv")

# definisikan model SEM
model <- '
  # ------------------------------------
  # Variabel Laten Eksogen
  # ------------------------------------
  Sikap_Belajar =~ CLASS3 + CLASS11 + CLASS14 + CLASS25 + CLASS28 + CLASS30
  Upaya_Pemaknaan =~ CLASS23 + CLASS24 + CLASS32 + CLASS36 + CLASS39 + CLASS42
  Status_Sosial_Ekonomi =~ FATHINC + MOTHINC + FATHOCC + MOTHOCC + FATHEDU + MOTHEDU

  # ------------------------------------
  # Variabel Laten Endogen
  # ------------------------------------
  Kemampuan_Ilmiah =~ SAAR.B1 + SAAR.B2 + SAAR.B3 + SAAR.B4 +
                      SAAR.B5 + SAAR.B6 + SAAR.B7 + SAAR.B8 + SAAR.B9

  # ------------------------------------
  # Hubungan Struktural
  # ------------------------------------
  Kemampuan_Ilmiah ~ Sikap_Belajar + Upaya_Pemaknaan + Status_Sosial_Ekonomi
'

# jalankan model SEM
fit_wlsmv <- sem(model,
                 data = data,
                 estimator = "WLSMV",
                 ordered = c("SAAR.B1","SAAR.B2","SAAR.B3","SAAR.B4","SAAR.B5",
                             "SAAR.B6","SAAR.B7","SAAR.B8","SAAR.B9",
                             "CLASS3","CLASS11","CLASS14","CLASS23","CLASS24",
                             "CLASS25","CLASS28","CLASS30","CLASS32","CLASS36",
                             "CLASS39","CLASS42"))
summary(fit_wlsmv, fit.measures = TRUE, standardized = TRUE)


library(semTools)

# hitung CRI
compRelSEM(fit_wlsmv)

# hitung AVE
AVE(fit_wlsmv)

