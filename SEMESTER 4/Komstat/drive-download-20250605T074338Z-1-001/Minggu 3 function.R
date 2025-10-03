data("mtcars") #memanggil data di R
?mtcars #mengetahui tentang data mtcars
head(mtcars) #mengecek 6 observasi awal
tail(mtcars) #mengecek 6 observari akhir
str(mtcars) #mengetahui struktur data

#===menghitung mean===

attach(mtcars) #untuk selalu menyertakan seluruh dataset pada tiap command


sum(wt)/nrow(mtcars) #menghitung manual nilai mean
mean(wt) #menghitung mean dengan fungsi


#jika tanpa menggunakan fungsi attach
sum(mtcars$wt)/nrow(mtcars) #menghitung manual nilai mean
mean(mtcars$wt) #menghitung mean dengan fungsi

#menghitung mean dengan function sendiri
getmean = function(x) {
  n = length(x)
  xbar = 0
  for (i in c(1:n)) {
    xbar = xbar + ((x[i]/n)) 
  }
  xbar
}
getmean(wt)


# x pada function(x) itu vektornya
#n itu banyaknya/panjangnya data x
#xbar 0 karena matriks ditambah 0 pasti tetep matriks (ini xbar nanti buat nampung hasil yang ada)
#pake for karena ingin mau mengulang perhitungan sampai n


#menghitung median
df <- sort(mtcars$wt) #mengurutkan data 1 variabel secara parsial
head(df) #melihat 6 observasi awal
n <- length(df) #menghitung banyaknya observasi
p <- 0.5 #persentil 50%
np <- n*p
#karena hasil np integer, sehingga median ada di observasi ke-16 dan 17
x16 <- df[16] #mengambil data ke-16
x17 <- df[17] #mengambil data ke-17
median <- (x16+x17)/2 #menghitung median dengan manual
median
median <- median(wt) #menghitung median dengan fungsi median()
median
median <- quantile(wt,0.5) #menghitung median dengan fungsi quantile()
median

#menghitung modus
table(cyl) #tabel frekuensi setiap level variabel cyl
l=length(levels(factor(cyl))) #mencari banyak level
modus <- names(sort(table(cyl))[l]) #mengurutkan frekuensi, mencari level terakhir
modus

sort(table(cyl)) #mengetahui secara spesifik isi dari sort table(cyl)
factor(cyl)
levels(factor(cyl))

#menggunakan fungsi sendiri
getmode <- function(x) {
  uniqx <- unique(x)
  uniqx[which.max(tabulate(match(x, uniqx)))]
}
mode <- getmode(cyl)
print(mode)

#unique ini ngehitung data duplicate jadi 1

uniqx = unique(cyl)
tabulate(match(cyl, uniqx)) #ambil frekuensi dari nilai unique masing-masing data
which.max(tabulate(match(cyl, uniqx))) #mengeluarkan indeksnya
uniqx[which.max(tabulate(match(cyl, uniqx)))]

#menghitung ukuran penyebaran 
variansi <- var(wt)
variansi
dev_standar <- sqrt(variansi)
dev_standar
sd(wt) #autonya bisa pakai sd untuk deviasi standar
range <- max(wt)-min(wt)
range
range <- range(wt)[2]-range(wt)[1]
range
iqr <- IQR(wt)
iqr

#fungsi summary() di R
attach(mtcars)
allstdes <- summary(mtcars)
allstdes
wtcyl_stdes <- allstdes[,c(2,6)] #mengambil cyl di kolom 2 dan wt di kolom 6
wtcyl_stdes

#fungsi stat.desc() dari paket pastecs di R
install.packages("pastecs") #install package dulu jika belum ter-install di R
library(pastecs) #memanggil library pastecs
stat.desc(mtcars)
stat.desc(mtcars[,c(2,6)]) #mengambil cyl di kolom 2 dan wt di kolom 6

#paket tidyverse di R
library(tidyverse) #tidyverse mendukung pipeline
mtcars %>%
  group_by(cyl) %>%
  summarise(Mean=mean(cyl), Median=median(cyl), St.Dev=sd(cyl))

#korelasi
korelasi = cor(mtcars$wt, mtcars$mpg)

#qplotnya
qplot(mpg, wt, data = mtcars, colour = I("green")) #I itu cuma mau ngewarna bukan ngasi keterangan


qplot(mpg, wt, data = mtcars, colour = "green") #jika tidak menggunakan I






#membuat fungsi sort dengan bubblesort
sortnya = function(x) {
  n = length(x)
  for (i in 1:(n-1)) {
    for (j in 1:(n-i)) {
      if (x[j] > x[j+1]) {
        temp = x[j]
        x[j] = x[j+1]
        x[j+1] = temp
      }
    }
  }
  return(x)
}
print(mtcars$wt)
sortnya(mtcars$wt)


#bisa pake sorting ini (ini yang ada di PPT)
getsort = function(x){
  input = x
  n = length(x)
  # looping
  for(i in 1:(n-1)){
    for(j in (i+1):n){
      temp1 = x[i] # temporary
      temp2 = x[j] # temporary
      if(temp1 > temp2){
        x[i] = temp2 # proses penukaran
        x[j] = temp1 # proses penukaran
      }
    }
  }
  hasil = list(`Data asli` = input, `Hasil terurut` = x) # menulis hasilnya
  return(hasil) # print output
}
getsort(wt)

#fungsi menghitung min, max, dan range
getrange <- function(x){
  sortt = getsort(x)
  n = length(x)
  u = sortt$`Hasil terurut`
  min = u[1]
  maks = u[n]
  {
    summary=list(minimum = min, maksimum = maks, range = maks-min)
    a = cbind(summary)
    return(summary)
  }
}
getrange(wt)

class(getrange(wt))
getrange(wt)["minimum", "summary"]

#fungsi menghitung mean
getmean <- function(x) {
  n <- length(x)
  xbar <- 0
  for (i in 1:n)
  {
    xbar <- xbar + (x[i]/n)
  }
  xbar
}
getmean(wt)

#fungsi menghitung median
getmedian = function(x){
  sortt = getsort(x)
  n = length(x)
  u = sortt$`Hasil terurut`
  k = n*0.5
  if (n%%2==0)
  {
    median = (u[k]+u[k+1])/2
  }
  else
  {
    median=u[ceiling(k)]
  }
  median
}
getmedian(wt)

#fungsi menghitung modus
getmodus<- function(x) {
  uniq <- unique(x)
  tab <- tabulate(match(x, uniq))
  if (length(uniq) == length(x))
  {
    modus <- NA
  }
  else
  {
    modus <- uniq[tab == max(tab)]
  }
  return(modus)
}
getmodus(cyl)

#fungsi menghitung variansi dan standar deviasi
getvarsd <- function(x){
  n = length(x)
  dev = 0
  for (i in 1:n)
  {
    dev = dev + (x[i]-mean(x))^2
  }
  varians = dev/(n-1)
  stdev = sqrt(varians)
  spread = list(Variansi = varians, `Standar Deviasi` = stdev)
  return(spread)
}
getvarsd(wt)



# no 1 fungsi summary jadi satu pake fungsi diatasnya
getstatdesc = function(x) {
  nilai_minmax = getrange(x)
  nilaisdvar = getvarsd(x)
  summary = list(min = nilai_minmax$minimum, max = nilai_minmax$maksimum, range = nilai_minmax$range, mean = getmean(x), median = getmedian(x), mode = getmodus(x), 
                 var = nilaisdvar$Varians, std = nilaisdvar$`Standar Deviasi`)
  cbind(summary)
  
}

getstatdesc(wt)

data("swiss")

head(swiss)
?swiss

attach(swiss)
getstatdesc(Fertility)

?tabulate

# Membuat vektor numerik
v <- c(2, 1, 3, 1)

# Menghitung frekuensi kemunculan setiap nilai dalam vektor
tabulate(v)
tabulate(Examination)
head(swiss)
swiss$Examination
tabulate(c(2,3,3,5,1))


# get range asprak
getrange <- function(x){
  n = length(x)
  u = sort(x)
  min = u[1] # ambil nilai minimum
    maks = u[n] # ambil nilai maksimum
    {
      summary=list(minimum = min, maksimum = maks, range = (maks-min)) # lengkapi baris ini
      cbind(summary)
    }
}
getrange(wt)


#korelasi pearson
corr_pearson = function(x,y){
  cornya = sum((x-getmean(x))*(y-getmean2(y)))/sqrt((sum((x-getmean(x))^2))*(sum((y-getmean2(y))^2))) #memasukkan rumus korelasi pearson dengan menggunakan fungsi yang telah dibuat
  return(cornya) #return variabel berisi rumusnya
}

var(wt)
