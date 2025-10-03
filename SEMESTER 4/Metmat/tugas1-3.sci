clc;
clear all;

// Contoh 3 (Regula falsi)
// Diketahui
a = -1;
b = 0;
eps = 1 * 10^(-3);

// Menghitung fa, fb, x, dan fx
fa = a * exp(-a) + 1;
fb = b * exp(-b) + 1;
x = b - ((b - a) * fb) / (fb - fa);
fx = x * exp(-x) + 1;

// Menghitung akar dari f(x) = x * exp(-x) + 1
while abs(fx) > eps
    if fx * fa < 0 then
        b = x;
        fb = b * exp(-b) + 1;
    else
        a = x;
        fa = a * exp(-a) + 1;
    end

    x = b - ((b - a) * fb) / (fb - fa);
    fx = x * exp(-x) + 1;
end

disp(x);


