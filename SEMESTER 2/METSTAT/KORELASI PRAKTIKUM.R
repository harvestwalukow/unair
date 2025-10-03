# NOMOR 1
a <- c(250, 50, 300)
b <- c(200, 1000, 1200)
c <- c(450, 1050, 1500)

matrik <- cbind(a, b, c)
dimnames(matrik) <- list(Jenis_Bacaan = c("Fiction", "Non-Fiction", "Total"), Jenis_Kelamin = c("Male", "Female", "Total"))
matrik

Uji1_a=chisq.test(matrik,correct=TRUE)
Uji1_a

Uji1_a$observed

Uji1_a$expected

# NOMOR 2
x <- c(2,1,5,0)
y <- c(5,3,6,2)
data_pearson <- cbind(x, y)
dimnames(data_pearson) = list(c("1", "2", "3", "4"), c("x", "y"))

data_pearson

Uji2=cor.test(x, y, alternative = "two.sided", method = "pearson", conf.level = 0.90)
Uji2

# NOMOR 3
data_praktikum_3 <- data.frame(
  kedisiplinanX = c(75, 45, 44, 70, 75, 64, 80, 77, 92, 66),
  kinerjaY = c(80, 45, 34, 80, 70, 65, 79, 76, 89, 72)
)

data_praktikum_3

x=data_praktikum_3$`kedisiplinanX`
y=data_praktikum_3$`kinerjaY`

Uji3=cor.test(x,y,alternative="two.sided", method = "spearman", exact = FALSE, conf.level = 0.95)
Uji3

# NOMOR 4
x = data.praktikum.4$pewawancara_1
y = data.praktikum.4$pewawancara_2
Uji4=cor.test(x,y,alternative = "two.sided", method = "kendall", exact = FALSE, conf.level = 0.95)
Uji4