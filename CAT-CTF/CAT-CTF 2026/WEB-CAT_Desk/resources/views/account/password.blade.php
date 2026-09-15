@extends('layout')
@section('title', 'Change password · CatDesk')
@section('content')
  <section class="card narrow">
    <h1>Change password</h1>
    <p>Your other signed-in sessions will be closed.</p>
    <form method="post" action="{{ route('account.password.update') }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>New password<input type="password" name="new_password" required minlength="10" maxlength="200" autocomplete="new-password"></label>
      <button type="submit">Change password</button>
    </form>
  </section>
@endsection
