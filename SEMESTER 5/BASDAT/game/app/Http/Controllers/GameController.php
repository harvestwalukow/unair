<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Game;

class GameController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->input('search');

        $games = Game::query()
            ->when($search, function ($query, $search) {
                return $query->where('title_name', 'like', "%{$search}%")
                             ->orWhere('harga', 'like', "%{$search}%");
            })
            ->paginate(10); // Menggunakan paginasi untuk data yang banyak

        return view('games.index', compact('games'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        return view('games.create');
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'title_name'=>'required',
            'harga'=> 'required|numeric'
        ]);
        $game = new Game([
            'title_name' => $request->get('title_name'),
            'harga' => $request->get('harga')
        ]);
        $game->save();
        return redirect('/games')->with('success', 'Game berhasil ditambahkan');
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        // Not used for this tutorial
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
    {
        $game = Game::find($id);
        return view('games.edit', compact('game'));
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $request->validate([
            'title_name'=>'required',
            'harga'=> 'required|numeric'
        ]);

        $game = Game::find($id);
        $game->title_name = $request->get('title_name');
        $game->harga = $request->get('harga');
        $game->save();

        return redirect('/games')->with('success', 'Game berhasil diperbarui');
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        $game = Game::find($id);
        $game->delete();

        return redirect('/games')->with('success', 'Game berhasil dihapus');
    }
}
