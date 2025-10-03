<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/beranda', function () {
    return view('beranda');
});

Route::get('/prestasi', function () {
    return view('prestasi');
});

Route::get('/hobi', function () {
    return view('hobi');
});

Route::get('/pendidikan', function () {
    return view('pendidikan');
});

Route::get('/kontak', function () {
    return view('kontak');
});

