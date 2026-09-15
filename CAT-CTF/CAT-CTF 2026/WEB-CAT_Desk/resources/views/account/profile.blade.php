@extends('layout')
@section('title', 'Profile · CatDesk')
@section('content')
  <section class="card narrow">
    <h1>Edit profile</h1>
    <form method="post" action="{{ route('account.profile.update') }}">
      <input type="hidden" name="form_token" value="{{ $form_token }}">
      <label>Display name<input name="display_name" required maxlength="80" value="{{ old('display_name', $user->display_name) }}"></label>
      <label>Bio<textarea name="bio" rows="6" maxlength="500">{{ old('bio', $user->bio) }}</textarea></label>
      <button type="submit">Save profile</button>
    </form>
  </section>
@endsection
