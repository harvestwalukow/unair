# install.packages("lavaan")
# install.packages("semTools")
# install.packages("lavaanPlot") # Pastikan ini terinstal
# Muat library
library(lavaan)
library(semTools)
library(lavaanPlot)
library(DiagrammeR)    
library(DiagrammeRsvg) 
library(rsvg)          
# Baca dataset
data <- read.csv("SPHERE dataset cleaned.csv")

# Definisikan model SEM sesuai header kamu
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

# Jalankan model SEM
fit_wlsmv <- sem(model,
                 data = data,
                 estimator = "WLSMV",
                 ordered = c("SAAR.B1","SAAR.B2","SAAR.B3","SAAR.B4","SAAR.B5",
                             "SAAR.B6","SAAR.B7","SAAR.B8","SAAR.B9",
                             "CLASS3","CLASS11","CLASS14","CLASS23","CLASS24",
                             "CLASS25","CLASS28","CLASS30","CLASS32","CLASS36",
                             "CLASS39","CLASS42"))
summary(fit_wlsmv, fit.measures = TRUE, standardized = TRUE)


# ------------------------------------
# Visualisasi Diagram Jalur SEM (dengan lavaanPlot)
# ------------------------------------

# 1. Buat objek plot
#    Opsi-opsi ini tetap sama untuk tampilan yang bersih
plot_obj <- lavaanPlot(model = fit_wlsmv,
                       node_options = list(shape = "box", fontname = "Helvetica"),
                       edge_options = list(color = "black"),
                       coefs = TRUE,       
                       stand = TRUE,      
                       stars = "regress",  
                       graph_options = list(layout = "dot", rankdir="LR")) 

export_graph(plot_obj,
             file_name = "diagram_sem_high_res.png",
             file_type = "png",
             width = 2000)

print(plot_obj)

