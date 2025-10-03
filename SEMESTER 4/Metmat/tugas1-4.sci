clc;
clear all;

// Contoh 4 (Newton-raphson)
// Diketahui
x = 0;
eps = 1 * 10^(-10);

// Menghitung fx dan f' x
fx = x - exp(-x);
diff_fx = 1 + exp(-x);

// Menghitung akar dari f(x) = x - exp(-x)
while abs(fx) > eps
    x = x - (fx / diff_fx);
    fx = x - exp(-x);
    diff_fx = 1 + exp(-x);
end

disp(x);



