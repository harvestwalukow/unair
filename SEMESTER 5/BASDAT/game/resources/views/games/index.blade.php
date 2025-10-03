<!-- index.blade.php -->

@extends('layout')

@section('content')

<div class="bg-white shadow-md rounded-lg p-6">
  <div class="flex justify-between items-center mb-4">
    <h1 class="text-2xl font-bold">Daftar Game</h1>
    <a href="{{ route('games.create') }}" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      Tambah Game Baru
    </a>
  </div>

  <div class="mb-4">
    <form action="{{ route('games.index') }}" method="GET">
      <div class="flex">
        <input type="text" name="search" class="shadow appearance-none border rounded-l w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" placeholder="Cari berdasarkan nama atau harga..." value="{{ request('search') }}">
        <button type="submit" class="bg-gray-800 hover:bg-gray-900 text-white font-bold py-2 px-4 rounded-r">
          Cari
        </button>
      </div>
    </form>
  </div>

  @if(session()->get('success'))
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
      {{ session()->get('success') }}
    </div>
  @endif

  <table class="min-w-full bg-white">
    <thead class="bg-gray-800 text-white">
        <tr>
          <th class="w-1/12 text-left py-3 px-4 uppercase font-semibold text-sm">ID</th>
          <th class="w-5/12 text-left py-3 px-4 uppercase font-semibold text-sm">Nama Game</th>
          <th class="w-3/12 text-left py-3 px-4 uppercase font-semibold text-sm">Harga Game</th>
          <th class="w-3/12 text-center py-3 px-4 uppercase font-semibold text-sm">Aksi</th>
        </tr>
    </thead>
    <tbody class="text-gray-700">
        @foreach($games as $game)
        <tr class="border-b">
            <td class="text-left py-3 px-4">{{$game->id}}</td>
            <td class="text-left py-3 px-4">{{$game->title_name}}</td>
            <td class="text-left py-3 px-4">Rp {{ number_format($game->harga, 0, ',', '.') }}</td>
            <td class="text-center py-3 px-4">
              <div class="flex item-center justify-center">
                <a href="{{ route('games.edit', $game->id)}}" class="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded mr-2">Ubah</a>
                <form action="{{ route('games.destroy', $game->id)}}" method="post" onsubmit="return confirm('Apakah Anda yakin?');">
                  @csrf
                  @method('DELETE')
                  <button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" type="submit">Hapus</button>
                </form>
              </div>
            </td>
        </tr>
        @endforeach
    </tbody>
  </table>
  <div class="mt-4">
    {{ $games->appends(['search' => request('search')])->links() }}
  </div>
</div>
@endsection