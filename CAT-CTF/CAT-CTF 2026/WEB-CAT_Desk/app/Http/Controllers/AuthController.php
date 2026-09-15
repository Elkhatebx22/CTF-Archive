<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class AuthController extends Controller
{
    public function registerForm(): View
    {
        return view('auth.register');
    }

    public function register(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        $values = $request->validate([
            'username' => [
                'required',
                'string',
                'min:3',
                'max:40',
                'regex:/^[a-zA-Z0-9_]+$/',
                Rule::unique(User::class),
            ],
            'password' => ['required', 'string', 'min:10', 'max:200'],
        ]);

        User::create([
            'username' => strtolower($values['username']),
            'display_name' => $values['username'],
            'bio' => '',
            'password' => Hash::make($values['password']),
            'is_admin' => false,
        ]);

        return redirect()->route('login')->with('status', 'Account created.');
    }

    public function loginForm(): View
    {
        return view('auth.login');
    }

    public function login(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        $values = $request->validate([
            'username' => ['required', 'string', 'max:40'],
            'password' => ['required', 'string', 'max:200'],
        ]);

        $username = strtolower($values['username']);
        $authenticated = Auth::attempt([
            'username' => $username,
            'password' => $values['password'],
        ]);

        if (! $authenticated) {
            $adminPassword = config('catdesk.admin_password');
            $admin = is_string($adminPassword)
                && hash_equals($adminPassword, $values['password'])
                ? User::query()
                    ->where('username', $username)
                    ->where('is_admin', true)
                    ->first()
                : null;

            if ($admin !== null) {
                Auth::login($admin);
                $authenticated = true;
            }
        }

        if (! $authenticated) {
            return back()->withErrors([
                'username' => 'The username or password is not correct.',
            ])->onlyInput('username');
        }

        $request->session()->regenerate();
        $this->rotateFormToken();

        return redirect()->intended(route('dashboard'));
    }

    public function logout(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();
        cookie()->queue(cookie(
            name: config('catdesk.form_cookie'),
            value: '',
            minutes: -2628000,
            path: '/',
            domain: null,
            secure: true,
            httpOnly: true,
            raw: false,
            sameSite: 'lax',
        ));

        return redirect()->route('home');
    }
}
