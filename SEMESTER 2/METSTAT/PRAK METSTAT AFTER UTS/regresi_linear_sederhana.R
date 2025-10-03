# Regresi Linear Sederhana

# Load Data
library(readr)
Salary_Data <- read_csv("D:/UNAIR/SEMESTER 2/METSTAT/PRAK METSTAT AFTER UTS/Salary Data.csv")
head(Salary_Data)

# Subset Data
x = Salary_Data$YearsExperience
y = Salary_Data$Salary

library(ggplot2)
ggplot(Salary_Data, aes(x, y)) + 
  geom_point() + 
  geom_smooth(method = "lm")

# Regresi Manual
slope <- function(x, y){
  mean_x <- mean(x)
  mean_y <- mean(y)
  sxy <- sum((x - mean_x) * (y - mean_y))
  sxx <- sum((x - mean_x) ^ 2)
  b1 <- sxy / sxx
  return(b1)
}

intercept <- function(x, y, b1){
  b0 <- mean(y) - (b1 * mean(x))
  return(b0)
}

print("b1")
slope(x, y)

print("b0")
intercept(x, y, slope(x, y))

# Regresi with Built-in
model = lm(y ~ x, data = Salary_Data)
summary(model)

model$coefficients

summary(model)$r.squared

resid(model)
