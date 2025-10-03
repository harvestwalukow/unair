clc;
clear all;

// Contoh 1 (Tabel)
// Diketahui
N = 10;
x_bawah = -1;
x_atas = 0;
h = (x_atas - x_bawah) / N;

// Menghitung x
for i = 1:N-1
    x(i) = x_bawah + i * h;
end

// Menghitung akar dari f(x) = x + exp(x)
for i = 1:N-1
    fx(i) = x(i) + exp(x(i));
    fx(i+1) = x(i+1) + exp(x(i+1)); 
    if fx(i) * fx(i+1) < 0 then
        if abs(fx(i)) < abs(fx(i+1)) then
            root = x(i);
            disp(root);
        else
            root = x(i+1);
            disp(root);
        end
    end
end


