df <- data.frame(
  Asam_Askorbat = c(
    5.34, 5.38, 5.26, 5.47, 5.19, 5.5, 5.42, 5.47, 5.71, 5.62,
    7.12, 6.89, 6.93, 6.82, 7.06, 6.91, 6.88, 6.76, 6.97, 6.88,
    6.28, 6.01, 6.27, 6.15, 6.38, 6.4, 6.12, 6.24, 6.31, 6.37
  ),
  Varietas = c(
    rep("Varietas_A", 10),
    rep("Varietas_B", 10),
    rep("Varietas_C", 10)
  )
)

y1 = df$Asam_Askorbat
perlakuan = df$Varietas

summary(df)

# ANOVA
anova1 <- aov(y1 ~ perlakuan, data = df)
summary(anova1)

# p-value < 2e-16 (tolak H0)