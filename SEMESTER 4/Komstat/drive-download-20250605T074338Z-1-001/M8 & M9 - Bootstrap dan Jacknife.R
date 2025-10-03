#bootstrap nonparametrik (tanpa asumsi distribusi)
#intinya buat tau apakah melenceng atau tidak estimator terhadap distribusi parameter populasi
#kaya misalnya kalo kita taro data yang mirip mirip apakah hasilnya akan konsisten
x = c(1:5)
x
n = length(x)
B = 10

x_star = NULL
for (i in 1:B){
  x_star = cbind(x_star, sample(x,n,replace = TRUE))
}
x_star

x_boot = matrix(0,1,B) #ini matriks elemennya isinya 0, 1 baris, dan kolom sejumlah B
for (i in 1:B){
  x_boot[,i] = mean(x_star[,i])
}
x_boot


#bootstrap parametrik (dengan asumsi distribusi rnorm)
n = 10
x = rnorm(n, mean = 0, sd = 1)
x_bar = mean(x)
var_x = var(x)
sd_x = sd(x)
B2 = 100
x_bar_boot = vector()
for (i in 1:B2){
  x_boot = sample(x,n, replace = TRUE)
  x_bar_boot[i] = mean(x_boot)
}

x_bar_boot

hist(x_bar_boot)
qqnorm(x_bar_boot)








#coba soal kating
x = c(5.7, 13.6, 6.0, 10.4, 2.9, 16.4, 7.3, 15.7, 18.2, 2.7, 8.1, 4.4, 5.1, 9.1, 8.9, 9.1, 14.3, 13.1, 14.6, 4.9)
x_sum = sum(x)
mean(x)
n = 20
xbar = x_sum/n
var_x = var(x)
sd_x = sd(x)
cv = sd_x/xbar

B5 = 100
cv_boot = vector()
for (i in 1:B5){
  x_boot = sample(x,n, replace = TRUE)
  cv_boot[i] = sd(x_boot)/mean(x_boot)
}

cv_boot
hist(cv_boot)

#hitung nilai estimasi cv
cv_est = mean(cv_boot)
cv_est

# menghitung interval kepercayaan 95% dari koefisien variasi bootstrap
lower_ci <- quantile(cv_boot, probs = 0.025)
upper_ci <- quantile(cv_boot, probs = 0.975)

cat("95% CI:", lower_ci, "<", cv_est, "<", upper_ci)

#Confidence Interval parametrik
#alpha = 95%
zscore = 1.96
n2 = 10
x_bar = mean(x_bar_boot)
var_boot = var(x_boot)
sigma_n = var_boot/sqrt(n2)

lower = x_bar-(zscore*sigma_n)
upper = x_bar+(zscore*sigma_n)
lower
upper

#bootstrap nonparametrik 2
x = sample(seq(1,3, by = 0.001), 20, replace = TRUE)
n = length(x)
x_bar = mean(x)
var_x = var(x)
sd_x = sd(x)
var_x_bar = var_x/n
sd_x_bar = sqrt(var_x_bar)
B = 100
x_bar_boot = vector()
for(i in 1:B){
  x_boot = sample(x, n, replace = TRUE)
  x_bar_boot[i] = mean(x_boot)
}

hist(x_bar_boot)
qqnorm(x_bar_boot)

#ci nonpar
x.est = mean(x_bar_boot)
x.se = sqrt(var(x_bar_boot)/n)
CI = qt(0.05/2,n-1, lower.tail = FALSE)*x.se
lower = x.est- CI
upper = x.est+CI
lower
upper


#==== Resampling Jackknife ====

#jackknife (buat tau apakah data kita ini "stable", goyang" ato engga ketika diresampling)
#intinya buat tau apakah estimator kita stabil ketika membuang satu data (menghilangkan sedikit data) pada data asli 
#analoginya kaya kalo misal kita buang satu orang, apakah hasil kerja dari suatu kelompok ini bakal tetep stabil apa engga
set.seed(123)
x = rnorm(100) #default, mean = 0, sd = 1
n = length(x)
partials = rep(0,n) #bikin data kosong menggunakan repetisi dari 1 sampai n berupa length data
for (i in 1:n){
  partials[i] = mean(x[-i])
} #bikin perulangan dimana mencari mean untuk masing masing resampling, dengan tiap resampling membuang satu data secara urut indeks

partials
pseudos = (n*mean(x)) - (n-1)*partials #sebagai perkiraan, nilai yang dihitung berbasis informasi yang tidak komplit, serta nilai ini digunakan untuk tujuan spesifik tapi ngga merefleksikan realitasnya
#pseudos ini buat koreksi bias untuk setiap resample dan jadi dasar estimasi jackknife nya
#rumus pseudo = n x mean(x) - (n-1) x mean dari tiap resamplenya (partials)
#pseudo values mempermudah perhitungan estimasi jackknife dan variansnya, serta merupakan bentuk perhitungan yang lebih efisien

#jackknife estimation
jack.est = mean(pseudos) #sehingga estimasinya pake pseudo values
#jackknife standard error
jack.se = sqrt(var(pseudos)/n) #rumus standard error
#standard error
jack.se
CI = qt(0.05/2,n-1, lower.tail = FALSE)*jack.se
lower = jack.est - CI
upper = jack.est + CI
lower
upper

#confidence interval jackknife
cat("95% CI:", lower, "<", jack.est, "<", upper)

#optional
jknife = function(x, fxn, ci = 0.95){
  theta = fxn(x)
  n = length(x)
  partials = rep(0,n)
  for (i in 1:n){
    partials[i] = fxn(x[-i])
  }
  pseudos = (n*theta)-(n-1)*partials
  jack.est = mean(pseudos)
  jack.se = sqrt(var(pseudos)/n)
  alpha = 1-ci
  CI = qt(alpha/2, n-1, lower.tail = FALSE)*jack.se
  jack.ci = c(jack.est-CI, jack.est + CI)
  list(est = jack.est, se = jack.se, ci = jack.ci, pseudos = pseudos, partials = partials)
}

jknife(x, mean, ci = 0.95)


#cara lain jackknife

set.seed(123)

# Data
data = rnorm(100)


# Banyaknya Iterasi (B)
B <- 1000

# Banyaknya Observasi (N)
N <- length(data)

# Inisialisasi Variabel Output
hasil <- vector("numeric", B)

# Loop Iterasi Jackknife
for (i in 1:B) {
  # Salinan data dengan menghilangkan satu observasi
  data_jack <- data[-i]
  
  # Hitung descriptive statistic (misalnya, mean)
  hasil[i] <- mean(data_jack)
}

# Rata-rata dan Confidence Interval
rata_rata <- mean(hasil)
lower_ci <- quantile(hasil, 0.025)
upper_ci <- quantile(hasil, 0.975)

# Print hasil
cat("Jackknife Estimation:\n")
cat("Mean:", rata_rata, "\n")
cat("95% Confidence Interval:", lower_ci, "-", upper_ci, "\n")
