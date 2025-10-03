---
title: "Praktikum Komstat W5"
author: "Harvest Walukow"
date: "2025-03-14"
output: pdf_document
editor_options: 
  markdown: 
    wrap: 72
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
set.seed(100)
```

## 1. ITM untuk Variabel Acak Diskrit

```{r}
pmf <- c(0.2, 0.15, 0.2, 0.35, 0.1)
x_values <- c(-2, -1, 0, 1, 2)
cdf <- cumsum(pmf)

simulate_discrete <- function(n) {
  u <- runif(n)
  x_sim <- sapply(u, function(ui) x_values[min(which(cdf >= ui))])
  return(x_sim)
}

sim_data <- simulate_discrete(100)
hist_data <- hist(sim_data, breaks=seq(-2.5,2.5,1), main="Histogram - Distribusi Diskrit", col="lightblue", xlab="x", probability=TRUE)

points(x_values, pmf, col="red", type="b", pch=19, lwd=2) # bandingkan dgn pmf
```

## 2. Distribusi Bernoulli

```{r}
simulate_bernoulli <- function(n, p) {
  u <- runif(n)
  return(ifelse(u < p, 1, 0))
}

bernoulli_data <- simulate_bernoulli(100, 0.5)
bernoulli_rbinom <- rbinom(100, 1, 0.5)

par(mfrow=c(1,2))
hist(bernoulli_data, main="ITM Bernoulli", col="lightgreen", xlab="x", breaks=2)
hist(bernoulli_rbinom, main="rbinom Bernoulli", col="lightcoral", xlab="x", breaks=2)
```

## 3. Distribusi Geometrik

```{r}
simulate_geometric <- function(n, p) {
  u <- runif(n)
  return(ceiling(log(1 - u) / log(1 - p)) - 1)
}

geom_data <- simulate_geometric(100, 0.6)
geom_rgeom <- rgeom(100, 0.6)

par(mfrow=c(1,2))
hist(geom_data, main="ITM Geometrik", col="lightblue", xlab="x")
hist(geom_rgeom, main="rgeom Geometrik", col="lightpink", xlab="x")
```
