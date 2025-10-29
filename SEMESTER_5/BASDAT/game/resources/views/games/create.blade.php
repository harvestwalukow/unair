<!-- create.blade.php -->

@extends('layout')

@section('content')
<div class="max-w-lg mx-auto bg-white shadow-md rounded-lg p-6">
  <div class="mb-4">
    <h1 class="text-2xl font-bold">Tambah Game Baru</h1>
  </div>

  @if ($errors->any())
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Oops!</strong>
      <span class="block sm:inline">Terjadi beberapa masalah dengan input Anda.</span>
      <ul class="mt-3 list-disc list-inside text-sm">
          @foreach ($errors->all() as $error)
            <li>{{ $error }}</li>
          @endforeach
      </ul>
    </div>
  @endif

  <form method="post" action="{{ route('games.store') }}">
      @csrf
      <div class="mb-4">
          <label for="title_name" class="block text-gray-700 text-sm font-bold mb-2">Nama Game:</label>
          <input type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" name="title_name" value="{{ old('title_name') }}"/>
      </div>
      <div class="mb-6">
          <label for="harga" class="block text-gray-700 text-sm font-bold mb-2">Harga:</label>
          <input type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" name="harga" value="{{ old('harga') }}"/>
      </div>
      <div class="flex items-center justify-between">
        <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Tambah Game</button>
        <a href="{{ route('games.index') }}" class="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
          Batal
        </a>
      </div>
  </form>
</div>
@endsection