<?php

namespace App\Http\Controllers;

use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\View\View;

class AccountController extends Controller
{
    public function profile(Request $request): View
    {
        return view('account.profile', ['user' => $request->user()]);
    }

    public function updateProfile(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        $values = $request->validate([
            'display_name' => ['required', 'string', 'max:80'],
            'bio' => ['nullable', 'string', 'max:500'],
        ]);

        $request->user()->update([
            'display_name' => $values['display_name'],
            'bio' => $values['bio'] ?? '',
        ]);

        return redirect()->route('account.profile')->with('status', 'Profile updated.');
    }

    public function passwordForm(): View
    {
        return view('account.password');
    }

    public function updatePassword(Request $request): RedirectResponse
    {
        $this->verifyFormToken($request);

        $values = $request->validate([
            'new_password' => ['required', 'string', 'min:10', 'max:200'],
        ]);

        $request->user()->update([
            'password' => Hash::make($values['new_password']),
        ]);

        if (config('session.driver') === 'database') {
            DB::table(config('session.table', 'sessions'))
                ->where('user_id', $request->user()->id)
                ->where('id', '!=', $request->session()->getId())
                ->delete();
        }

        return redirect()->route('dashboard')->with('status', 'Password changed.');
    }
}
