@extends('layouts.portfolio')

@section('title', 'Projects')

@section('content')
    <section class="hero">
        <h1>Projects Pilihan</h1>
        <p class="subline muted">Kunjungi <a href="https://harvestwalukow.github.io">harvestwalukow.github.io</a> untuk melihat project lainnya.</p>
    </section>
    <section class="section grid">
        <div class="card" onclick="window.location.href='https://tanya.beasiswamahaghora.com'">BMHG Chatbot</div>
        <div class="card" onclick="window.location.href='https://github.com/harvestwalukow/apple-music'">Apple Music Database</div>
    </section>
@endsection

