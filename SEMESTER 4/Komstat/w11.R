# Menggunakan function
library(stats4)
library(MASS)

xpoisson <- rpois(n = 300, lambda = 2)

lpoisson = function(lambda)
{
  n = length(xpoisson)
  x = xpoisson
  for (i in 1:n) {
    lnlikeli = (n * lambda - sum(x) * log(lambda) + sum(log(factorial(x))))
  }
  return(lnlikeli)
}
estpoisson = mle(minuslogl = lpoisson, start = list(lambda=2))
summary(estpoisson)


# Tanpa function bawaan
set.seed(123)
x = rnorm(100)

x = x/sd(x) * 8
x = x-mean(x) + 10
c('mean' = mean(x), 'sd' = sd(x))

hist(x, freq = FALSE, col = 'tan')
lines(density(x), col = 'red', lwd = 2)

norm_lik = function(x, m, s) {
  1 / (sqrt(2 * pi) * s) * exp(-((x - m)^2) / (2 * s^2))
}

par(mar = c(4, 4, 2, 1))
plot(seq(-3, 3, .1), sapply(seq(-3, 3, .1), FUN=norm_lik, m=0, s=1), type = 'l', ylab = 'Density', xlab = 'x', main = 'Gaussian Normal')

llik = function(x.par) {
  m = par[1]
  s = par[2]
  n = length(x)
  ll = -(n/2) * (log(2*pi*s^2)) + (-1/(2*s^2)) * sum((x-m)^2)
  return(-ll) # krn mau minimize
}

# kurva ll
plot(seq(-3, 3, .1), sapply(seq(-3, 3, .1), FUN=llik, par=c(0,1)), type = 'l', ylab = '', xlab = '',)
