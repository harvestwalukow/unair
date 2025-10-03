library(sf)
jatim <- st_read(file.choose())
data_sekolah <- read.csv(file.choose())


# Sesuaikan nama kolom
data_sekolah$Kabupaten.Kota <- toupper(data_sekolah$Kabupaten.Kota)

# Rename kolom di shapefile agar seragam
jatim$Kabupaten.Kota <- toupper(jatim$Kabupaten)

# Join data
jatim_joined <- merge(jatim, data_sekolah, by = "Kabupaten.Kota", all.x = TRUE)


library(dplyr)

jatim_joined <- jatim_joined %>%
  select(SD, SMP, SMA, PT)
