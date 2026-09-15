<?php

use App\Http\Middleware\RequestGate;
use App\Http\Middleware\ShareFormToken;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Foundation\Http\Middleware\ValidateCsrfToken;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->encryptCookies(except: ['__Host-cat_form']);

        $middleware->web(
            append: [ShareFormToken::class, RequestGate::class],
            remove: [ValidateCsrfToken::class],
        );
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
