<?php

namespace App\Http\Controllers;

use App\Models\Note;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class NoteController extends Controller
{
    public function store(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        $values = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['nullable', 'string', 'max:5000'],
        ]);

        $request->user()->notes()->create([
            'title' => $values['title'],
            'body' => $values['body'] ?? '',
        ]);

        return redirect()->route('dashboard')->with('status', 'Note created.');
    }

    public function edit(Request $request, Note $note): View
    {
        $this->ownedNote($request, $note);

        return view('notes.edit', ['note' => $note]);
    }

    public function update(Request $request, Note $note): RedirectResponse
    {
        $this->ownedNote($request, $note);
        $this->verifyFormToken($request);

        $values = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['nullable', 'string', 'max:5000'],
        ]);

        $note->update([
            'title' => $values['title'],
            'body' => $values['body'] ?? '',
        ]);

        return redirect()->route('notes.edit', $note)->with('status', 'Note updated.');
    }

    public function destroy(Request $request, Note $note): RedirectResponse
    {
        $this->ownedNote($request, $note);
        $this->verifyFormToken($request);
        $note->delete();

        return redirect()->route('dashboard')->with('status', 'Note deleted.');
    }

    private function ownedNote(Request $request, Note $note): void
    {
        abort_unless($note->user_id === $request->user()->id, 404);
    }
}
