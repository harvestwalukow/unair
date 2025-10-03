// Contoh 7 (Newton-raphson)
// Diketahui
x = input("Masukkan nilai awal x: ");
eps = 1 * 10^(-10);

// Menghitung fx dan f'x
fx = x * exp(-x) + cos(2 * x);
diff_fx = exp(-x) - x * exp(-x) - 2 * sin(2 * x);

// Menghitung akar dari f(x) = x*exp(-x) + cos(2x)
while abs(fx) > eps
    x = x - (fx / diff_fx);
    fx = x * exp(-x) + cos(2 * x);
    diff_fx = exp(-x) - x * exp(-x) - 2 * sin(2 * x);
end

disp(x);




