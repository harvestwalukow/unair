#create function for ols linear regression

## start with clean work-space
rm(list=ls())

## create artificial data set
#  set seed for reproducibility
set.seed(123)

#  height in cm
height <- rnorm(200,160,sd = 15) #dengan mean = 160 dan sd = 15
height

#  weight in kilogram (the relationship between height
#  and weight is completely random)
weight <- height-80+1.02*(height)^0.01*
  rnorm(200,0,sd = 15)*
  rnorm(200,1.1,sd = 0.2)
weight

#  join height and weight in data frame
df <- data.frame(height,weight)


## build OLS estimator as a function
# create function names OLS
#rumus OLS: (X'X)^-1(X'Y)
OLS <- function(X,y){
  y <- as.matrix(y) #define y vector
  X <- as.matrix(cbind(1,X)) #define X matrix
  beta <- solve(t(X)%*%X)%*%t(X)%*%y #coeficients beta
  res <- as.matrix(y-beta[1]-beta[2]*X[,2]) #residuals
  n <- nrow(df) #number of observations (n)
  k <- ncol(X) #number of parameters (k)
  
  #variance covariance (Var (beta topi)) = sigma^2(X'X)-1
  #var(beta topi) = 1/(n-k)*(e'e)*(X'X)-1, dimana e = residual/errornya
  #1/(n-k)* e'e * (x'x)^-1 (ini varians errornya)
  VCV <- 1/(n-k)*as.numeric(t(res)%*%res)*solve(t(X)%*%X) #Variance-Covariance matrix (VCV)
  se <- sqrt(diag(VCV)) #standard errors (diag itu dibuat matrix diagonal) dilakukan diagonal karena variansnya tiap parameter ada di diagonalnya
  #selain diagonalnya itu kovariansnya
  
  #cari p value pakai distribusi t
  #2*P(T>t) t = nilai statistik (abs beta/standar error)
  p_value <- rbind(2*pt(abs(beta[1]/se[1]),df=n-k, #p-values
                        lower.tail= FALSE),
                   2*pt(abs(beta[2]/se[2]),df=n-k,
                        lower.tail= FALSE))
  output <- as.data.frame(cbind(c("(Intercept)","height"),
                                beta,se,p_value))
  names(output) <- c("Coefficients:","Estimate",
                     "Std. Error","Pr(>|t|)")
  return(output)
}

#di luar fungsi coba satu satu
y = as.matrix(df$weight)
X = as.matrix(cbind(1, df$height))
X[,2]
beta = solve(t(X)%*%X)%*%t(X)%*%y
beta

res <- as.matrix(y-beta[1]-beta[2]*X[,2])
n <- nrow(df) #number of observations (n)
k <- ncol(X)

VCV <- 1/(n-k)*as.numeric(t(res)%*%res)*solve(t(X)%*%X) #Variance-Covariance matrix (VCV)
VCV
diag(VCV)
se <- sqrt(diag(VCV)) #standard errors
se
p_value <- rbind(2*pt(abs(beta[1]/se[1]),df=n-k, #p-values
                      lower.tail= FALSE),
                 2*pt(abs(beta[2]/se[2]),df=n-k,
                      lower.tail= FALSE))
p_value
output <- as.data.frame(cbind(c("(Intercept)","height"),
                              beta,se,p_value))
names(output) <- c("Coefficients:","Estimate",
                   "Std. Error","Pr(>|t|)")
output

## use R build-in OLS estimaor (lm())
reg <- lm(weight ~ height, data=df)
summary(reg)

## use our own function
OLS(y=df$weight,X=df$height)


#Implementasi fungsi manual dan bawaan r menggunakan dataset r



OLS2 <- function(X,y){
  y <- as.matrix(y) #define y vector
  X <- as.matrix(cbind(1,X)) #define X matrix
  beta <- solve(t(X)%*%X)%*%t(X)%*%y #coeficients beta
  res <- as.matrix(y-beta[1]-beta[2]*X[,2]) #residuals
  n <- nrow(df) #number of observations (n)
  k <- ncol(X) #number of parameters (k)
  
  #1/(n-k)* e'e * (x'x)^-1
  VCV <- 1/(n-k)*as.numeric(t(res)%*%res)*solve(t(X)%*%X) #Variance-Covariance matrix (VCV)
  se <- sqrt(diag(VCV)) #standard errors
  
  #cari p value pakai distribusi t
  #2*P(T>t) t = nilai statistik (abs beta/standar error)
  p_value <- rbind(2*pt(abs(beta[1]/se[1]),df=n-k, #p-values
                        lower.tail= FALSE),
                   2*pt(abs(beta[2]/se[2]),df=n-k,
                        lower.tail= FALSE))
  output <- as.data.frame(cbind(c("(Intercept)","mpg"),
                                beta,se,p_value))
  names(output) <- c("Coefficients:","Estimate",
                     "Std. Error","Pr(>|t|)")
  return(output)
}

#mtcars
data("mtcars")
?mtcars
mtcars


attach(mtcars)
OLS2(X = mtcars$cyl, y = mtcars$mpg)

#fungsi
reg2 = lm(mtcars$mpg ~ mtcars$cyl)
summary(reg2)


#belajar punya irfani
# Data
y <- c(2, 4, 5, 7, 8)
x <- c(1, 2, 3, 4, 5)

# Matriks desain X
X <- cbind(1, x)

# Estimasi koefisien beta
beta <- solve(t(X) %*% X) %*% t(X) %*% y

# Residuals
residuals <- y - X %*% beta

# Jumlah observasi (n) dan jumlah parameter (k)
n <- length(y)
k <- ncol(X)

# Sum of Squared Errors (SSE)
SSE <- sum(residuals^2)

# Mean Squared Error (MSE)
MSE <- SSE / (n - k)

# Variance-Covariance matrix (VCV)
VCV <- MSE * solve(t(X) %*% X)

# Standard error
SE <- sqrt(diag(VCV))

# t-value
t_value <- beta / SE

# p-value
p_value <- 2 * pt(abs(t_value), df = n - k, lower.tail = FALSE)

# Print hasil
output <- data.frame(
  "Coefficients" = c("(Intercept)", "x"),
  "Estimate" = beta,
  "Std. Error" = SE,
  "t value" = t_value,
  "P-value" = p_value
)

print(output)
