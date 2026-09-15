<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class RequestGate
{
    public function handle(Request $request, Closure $next): Response
    {
        if (
            $request->isMethod('POST')
            && $request->header('Sec-Fetch-User') !== '?1'
        ) {
            abort(403, 'Forbidden');
        }

        return $next($request);
    }
}
