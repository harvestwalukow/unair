set.seed(123)
x = range(100)
n = length (x)
partial = rep(0,n)
for (i in 1:n) {
  partial[i] = mean(x[-1])
}

partial
psedous = (n*mean(x)) - (n-1)*partial

jack.est = mean(psedous)

jack.se = sqrt(var(psedous)/n)
ci = qt(0.05/2, n-1, lower.tail = FALSE)*jack.se

lower = jack.est - ci
upper = jack.est + ci

lower
upper


