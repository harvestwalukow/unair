clc;
clear all;

// Contoh 2 (Bagi dua)
// Diketahui
x_bawah = -1;
x_atas = 0;
eps = 1 * 10^(-3);

// menghitung fx_bawah dan fx_atas
fx_bawah = x_bawah * exp(-x_bawah) + 1;
fx_atas = x_atas * exp(-x_atas) + 1;

// menghitung akar dari f(x) = x*exp(-x) + 1
if fx_atas * fx_bawah < 0 then
    while abs(x_atas - x_bawah) > eps
        x_mid = (x_bawah + x_atas) / 2;
        fx_mid = x_mid * exp(-x_mid) + 1;
        if fx_mid * fx_bawah < 0 then
            x_atas = x_mid;
        else
            x_bawah = x_mid;
        end
    end
    x_mid = (x_atas + x_bawah) / 2;
    disp(x_mid);
end


