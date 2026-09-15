<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', 'CatDesk')</title>
    <link rel="stylesheet" href="/app.css">
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="{{ route('home') }}">CatDesk</a>
      <nav>
        @auth
          <a href="{{ route('dashboard') }}">Dashboard</a>
          <a href="{{ route('account.profile') }}">Profile</a>
          @if(auth()->user()->is_admin)<a href="{{ route('admin') }}">Admin</a>@endif
          <form class="inline" method="post" action="{{ route('logout') }}">
            <input type="hidden" name="form_token" value="{{ $form_token }}">
            <button class="link-button" type="submit">Sign out</button>
          </form>
        @else
          <a href="{{ route('login') }}">Sign in</a>
          <a href="{{ route('register') }}">Create account</a>
        @endauth
      </nav>
    </header>

    <main class="page">
      @if(session('status'))<div class="flash success">{{ session('status') }}</div>@endif
      @if($errors->any())
        <div class="flash error">
          @foreach($errors->all() as $error)<div>{{ $error }}</div>@endforeach
        </div>
      @endif
      @yield('content')
    </main>
  </body>
</html>
