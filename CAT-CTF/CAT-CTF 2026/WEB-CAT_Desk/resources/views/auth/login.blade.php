@extends('layout')
@section('title', 'Sign in · CatDesk')
@section('content')
  <section class="card narrow">
    <h1>Sign in</h1>
    <form method="post" action="{{ route('login') }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>Username<input name="username" required maxlength="40" value="{{ old('username') }}" autocomplete="username"></label>
      <label>Password<input type="password" name="password" required maxlength="200" autocomplete="current-password"></label>
      <button type="submit">Sign in</button>
    </form>
  </section>
@endsection
