library(BSDA)

#uji Z 1 populasi #jika jumlah n > 30
#h0: miu <= miu0
#h1: miu > miu0
#right tail
zsum.test(mean.x = 1200000, sigma.x = 600000, n.x = 100,
          alternative = "greater", mu = 0,
          conf.level = 0.95) #H0: <=, H1: > (greater)



#pvalue
xbar = 1200000
miu = 0
n = 100
s = 600000

z = (xbar - miu)/(s/sqrt(n))

#right tail
pvalue = pnorm(z, lower.tail = FALSE)
pvalue2 = 1-pnorm(z) #sama kaya pvalue atas ini
#twotail
pvalue3 = 2*pvalue
#pvalue4 = 2*pvalue2
pvalue
pvalue3
#left tail
pnorm(z, lower.tail = TRUE)

#left tail
#h0: miu >= miu0
#h1: miu < miu0
zsum.test(mean.x = 1200000, sigma.x = 600000, n.x = 100,
          alternative = "less", mu = 0,
          conf.level = 0.95) #H0: <=, H1: > (greater)


#uji t 1 populasi #jika jumlah sampel n < 30
#H0: miu = miu0
#H1: miu != miu0
tsum.test(mean.x = 25, s.x = 6.4, n.x = 20, 
          alternative = "two.sided", mu = 0,
          var.equal = TRUE, conf.level = 0.95)

IR64=c(4.5,4.8,4,3.6,3.8,5,4,3.9,4.8)
MSP=c(6.4,6.5,4.2,4,5.8,5.9,6.2,3.8,2.5,3.6,7,8)

t.test(MSP, alternative = "two.sided")
tsum.test(mean.x = mean(MSP), s.x = sd(MSP), n.x = length(MSP),
          alternative = "two.sided", mu = 0,
          var.equal = TRUE, conf.level = 0.95)

#uji 2 populasi independen/tak berpasangan
#H0: miu1-miu2 = 0
#H1: miu1-miu2 != 0
t.test(x = IR64, y = MSP, alternative = "two.sided",
       paired = FALSE, var.equal = TRUE,
       conf.level = 0.95)

#uji t berpasangan
Orang.ke=seq(1:10)
BB.Sebelum=c(57,69,56,67,55,56,62,67,67,56)
BB.Sesudah=c(55,70,56,65,54,55,64,65,67,54)
data=data.frame(Orang.ke,BB.Sebelum,BB.Sesudah)

#H0: miu1-miu2 <= 0
#H1: miu1-miu2 > 0
t.test(x = data$BB.Sebelum, y = data$BB.Sesudah, alternative = "greater",
       mu = 0, paired = TRUE, var.equal = TRUE,
       conf.level = 0.95)
