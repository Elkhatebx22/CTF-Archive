<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpKernel\Exception\HttpException;

abstract class Controller
{
    protected function verifyFormToken(Request $request): void
    {
        $cookieToken = $request->cookie(config('catdesk.form_cookie'));
        $bodyToken = $request->request->get('form_token');

        if ($cookieToken !== $bodyToken) {
            throw new HttpException(403, 'Invalid form token.');
        }
    }

    protected function rotateFormToken(): string
    {
        $token = bin2hex(random_bytes(32));

        cookie()->queue(cookie(
            name: config('catdesk.form_cookie'),
            value: $token,
            minutes: config('catdesk.form_lifetime'),
            path: '/',
            domain: null,
            secure: true,
            httpOnly: true,
            raw: false,
            sameSite: 'lax',
        ));

        return $token;
    }
}
