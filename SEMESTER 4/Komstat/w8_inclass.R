# bootstrap nonpar (tanpa asumsi distribusi)
x = c(1:5)
x
n = length(x)
B = 10

x_star = NULL
for (i in 1:8) {
  x_star = cbind(x_star, sample(x, n, replace = TRUE))
}
x_star

x_boot = matrix(0, 1, 8) 
for (i in 1:8) {
  x_boot[,i] = mean(x_star[,i])
}
x_boot


# bootstrap parametrik (dengan asumsi distribusi rnorm)
n = 10
x = rnorm(n, mean = 0, sd = 1)
x_bar = mean(x)
var_x = var(x)
sd_x = sd(x)
B2 = 100
x_bar_boot = vector()
for (i in 1:B2) {
  x_boot = sample(x, n, replace = TRUE)
  x_bar_boot[i] = mean(x_boot)
}

x_bar_boot

hist(x_bar_boot)
qqnorm(x_bar_boot)
