#Univariate
set.seed(123) # for consistency set the seed explicitly.
#first simulate some normal data with expected mean of 0 and sd of 1
x = rnorm(100)
# scale the data the way that we would like
x = x/sd(x) * 8 # sd of 8
x = x-mean(x) + 10 # mean of 10
c('mean'=mean(x),'sd'=sd(x)) # double check

# histogram (in the fashion of SPSS)
hist(x, freq=FALSE,col='tan')
lines(density(x),col='red',lwd=2)

#Since these data are drawn from a Normal distribution,
#we will use the Gaussian Normal distribution function for fitting

# specify the single value normal probability function
norm_lik = function(x, m, s){
  y = 1/sqrt(2*pi*s^2)*exp((-1/(2*s^2))*(x-m)^2) #pdf dist. normal
}
# and plot it just to make sure
plot(seq(-3,3,.1),sapply(seq(-3,3,.1),FUN=norm_lik,m=0,s=1),type='l',
     ylab='',xlab='', main='Gaussian Normal')
#m = mean, s = std. deviasi

#create a likelihood function for normal distribution
llik = function(x,par){
  m=par[1]
  s=par[2]
  n=length(x)
  # log of the normal likelihood
  # -n/2 * log(2*pi*s^2) + (-1/(2*s^2)) * sum((x-m)^2)
  ll = -(n/2)*(log(2*pi*s^2)) + (-1/(2*s^2)) * sum((x-m)^2) #log likelihoodnya
  # return the negative to maximize rather than minimize
  return(-ll) #ini direturn negatif buat ngebalikin tanda log likelihoodnya (negative loglike)
}

# log likelihood curve
plot(seq(-3,3,.1),-1*sapply(seq(-3,3,.1),FUN=llik,par=c(0,1)),type='l',
     ylab='',xlab='')
#puncak kurva sama dengan titik maksimum kurva loglikelihood

# negative log likelihood curve
# just to see what the funciton produces we can plot it.
plot(seq(-3,3,.1),sapply(seq(-3,3,.1),FUN=llik,par=c(0,1)),type='l',
     ylab='',xlab='')
#puncak kurva sama dengan titik minimum kurva loglikelihood

# call optim with the starting values 'par',
# the function (here 'llik'),
# and the observations 'x'
res0 = optim(par=c(.5,.5), llik, x=x) #par c itu parameter yang diinginkan (0.5 itu mengira ngira aja)
#optim mencari nilai parameter par yang meminimalkan negative log-likelihood

library(knitr)
print(kable(
  cbind('direct'=c('mean'=mean(x),'sd'=sd(x)),
        'optim'=res0$par),digits=3))

#direct adalah nilai asli
#selisih mean dari direct sama optim itu bias





#Bivariate example (regression) #least square (cari error terus dikuadratkan)
# our totally made up data
MomEd = c(0, 1, 3, 4) #mom's education
CGPA = c(3.0, 3.2, 3.3, 3.7) #children's GPA
# fit a linear model
coef(lm(CGPA ~ MomEd)->lm0)

# sum of squares function
SS_min = function(data,par){
  b0=par[1]
  b1=par[2]
  loss = with(data, sum((b0+b1*x - y)^2)) #ini least square sum e^2 = sum (y-beta0-betax)^2
  return(loss)
} #penggunaan with untuk copy data jadi memodifikasi data asli tapi dicopy dulu
#ini kita mengestimasi parameter model linier (beta0 dan beta1) lewat meminimalkan sum of squares (Least Square)
#ini metode least square

# data on mom's ed and Children GPA from above
dat=data.frame(x=MomEd,y=CGPA)
# min resid sum of squares
res1a = optim(par=c(.5,.5),SS_min, data=dat) #par c itu parameter yang diinginkan (0.5 itu mengira ngira aja) kalo ga diketahui gapapa ngira aja 0.5. Untuk initial value bebas
#mencari nilai parameter yang meminimalkan error
#dimana 0.5 pertama adalah penduga awal untuk beta0 dan 0.5 kedua adalah penduga awal untuk beta1

library(knitr)
# direct comparison
print(kable(cbind('lm()'=coef(lm0),'SS_min'=res1a$par),digits=4)) #untuk beta 1 gaada bias karena gaada selisih, kalo yang beta0 ada bias karena ada selisihnya

# slope effect
b1 = .85
# simulated data
x = 1:60
dat = data.frame(x=x,y=(x*b1)+rnorm(60))
# from the lm() function
lm1 = lm(y~x, data=dat)
lm1

# different start values
res1 = optim(par=c(.01,1),SS_min, data=dat)
res1$par

op=par(mfrow=c(1,2),mar=c(3,3,3,1),pty='s')
# scatterplot
with(dat,plot(x,y,col='grey60',main='lm() results'))
# regression line from lm()
abline(lm1,lwd=2)
with(dat,plot(x,y,col='grey60',main='optim() results'))
# from the Min SS
abline(res1$par[1],res1$par[2],col='red',lty=1,lwd=2)


#estimasi parameter distribusi poisson
set.seed(123)
#first simulate some normal data with expected mean of 0 and sd of 1
x2 = rpois(100, 20)

# histogram (in the fashion of SPSS)
hist(x2, freq=FALSE,col='tan')
lines(density(x2),col='red',lwd=2)

pmf_pois = function(x, lambda) {
  y = exp(lambda) * 1 / factorial(x) * lambda ^ x
  return(y)
}

plot(seq(0, 20, 1), 
     sapply(seq(0, 20, 1), 
            FUN = pmf_pois,
            lambda = 4),
     type='l',
     main='PMF Poisson lambda 4')


llik = function(x, par) {
  lambda = par[1]
  n = length(x)
  ll = -n * lambda - sum(log(factorial(x))) + log(lambda) * sum(x)
  return(-ll)
}

res0 = optim(par=c(0.5), llik, x=x2)
res0$par


# Distribusi Bernouli
# generate data
set.seed(123)
library(Rlab)
x <- rbern(100, 0.5)

# likelihood function
bernoulli_lik <- function(x, p) {
  prod(p^x * (1 - p)^(1 - x))
}

# negative log-likelihood function
bernoulli_nllik <- function(x, p) {
  -sum(log(bernoulli_lik(x, p)))
}

# estimate parameter
res_bernoulli <- optimize(f = bernoulli_nllik, interval = c(0, 1), x = x)
#perbedaan mencolok antara estimasi dengan "optim" dan "optimize" adalah "optim" lebih cocok untuk lebih dari 1 parameter
#"optimize" cocok untuk yang parameter hanya 1
#penggunaan "optim" bisa juga untuk satu parameter (contohnya di poisson). "optimize" harus menuliskan intervalnya untuk mencari nilai probabilitas minimum berdasarkan interval yang kita tuliskan
#penggunaan "optimze" memang untuk mencari nilai minimum log likelihood dari interval yang kita tuliskan

# print result
print(paste0("MLE estimate for Bernoulli distribution: ", res_bernoulli$minimum))
#diambil negatif karena kita mencari negative log-likelihood, jadi mencari nilai minimumnya



#Distribusi Binomial
# generate data
set.seed(123)
x <- rbinom(100, 10, 0.5)

# likelihood function
binomial_lik <- function(x, n, p) {
  prod(choose(n, x) * p^x * (1 - p)^(n - x))
}

# negative log-likelihood function
binomial_nllik <- function(x, n, p) {
  -sum(log(binomial_lik(x, n, p)))
}

# estimate parameter
res_binomial <- optim(par = c(0.3), binomial_nllik, x = x, n = 10)

# print result
print(paste0("MLE estimate for Binomial distribution: ", res_binomial$par))


#Distribusi Exponensial
# generate data
set.seed(123)
x <- rexp(120, 5)

# likelihood function
exponential_lik <- function(x, lambda) {
  prod(lambda * exp(-lambda * x))
}

# negative log-likelihood function
exponential_nllik <- function(x, lambda) {
  -sum(log(exponential_lik(x, lambda)))
}

# estimate parameter
res_exponential <- optim(par = 0.5, exponential_nllik, x = x)

# print result
print(paste0("MLE estimate for Exponential distribution: ", res_exponential$par))


# Distribusi Gamma
# generate data
set.seed(123)
x <- rgamma(50, 1, 2)

# likelihood function
gamma_lik <- function(x, shape, rate) {
  prod(dgamma(x, shape, rate))
}

# negative log-likelihood function
gamma_nllik <- function(x, shape, rate) {
  -sum(log(gamma_lik(x, shape, rate)))
}

# estimate parameter
res_gamma <- optim(par = c(0.5, 0.5), gamma_nllik, x = x, shape = 5)

# print result
print(paste0("MLE estimate for Gamma distribution: ", res_gamma$par))

#pareto
set.seed(123)
library(Pareto)
x <- rPareto(50, 2, 1)

pmfpareto <-function(x, t, alpha){
  pem = alpha * t^alpha
  pen = x^(alpha+1)
  return(pem/pen)
}

#likelihood
logpareto <- function(x,par){
  t <- par[1]
  alpha <- par[2]
  logpare = sum(log(pmfpareto(x,t,alpha)))
  return(-logpare)
}

respar <- optim(par = c(5, 5), logpareto, x = x)
respar$par


#Gamma
set.seed(123)
x=rgamma(50,2,1)

#gamma_lik = function(x,a,b){
#  y = ((b^a)/(gamma(a)))*x^(a-1)*exp(-b*x)
#  return(y)
#}

llik = function(x,par){
  n = length(x)
  a = par[1]
  b= par[2]
  z = sum(x)
  ll =  (n*(-a*log(b)-log(gamma(a))))+(a - 1)* sum(log(x))-(1/b)*sum(x)
  return(-ll)
}

resgamma = optim(par=c(0.5,0.5),llik,x=x)
resgamma$par

