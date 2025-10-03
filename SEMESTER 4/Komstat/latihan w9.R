# 1.
n = 1000
mean_x = 160
sd_x = 4

se = sd_x / sqrt(n)

z = qnorm(0.05 / 2, lower.tail = FALSE)
ci = z * se

lower = mean_x - ci
upper = mean_x + ci

se
lower
upper

# 2.
x = c(25, 10, 3, 2, 7, 20, 30, 9, 15)
n = length(x)
partial = rep(0, n)

for (i in 1:n) {
  partial[i] = mean(x[-i])
}

psedous = n * mean(x) - (n - 1) * partial

jack.est = mean(psedous)

jack.se = sqrt(var(psedous) / n)

ci = qt(0.05 / 2, n - 1, lower.tail = FALSE) * jack.se
lower = jack.est - ci
upper = jack.est + ci

jack.est #a
jack.se #c
lower
upper
bias = mean(x) - jack.est
bias

# 3.
x = c(98.5, 101.2, 99.0, 100.3, 97.8, 102.1, 98.9, 100.0, 99.7, 101.5)
n = length(x)
partial = rep(0, n)

for (i in 1:n) {
  partial[i] = mean(x[-i])
}

psedous = n * mean(x) - (n - 1) * partial

jack.est = mean(psedous)

jack.se = sqrt(var(psedous) / n)

ci = qt(0.05 / 2, n - 1, lower.tail = FALSE) * jack.se
lower = jack.est - ci
upper = jack.est + ci

jack.est #a
jack.se #b
lower #c
upper #c

