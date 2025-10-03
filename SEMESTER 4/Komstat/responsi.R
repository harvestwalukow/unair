set.seed(10)

rayleigh_inverse_cdf <- function(n, sigma=1) {
  u <- runif(n)
  x <- sigma * sqrt(-2 * log(1-u))
  return(x)
}

samples <- rayleigh_inverse_cdf(10000, sigma=1)

hist(samples, breaks=50, probability=TRUE, col=rgb(0, 0, 1, 0.6), main="Rayleigh Distribution - Random Samples", xlab="x", ylab="Density")

x <- seq(0, 5, length.out=100)
pdf <- (x / 1^2) * exp(-x^2 / (2 * 1^2))
lines(x, pdf, col="red", lwd=2)
legend("topright", legend=c("Rayleigh PDF"), col="red", lwd=2)
