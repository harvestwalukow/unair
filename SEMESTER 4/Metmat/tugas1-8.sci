clc;
clear all;

// Contoh 8 (Secant)
// Diketahui
x(1) = 0.8;
x(2) = 0.9;
eps = 1 * 10^(-10);

// Menghitung fx(1) dan fx(2)
fx(1) = x(1)^2 - (x(1) + 1) * exp(-x(1));
fx(2) = x(2)^2 - (x(2) + 1) * exp(-x(2));

// Menghitung akar dari f(x)
for i = 2:1000
    x(i + 1) = x(i) - fx(i) * ((x(i) - x(i - 1)) / (fx(i) - fx(i - 1)));
    fx(i + 1) = x(i + 1)^2 - (x(i + 1) + 1) * exp(-x(i + 1));
    
    if abs(fx(i + 1)) < eps then
        root = x(i + 1);
        break;
    end
end

disp(root);





