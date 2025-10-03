#contoh 1
x <- 2
.y <- 3
z <- x+.y
z

#contoh 2
A <- c(TRUE, FALSE) #c is combine
class(A)

A <- c(1.5, 2.4, 3.3)
class(A)

A <- c(3L, 4L, 40L)
class(A)

A <- c(3+2i, 2i)
class(A)

A <- c('a', 'hello', '1.35')
class(A)

#Contoh 3 (alternatif)
Data <- data.frame(
  Age = c(25, 32, 41, 29, 37, 45, 22, 39, 28, 34),
  Salary = c(50000, 65000, 80000, 55000, 70000, 90000, 40000, 75000, 60000, 68000)
)

#contoh 4
x=Data$Age
y=Data$Salary

summary(x)
summary(y)

mean(x)
mean(y)

max(x)
max(y)

summary(Data)

#Contoh 5
hist_age=hist(x)
hist_salary=hist(y)

hist_age1 <- hist(x, plot = FALSE)
hist_salary1 <- hist(y, plot = FALSE)
plot(hist_age1, col=rgb(1,0,0,0.25), main=NULL, xlim=c(0,40))
plot(hist_salary1, col=rgb(0,1,0,0.25), xlim=c(0,40), add = TRUE)

#Contoh 6
plot(x, y, main="scatter plot", xlab="age", ylab="salary", pch=19)

#Contoh 7
boxplot(x, data=Data)
boxplot(y, data=Data)

#Contoh 8
plot(density(x))
plot(density(y))

#Contoh 9
cor(x, y, method = "pearson")
cor.test(x, y, method = "pearson")

#Contoh 10
linearMod <- lm(y ~ x, data=Data)
summary(linearMod)