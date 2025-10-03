data_prak = read.table("data.txt", header = TRUE)

D1 = dist(data_prak, method = "euclidean", diag = TRUE, upper = FALSE)
D2 = dist(data_prak, method = "manhattan", diag = TRUE, upper = FALSE)
D3 = dist(data_prak, method = "minkowski", diag = TRUE, upper = FALSE)

D1
D2
D3

Klaster1 = hclust(D1, method = "single")
Klaster2 = hclust(D1, method = "complete")
Klaster3 = hclust(D1, method = "average")

plot(Klaster1)
plot(Klaster2)
plot(Klaster3)
