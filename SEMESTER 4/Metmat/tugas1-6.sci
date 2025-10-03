clc;
clear all;

// Contoh 6 (Newton-raphson)
// Diketahui
x = -1;
eps = 1 * 10^(-10);

// Menghitung fx dan f'x
fx = exp(x) - 5 * x^2;
diff_fx = exp(x) - 10 * x;

// Menghitung akar dari f(x) = exp(x) - 5x^2
while abs(fx) > eps
    x = x - (fx / diff_fx);
    fx = exp(x) - 5 * x^2;
    diff_fx = exp(x) - 10 * x;
end

disp(x);




