<?php

return [
    'form_cookie' => env('FORM_COOKIE', '__Host-cat_form'),
    'form_lifetime' => (int) env('FORM_LIFETIME', 480),
    'admin_username' => env('ADMIN_USERNAME', 'admin'),
    'admin_password' => env('ADMIN_PASSWORD'),
    'flag' => env('FLAG'),
    'admin_message' => env(
        'ADMIN_MESSAGE',
        'Welcome to the private CatDesk operations dashboard.'
    ),
];
