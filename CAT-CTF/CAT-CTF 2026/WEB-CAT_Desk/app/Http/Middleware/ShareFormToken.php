<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\View;
use Symfony\Component\HttpFoundation\Response;

class ShareFormToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $name = config('catdesk.form_cookie');
        $formToken = $request->cookie($name);

        if (! is_string($formToken) || $formToken === '') {
            $formToken = bin2hex(random_bytes(32));
            cookie()->queue(cookie(
                name: $name,
                value: $formToken,
                minutes: config('catdesk.form_lifetime'),
                path: '/',
                domain: null,
                secure: true,
                httpOnly: true,
                raw: false,
                sameSite: 'lax',
            ));
        }

        $request->attributes->set('form_token', $formToken);
        View::share('form_token', $formToken);

        return $next($request);
    }
}
