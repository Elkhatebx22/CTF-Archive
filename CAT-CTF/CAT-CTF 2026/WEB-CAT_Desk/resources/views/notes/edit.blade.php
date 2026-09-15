@extends('layout')
@section('title', 'Edit note · CatDesk')
@section('content')
  <section class="card">
    <h1>Edit note</h1>
    <form method="post" action="{{ route('notes.update', $note) }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>Title<input name="title" required maxlength="120" value="{{ old('title', $note->title) }}"></label>
      <label>Note<textarea name="body" rows="10" maxlength="5000">{{ old('body', $note->body) }}</textarea></label>
      <button type="submit">Save changes</button>
    </form>
    <form class="danger-zone" method="post" action="{{ route('notes.destroy', $note) }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <button class="danger" type="submit">Delete note</button>
    </form>
  </section>
@endsection
