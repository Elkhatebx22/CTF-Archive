@extends('layout')
@section('title', 'Create account · CatDesk')
@section('content')
  <section class="card narrow">
    <h1>Create account</h1>
    <form method="post" action="{{ route('register') }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>Username<input name="username" required minlength="3" maxlength="40" value="{{ old('username') }}" autocomplete="username"></label>
      <label>Password<input type="password" name="password" required minlength="10" maxlength="200" autocomplete="new-password"></label>
      <button type="submit">Create account</button>
    </form>
  </section>
@endsection
