
library(sf)
library(sp)
library(dplyr)
library(readr)
library(GWmodel)
library(ggplot2)

data_eko <- read_csv("data_Lengkap.csv")
peta_provinsi <- st_read("gadm41_IDN_shp/gadm41_IDN_1.shp", quiet = TRUE)

data_eko$Provinsi_upper <- toupper(data_eko$Provinsi)
peta_provinsi$NAME_1_upper <- toupper(peta_provinsi$NAME_1)

peta_lengkap <- inner_join(peta_provinsi, data_eko, by = c("NAME_1_upper" = "Provinsi_upper"))

peta_bersih <- peta_lengkap %>%
  rename(Wisatawan_2023 = `2023`) %>%
  filter(!is.na(Wisatawan_2023) & !is.na(Mikro) & !is.na(Kecil) & !is.na(Datang))

data_sp <- as(peta_bersih, "Spatial")


cat("--- TAHAP 1: Menjalankan OLS untuk Variabel Global (Berangkat) ---\n")
model_global_ols <- lm(Wisatawan_2023 ~ Berangkat, data = data_sp@data)

coef_datang_global <- coef(model_global_ols)["Berangkat"]
cat("Koefisien Global untuk 'Berangkat' (dari OLS) adalah:", round(coef_datang_global, 4), "\n\n")

data_sp$residual_global <- residuals(model_global_ols)

formula_local_gwr <- residual_global ~ Mikro + Datang

cat("--- TAHAP 2: Mencari Bandwidth untuk Model GWR Lokal ---\n")
bw_local <- bw.gwr(formula = formula_local_gwr, data = data_sp,
                   adaptive = TRUE, approach = "CV")
cat("Bandwidth optimal untuk model lokal:", bw_local, "\n\n")

model_local_gwr <- gwr.basic(formula = formula_local_gwr, data = data_sp,
                             bw = bw_local, adaptive = TRUE, kernel = "gaussian")

cat("--- Hasil Model GWR Lokal (pada Residual) ---\n")
print(model_local_gwr)

