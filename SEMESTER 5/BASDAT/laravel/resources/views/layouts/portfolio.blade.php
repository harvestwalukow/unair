<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>@yield('title', 'Portfolio')</title>
    <link rel="stylesheet" href="/css/portfolio.css" />
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div><strong>👋 </strong></div>
            <div class="nav-right">
                <a href="{{ route('tentang') }}">Tentang</a>
                <a href="{{ route('projects') }}">Projects</a>
                <a href="{{ route('blog') }}">Blog</a>
                <a href="{{ route('kontak') }}">Kontak</a>
            </div>
        </nav>

        @yield('content')

        <div class="footer"></div>
    </div>
</body>
</html>


