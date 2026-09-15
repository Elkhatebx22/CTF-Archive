@extends('layout')
@section('title', 'Forbidden · CatDesk')
@section('content')
  <section class="card narrow error-page">
    <p class="error-code">403</p>
    <h1>{{ $exception->getMessage() ?: 'Forbidden.' }}</h1>
    <a class="button" href="{{ route('home') }}">Return home</a>
  </section>
@endsection
