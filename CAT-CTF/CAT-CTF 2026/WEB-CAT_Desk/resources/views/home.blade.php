@extends('layout')
@section('title', 'CatDesk · Team notes')
@section('content')
  <section class="hero">
    <p class="eyebrow">A calm place for busy teams</p>
    <h1>Keep small notes from becoming lost work.</h1>
    <p>CatDesk gives every team member a private notebook, profile, and account dashboard.</p>
    @auth
      <a class="button" href="{{ route('dashboard') }}">Open dashboard</a>
    @else
      <a class="button" href="{{ route('register') }}">Create an account</a>
    @endauth
  </section>
  <section class="feature-grid">
    <article><h2>Private notes</h2><p>Create, edit, and remove notes from one place.</p></article>
    <article><h2>Simple profiles</h2><p>Keep a display name and short team bio.</p></article>
    <article><h2>Account control</h2><p>Change your password from the signed-in dashboard.</p></article>
  </section>
@endsection
