@extends('layout')
@section('title', 'Dashboard · CatDesk')
@section('content')
  <div class="split-heading">
    <div><p class="eyebrow">Your workspace</p><h1>Hello, {{ auth()->user()->display_name }}</h1></div>
    <a class="button secondary" href="{{ route('account.password') }}">Change password</a>
  </div>

  <section class="card">
    <h2>New note</h2>
    <form method="post" action="{{ route('notes.store') }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>Title<input name="title" required maxlength="120"></label>
      <label>Note<textarea name="body" rows="5" maxlength="5000"></textarea></label>
      <button type="submit">Save note</button>
    </form>
  </section>

  <section>
    <h2>Your notes</h2>
    <div class="note-grid">
      @forelse($notes as $note)
        <a class="note-card" href="{{ route('notes.edit', $note) }}">
          <h3>{{ $note->title }}</h3>
          <p>{{ str($note->body)->limit(180) }}</p>
        </a>
      @empty
        <p class="empty">No notes yet. Add your first one above.</p>
      @endforelse
    </div>
  </section>
@endsection
