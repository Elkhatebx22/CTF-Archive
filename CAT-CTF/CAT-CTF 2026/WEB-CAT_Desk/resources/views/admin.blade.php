@extends('layout')
@section('title', 'Admin · CatDesk')
@section('content')
  <section class="admin-banner">
    <p class="eyebrow">Administrator only</p>
    <h1>Operations dashboard</h1>
    <p>{{ $adminMessage }}</p>
    <a class="button" href="{{ route('admin.flag') }}">View flag</a>
  </section>
  <section class="card table-wrap">
    <h2>Accounts</h2>
    <table>
      <thead><tr><th>ID</th><th>Username</th><th>Display name</th><th>Created</th></tr></thead>
      <tbody>
        @foreach($users as $user)
          <tr><td>{{ $user->id }}</td><td>{{ $user->username }}</td><td>{{ $user->display_name }}</td><td>{{ $user->created_at }}</td></tr>
        @endforeach
      </tbody>
    </table>
  </section>
@endsection
