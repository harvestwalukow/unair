def is_prime(x):
    if x == 2:
        return True
    for i in range (2,x):
        if x % i == 0:
            return False
    return True

n = int(input())
prima = []

i = 2
while len(prima) < n:
    if is_prime(i) == True:
        prima.append(i)
    i+=1

print(prima) 