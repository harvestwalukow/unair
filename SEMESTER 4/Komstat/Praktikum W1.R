Data <- read.csv("M1-Data Praktikum.csv", sep = " ")

x=Data$Age
y=Data$Salary 

hist_age=hist(x)
hist_salary=hist(y)

hist_age1 <- hist(x, plot = FALSE) # Save first histogram data
hist_salary1 <- hist(y, plot = FALSE) # Save 2nd histogram data

plot(hist_age1, col=rgb(1,0,0,0.25), main=NULL, xlim=c(0,40)) # Plot 1st histogram using a transparent color
plot(hist_salary1, col=rgb(0,1,0,0.25), xlim=c(0,40), add = TRUE) # Add 2nd histogram using different color

plot(x, y, main="scatter plot", xlab="age", ylab="salary", pch=4)

boxplot(x, data=Data)
boxplot(y, data=Data)

plot(density(x))
plot(density(y))

cor(x, y, method = "pearson")
cor.test(x, y, method = "pearson")

linearMod <- lm(y ~ x, data=Data)
summary(linearMod)
